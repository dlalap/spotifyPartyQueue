import spotipy as spotipy
import spotipy.util as util
from threading import Timer


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

    def isCurrentPlaybackQueueList(self):
        currentPlayback = self.client.current_playback()
        if currentPlayback is None:
            return None
        playbackContext = currentPlayback['context']
        if playbackContext is None:
            return False
        if playbackContext['type'] != 'playlist':
            return False

        return self.playlist[8:] in playbackContext['uri']

    def getCurrentTrack(self):
        currentPlayback = self.client.current_playback()
        if currentPlayback is None:
            return None
        if currentPlayback['item'] is None:
            return None
        
        songName = currentPlayback['item']['name']
        songArtist = currentPlayback['item']['artists'][0]['name']
        return [currentPlayback['item']['uri'], songName, songArtist]

    def monitorForCurrentSongOnQueue(self):
        try:
            currentPlayback = self.client.current_playback()
            if currentPlayback is not None:
                is_playing = currentPlayback.get('is_playing', False)
                if not is_playing:
                    self.client.start_playback()
                currentTrack = self.getCurrentTrack()
                currentPlaybackIsInQueue = self.isCurrentPlaybackQueueList()

                if currentTrack is not None and currentPlaybackIsInQueue:
                    print(
                        f'REMOVING {currentTrack} FROM PLAYLIST.'
                    )
                    self.removeCurrentSongFromQueue()
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

    def singleQuery(self, query=None):
        try:
            if query is not None:
                results = self.sp.search(query, limit=1)
                firstResult = results['tracks']['items'][0]
                song = firstResult['uri']
                songName = firstResult['name']
                songArtist = firstResult['artists'][0]['name']
                # print("Adding {} by {} to playlist.".format(
                #     songName, songArtist
                #     ))
                returnMessage = (
                    f"Adding {songName} by {songArtist} to playlist."
                )
                self.sp.user_playlist_add_tracks(
                    self.username, self.playlist, [song]
                )
                return firstResult
            else:
                pass
        except IndexError:
            print("No results.")
        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating.")
            self.authenticate()
