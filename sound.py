# import multiprocessing
# from playsound import playsound

# p = multiprocessing.Process(target=playsound, args=("different.mp3",))
# p.start()
# input("press ENTER to stop playback")
# p.terminate()
from pygame import mixer
import time
mixer.init() #Initialzing pyamge mixer

mixer.music.load('faded.mp3') 
mixer.music.play()
input("Press Enter to stop playing")
mixer.music.stop()