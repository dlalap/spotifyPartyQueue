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
        self.t = Timer(10.0, self.monitorForCurrentSongOnQueue)
        self.authenticate()

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

        playlist = self.get_queue_playlist()
        playlist_uri_list = [p['track']['uri'] for p in playlist['tracks']['items']]
        print(f'current_song[0] in playlist_uri_list: {current_song[0] in playlist_uri_list}')

        print(f'current_song[0] = {current_song[0]}')
        print(f'playlist_uri_list = {playlist_uri_list}')
        return current_song[0] in playlist_uri_list

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
        # print(f'Target playlist: {self.playlist[8:]}')
        # print(f'Current playlist: {playbackContext["uri"]}')
        return self.playlist[8:] in playbackContext['uri']

    def getCurrentTrack(self):
        currentPlayback = self.get_current_playback()
        if currentPlayback is None:
            return None
        if currentPlayback['item'] is None:
            return None
        
        songName = currentPlayback['item']['name']
        songArtist = currentPlayback['item']['artists'][0]['name']
        return [currentPlayback['item']['uri'], songName, songArtist]

    def monitorForCurrentSongOnQueue(self):
        try:
            currentPlayback = self.get_current_playback()
                
            if currentPlayback is not None:
                if self.isCurrentPlaybackQueueList():
                    is_playing = self.isPlaying(currentPlayback)
                    if not is_playing:
                        # firstTrack = self.get_first_item_in_playlist()
                        self.client.start_playback(context_uri=self.playlist)
                    self.removeTrackIfPlaying()
                else:    
                    self.client.start_playback(context_uri=self.playlist)

            else:
                print("No current playback.")
            if self.songMonitorActive:
                self.t = Timer(10.0, self.monitorForCurrentSongOnQueue)
                self.t.start()
        except Exception as e:
            print(f"Encountered error: {e}")

        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating.")
            self.authenticate()

    def isPlaying(self, current_playback):
        if current_playback.get('is_playing', False):
            if current_playback['item'] is None:
                return False
            current_timestamp = current_playback['progress_ms']
            max_timestamp = current_playback['item']['duration_ms']
            return current_timestamp < max_timestamp
        return False

    def removeTrackIfPlaying(self):
        currentTrack = self.getCurrentTrack()
        currentPlaybackIsInQueue = self.isCurrentSongInQueueList()

        if currentTrack is not None and currentPlaybackIsInQueue:
            print(
                f'REMOVING {currentTrack} FROM PLAYLIST.'
            )
            self.removeCurrentSongFromQueue()

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

    def removeCurrentSongFromQueue(self):
        currentTrack = self.getCurrentTrack()
        if currentTrack is None:
            return
        # if current track is still in playlist:
        # print("Removing {} by {}.".format(currentTrack[1], currentTrack[2]))

        self.client.user_playlist_remove_all_occurrences_of_tracks(
            self.username,
            self.playlist,
            [currentTrack[0]]
        )

    def NextSong(self):
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
        self.sp.user_playlist_add_tracks(
                self.username, self.playlist, [songs]
                )

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
        results = self.sp.search(query, limit=1)
        firstResult = self.getFirstResult(results)
        song = firstResult['uri']
        returnMessage = self.reportSongAddedToPlaylist(firstResult)
        self.addSongsToPlaylist(song)
        #songName = firstResult['name']
        #songArtist = firstResult['artists'][0]['name']
        #returnMessage = (
        #    f"Adding {songName} by {songArtist} to playlist."
        #)
        #self.sp.user_playlist_add_tracks(
        #    self.username, self.playlist, [song]
        #)
        return firstResult
 
    def multiQuery(self, query, limit):
        """
        Lists results up to number defined by limit.
        Result list sent to user so user can choose based on list.
        """
        results = self.sp.search(query, limit)
        resultLists = results['tracks']['items']
        return resultLists

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