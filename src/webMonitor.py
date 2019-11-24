from model.mainClass import Spot
import time

spotQueue = Spot()
programActive = True

while programActive:
    print("webMonitor active!")
    # Monitor playback every 5 seconds
    try:
        currentTrack = spotQueue.getCurrentTrack()
        currentPlaybackIsQueue = spotQueue.isCurrentPlaybackQueueList()
        # print(currentTrack)
        if currentTrack is not None and currentPlaybackIsQueue:
            # print("removing track")
            spotQueue.removeCurrentSongFromQueue()
        time.sleep(20)
    except KeyboardInterrupt:
        print("Closing program. Goodbye!")
        programActive = False
    except Exception as e:
        print("Encountered error: {}".format(e))
        programActive = False
