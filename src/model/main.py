import spotipy
import spotipy.util as util


scope = 'user-library-read playlist-modify-public playlist-modify-private'
username = 'dean.lalap'
playlist = 'spotify:playlist:7yBrFRm2xPvRpe8PM81Os0'

Token = util.prompt_for_user_token(
    username,
    scope
)

print("TOKEN: {}".format(Token))

sp = spotipy.Spotify(auth=Token)
print(sp.current_user_saved_tracks().keys())

while True:
    searchTerms = input("Enter your search term: ")

    try:
        results = sp.search(searchTerms, limit=1)
        # results_song_and_artist = [ (r['name'], r['artists'][0]['name']) 
        #                             for r in results['tracks']['items']]
        
        # for key, value in results['tracks'].items():
        #     print(value)

        # for result in results_song_and_artist:
        #     print(result)
        # print('\n')

        song = results['tracks']['items'][0]['uri']
        sp.user_playlist_add_tracks(username, playlist, [song])
    except IndexError:
        print("No results.")