#%% Import libraries 
import sys

sys.path.insert(0, "C:\\Users\\deanl\\source\\repos\\spotifyPartyQueue\\src\\spotenv\\bin\\activate")
sys.path.insert(0, "C:\\Users\\deanl\\source\\repos\\spotifyPartyQueue\\src\\.env")
import spotipy as spotipy
import spotipy.util as util
from threading import Timer

#%% Start Interactive
print('hello')
#%%
class Spot(object):
    def __init__(self, username=None, scope=None, playlist=None):
        if username is None:
            self.username = 'dean.lalap'
        else:
            self.username = username

        if scope is None:
            self.scope = 'user-library-read \
                        playlist-modify-public \
                        playlist-modify-private \
                        user-read-playback-state \
                        streaming \
                        user-read-currently-playing'
        else:
            self.scope = scope

        if playlist is None:
            self.playlist = 'spotify:playlist:7yBrFRm2xPvRpe8PM81Os0'
        else:
            self.playlist = playlist
        self.songMonitorActive = False
        self.timerActive = False
        self.playlistContent = []
        self.pause_timer_length = 10.0
        self.t = Timer(self.pause_timer_length, self.monitorForCurrentSongOnQueue)
        self.authenticate()
        self.syncLocalPlaylist()

    def authenticate(self):
        self.token = util.prompt_for_user_token(
            self.username,
            self.scope
        )

        self.sp = spotipy.Spotify(auth=self.token)
        self.client = spotipy.client.Spotify(auth=self.token)

    def startService(self):
        while True:
            searchTerms = input(
                'Search a song, artist, or playlist from Spotify: '
            )

            try:
                results = self.sp.search(searchTerms, limit=1)
                song = results['tracks']['items'][0]['uri']

                self.sp.user_playlist_add_tracks(
                                self.username, self.playlist, [song])

            except IndexError:
                print("No results.")

            except spotipy.SpotifyException:
                print("Session expired. Re-authenticating...")
                self.authenticate()

    def get_current_playback(self):
        try:
            return self.client.currently_playing()
        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating...")
            self.authenticate()
            return self.get_current_playback()

    def get_queue_playlist(self):
        try:
            return self.client.playlist(self.playlist)
        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating...")
            self.authenticate()
            return self.get_queue_playlist()
    
    def get_first_item_in_playlist(self):
        playlist = self.get_queue_playlist()
    
        if 'tracks' not in playlist: raise Exception("PLAYLIST DOES NOT HAVE TRACKS")
        if 'items' not in playlist['tracks']: raise Exception("TRACKS DOES NOT HAVE ITEMS")

        if len(playlist['tracks']['items']) < 1:
            return -1
        else:
            print(f'playlist.tracks.items[0] = {playlist["tracks"]["items"][0]}')
            return playlist['tracks']['items'][0]

    def isCurrentSongInQueueList(self):
        current_song = self.getCurrentTrack()
        if current_song is None:
            return False

        print(f'current_song[0] in self.playlistContent: {current_song[0] in self.playlistContent}')
        return current_song[0] in self.playlistContent

    def isCurrentPlaybackQueueList(self):
        currentPlayback = self.get_current_playback()
        if currentPlayback is None:
            return None
        playbackContext = currentPlayback['context']
        if playbackContext is None:
            return False
        if playbackContext['type'] != 'playlist':
            return False
        
        # print(f'current playback: {currentPlayback}')
        # print(f'Target playlist: {self.playlist}')
        # print(f'Current playlist: {playbackContext["uri"]}')
        # print(f'self.playlist in playbackContext["uri"]: {self.playlist in playbackContext["uri"]}')
        return self.playlist in playbackContext['uri']

    def getCurrentTrack(self):
        currentPlayback = self.get_current_playback()
        if currentPlayback is None:
            return None
        if currentPlayback['item'] is None:
            return None
        
        songName = currentPlayback['item']['name']
        songArtist = currentPlayback['item']['artists'][0]['name']
        return [currentPlayback['item']['uri'], songName, songArtist]

    def isPlaying(self, track):
        """
            Checks if a track is playing or not.
                Current timestamp equaling the max timestamp
                institutes as 'not playing.'
        """
        if track.get('is_playing', False):
            if track['item'] is None:
                return False
            return not self.trackIsDone(track)
        return False

    def trackIsDone(self, track):
        if track['item'] is None:
            return True
        current_timestamp = track['progress_ms']
        max_timestamp = track['item']['duration_ms']
        return current_timestamp >= max_timestamp

    def resumeFromQueuePlaylist(self, track):
        if not self.isCurrentPlaybackQueueList():
            self.client.start_playback(context_uri=self.playlist)
        elif self.trackIsDone(track):
            return
        elif not self.isPlaying(track):
            self.client.start_playback()
        self.removeSongFromQueue(track)

    def monitorForCurrentSongOnQueue(self):
        try:
            currentPlayback = self.get_current_playback()
            
            # If the song is selected,
            #   If we're currently playing from the playbackQueue list:
            #       If song selected is not playing:
            #           Start playback from the playbackQueue.
            #       Remove from the queue.
            #   Else (we assume song playing is not from the playbackQueue list)
            #       Start playback from the playbackQueue
            if currentPlayback is None:
                self.client.start_playback(context_uri=self.playlist)
                
            else:
                self.resumeFromQueuePlaylist(currentPlayback)
                # if self.isCurrentPlaybackQueueList():
                #     if not self.isPlaying(currentPlayback):
                #         self.client.start_playback(context_uri=self.playlist)
                #     self.removeSongFromQueue(currentPlayback)
                # else:    
                #     self.client.start_playback(context_uri=self.playlist)

            # else:
            #     print("No current playback.")
            self.restartMonitor()

        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating.")
            self.authenticate()
            self.restartMonitor()

        except Exception as e:
            print(f"Encountered error: {e}")

    def restartMonitor(self):
        if self.songMonitorActive:
            self.t = Timer(self.pause_timer_length, self.monitorForCurrentSongOnQueue)
            self.t.start()

    def setPauseTimer(self, new_pause_length):
        self.pause_timer_length = new_pause_length
        if self.songMonitorActive:
            self.t.cancel()
            self.restartMonitor()

    def getPauseTimer(self):
        return self.pause_timer_length

    def toggleSongMonitor(self):
        try:
            self.songMonitorActive = not self.songMonitorActive
            print(
                f'self.songMonitorActive is now {self.songMonitorActive}.'
            )
            if self.songMonitorActive:
                self.monitorForCurrentSongOnQueue()
            else:
                self.t.cancel()
            return self.songMonitorActive

        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating.")
            self.authenticate()

    def removeSongFromQueue(self, track):

        track_url = track["item"]["uri"]

        print(f'track_url = {track_url}')
        print(f'self.playlistContent = {self.playlistContent}')
        if track_url not in self.playlistContent:
            print(f'track {track_url} not found in self.playlistContent: {self.playlistContent}')
            return None

        self.client.user_playlist_remove_all_occurrences_of_tracks(
            self.username,
            self.playlist,
            [track_url]
        )

        while track_url in self.playlistContent:
            self.playlistContent.remove(track_url)

    def NextSong(self):
        try:
            self.client.next_track()
        except spotipy.SpotifyException as se:
            self.authenticate()
            self.client.next_track()

    def SayHi(self):
        print('Hello!')
        if self.timerActive:
            self.t = Timer(2.0, self.SayHi)
            self.t.start()

    def ToggleTimer(self):
        self.timerActive = not self.timerActive
        print(
            f'self.timerActive is now {self.timerActive}.'
        )
        if self.timerActive:
            self.SayHi()
        else:
            self.t.cancel()

    def getFirstResult(self, results):
        return results['tracks']['items'][0]

    def getSongData(self, result):
        uri = result['uri']
        songName = result['name']
        songArtist = result['artists'][0]['name']
        message = (
                f'Adding {songName} by {songArtist} to playlist.'
                )
        return message

    def reportSongAddedToPlaylist(self, queryResult):
        song = queryResult['uri']
        songName = queryResult['name']
        firstArtist = queryResult['artists'][0]['name']
        message = (
                f'Adding {songName} by {firstArtist} to playlist.'
                )
        return message

    def addSongsToPlaylist(self, songs):
        try:
            self.sp.user_playlist_add_tracks(
                    self.username, self.playlist, [songs]
                    )
            self.playlistContent.append(songs)
        except spotipy.SpotifyException as se:
            self.authenticate()
            self.addSongsToPlaylist(songs)

    def syncLocalPlaylist(self):
        # Check playlist for current songs
        # Synchronize self.playlistContent with current list
        playlist = self.get_queue_playlist()
        playlist_uri_list = [p['track']['uri'] for p in playlist['tracks']['items']]
        self.playlistContent = playlist_uri_list

    def callQuery(self, query, numResults=1):
        """
        Takes song query and returns results.
        If numResults is 1, runs an "I'm feeling lucky" type search
            where the first result is added to the playlist.
        """
        try:
            if numResults < 1:
                raise Exception(f"Invalid numResults: {numResults}")

            if numResults == 1:
                return self.singleQuery(query)

            else:
                return self.multiQuery(query, limit=numResults)

        except IndexError:
            print("No results.")
        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating.")
            self.authenticate()

    def singleQuery(self, query):
        """
        'I'm feeling lucky' style search query.
            Adds first result to the playlist.
        """
        try:
            results = self.sp.search(query, limit=1)
            firstResult = self.getFirstResult(results)
            song = firstResult['uri']
            returnMessage = self.reportSongAddedToPlaylist(firstResult)
            self.addSongsToPlaylist(song)
            return firstResult
        except spotipy.SpotifyException as se:
            self.authenticate()
            return self.singleQuery(query)

    def multiQuery(self, query, limit):
        """
        Lists results up to number defined by limit.
        Result list sent to user so user can choose based on list.
        """
        try:
            results = self.sp.search(query, limit)
            resultLists = results['tracks']['items']
            return resultLists
        except spotipy.SpotifyException as se:
            self.authenticate()
            return self.multiQuery(query, limit)

    def listAllArtistsInResult(self, result):
        """
        Lists all artists within a result.
        """
        artistList = [a['name'] for a in result['artists']]
        artistList = ', '.join(artistList)
        return artistList

    def listSongNameAndArtists(self, resultList, initIndex=0):
        """
        Lists the song name and artists associated in all results in list.
        """
        stringToReturn = ''        
        for r in range(len(resultList)):
            stringToReturn += f"{r + initIndex + 1}) {resultList[r]['name']} by {self.listAllArtistsInResult(resultList[r])}\n"

        return stringToReturn