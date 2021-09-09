# Spotify Queuer

The idea is for everyone at a party to add to a playlist through SMS.

## Things to note:
Spotipy library obtained via this command line:

`pip install git+https://github.com/plamere/spotipy.git --upgrade`

## Things to run
Run main Flask program
`python3 main.py`

Run ngrok to expose port to the world and Twilio can redirect SMS body content
`ngrok http 1812`

Turn on auto-removal timer to remove currently playing (and duplicate) tracks
`https://#####.ngrok.io/monitor` 

## Commands
`$NEXT` to skip the currently playing track
User can text any spotify query and Twilio will return the top 5 results.
Pressing 0 will return the last 5 results.

User is expected to type better search queries if they want to hear what they want.

## Features to develop
Not hardcoding in my spotify account 😬

## Known issues
When the playlist is queue and the last song has reached the end, nothing is playing. This is expected.

Then the user selects a track. It gets added to the queue but then the queuer may delete the track and skip to another track from the 'Recommended' playlist. This is not expected.