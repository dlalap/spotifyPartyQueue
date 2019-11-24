import spotipy as spotipy
import spotipy.util as util


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
                        user-read-currently-playing'
        else:
            self.scope = scope

        if playlist is None:
            self.playlist = 'spotify:playlist:7yBrFRm2xPvRpe8PM81Os0'
        else:
            self.playlist = playlist

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
            searchTerms = input('Search a song, artist, or playlist from Spotify: ')

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

    def removeCurrentSongFromQueue(self):
        currentTrack = self.getCurrentTrack()
        if currentTrack is None:
            return

        print("Removing {} by {}.".format(currentTrack[1], currentTrack[2]))
        self.client.user_playlist_remove_all_occurrences_of_tracks(
            self.username,
            self.playlist,
            [currentTrack[0]]
        )

    def singleQuery(self, query=None):
        try:
            if query is not None:
                results = self.sp.search(query, limit=1)
                song = results['tracks']['items'][0]['uri']
                songName = results['tracks']['items'][0]['name']
                songArtist = results['tracks']['items'][0]['artists'][0]['name']
                # print("Adding {} by {} to playlist.".format(
                #     songName, songArtist
                #     ))
                returnMessage = ("Adding {} by {} to playlist.".format(
                    songName, songArtist
                    ))
                self.sp.user_playlist_add_tracks(
                    self.username, self.playlist, [song]
                )
                return returnMessage
            else:
                pass
        except IndexError:
            print("No results.")
        except spotipy.SpotifyException:
            print("Session expired. Re-authenticating.")
            self.authenticate()