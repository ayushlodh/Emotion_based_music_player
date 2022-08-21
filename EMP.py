import cv2
import numpy as np
import argparse
import time
import glob
import os
import Face
import pandas
import Update_Model
from pygame import mixer
import time
from win32com.client import Dispatch
from time import sleep

mixer.init()
video_capture = cv2.VideoCapture(0)
facecascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


fishface = cv2.face.FisherFaceRecognizer_create()
try:
    fishface.read("trained_emoclassifier.xml")
except:
    print("no xml found. Using --update will create one.")
parser = argparse.ArgumentParser(description="Options for the emotion-based music player") #Create parser object
parser.add_argument("--update", help="Call to grab new images and update the model accordingly", action="store_true") #dd --update argument
args = parser.parse_args() #Store any given arguments in an object

facedict = {}
emotions = ["angry", "happy", "sad", "neutral", "surprise"]

def crop_face(clahe_image, face):
    for (x, y, w, h) in face:
        faceslice = clahe_image[y:y+h, x:x+w]
        faceslice = cv2.resize(faceslice, (350, 350))
    facedict["face%s" %(len(facedict)+1)] = faceslice
    return faceslice

def update_model(emotions):
    print("Model update mode active")
    check_folders(emotions)
    for i in range(0, len(emotions)):
        save_face(emotions[i])
    pre = Face.precision()
    rec = Face.recall()
    print("collected images, looking good! Now updating model...")
    print("The average precision acheived : ")
    print(pre)
    print("The average recall acheived : ")
    print(rec)
    print("The average f1 score : ")
    print(2*pre*rec//(pre+rec))
    Update_Model.update(emotions)
    print("Done!")

def check_folders(emotions): #check if folder infrastructure is there, create if absent
    for x in emotions:
        if os.path.exists("dataset\\%s" %x):
            pass
        else:
            os.makedirs("dataset\\%s" %x)

def save_face(emotion):
    print("\n\nplease look " + emotion + " when the timer expires and keep the expression stable until instructed otherwise.")
    for i in range(0,5):#Timer to give you time to read what emotion to express
        print(5-i)
        time.sleep(1)
    while len(facedict.keys()) < 16: #Grab 15 images for each emotion
        detect_face()
    for x in facedict.keys(): #save contents of dictionary to files
        cv2.imwrite("dataset\\%s\\%s.jpg" %(emotion, len(glob.glob("dataset\\%s\\*" %emotion))), facedict[x])
    facedict.clear() #clear dictionary so that the next emotion can be stored

def recognize_emotion():
    predictions = []
    confidence = []
    for x in facedict.keys():
        pred, conf = fishface.predict(facedict[x])
        cv2.imwrite("images\\%s.jpg" %x, facedict[x])
        predictions.append(pred)
        confidence.append(conf)
        # print(predictions)
        # print(confidence)
    #print("I think you're %s" %emotions[max(set(predictions), key=predictions.count)])
    
    #mp = Dispatch("WMPlayer.OCX")
    if predictions[0] == 0:
        #tune = mp.newMedia("astronaut.mp3")
        print("Angry song is playing.")
        mixer.music.load('astronaut.mp3') 
        mixer.music.play()
        input("Press Enter to stop playing")
        mixer.music.stop()
    elif predictions[0] == 1:
        #tune = mp.newMedia("faded.mp3")
        print("Happy song is playing.")
        mixer.music.load('faded.mp3') 
        mixer.music.play()
        input("Press Enter to stop playing")
        mixer.music.stop()
    elif predictions[0] == 2:
        #tune = mp.newMedia("lostcontrol.mp3")
        print("Sad song is playing.")
        mixer.music.load('lostcontrol.mp3') 
        mixer.music.play()
        input("Press Enter to stop playing")
        mixer.music.stop()
    elif predictions[0] == 3:
        #tune = mp.newMedia("play.mp3")
        if(confidence[0] <= 1800):
            print("Angry song is playing.")
            mixer.music.load('astronaut.mp3') 
            mixer.music.play()
            input("Press Enter to stop playing")
            mixer.music.stop()
        else:
            print("Happy song is playing.")
            mixer.music.load('faded.mp3')
            mixer.music.play()
            input("Press Enter to stop playing")
            mixer.music.stop()
    elif predictions[0] == 4:
        #tune = mp.newMedia("different.mp3")
        print("Surprise song is playing.")
        mixer.music.load('different.mp3')
        mixer.music.play()
        input("Press Enter to stop playing")
        mixer.music.stop()

    # mp.currentPlaylist.appendItem(tune)
    # mp.controls.play()
    # sleep(1)
    # mp.controls.playItem(tune)
    # # to stop playing use
    # input("Press Enter to stop playing")
    # mp.controls.stop()
    
def grab_webcamframe():
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_image = clahe.apply(gray)
    return clahe_image

def detect_face():
    clahe_image = grab_webcamframe()
    face = facecascade.detectMultiScale(clahe_image, scaleFactor=1.1, minNeighbors=15, minSize=(10, 10), flags=cv2.CASCADE_SCALE_IMAGE)
    if len(face) == 1: 
        faceslice = crop_face(clahe_image, face)
        return faceslice
    else:
        print("no/multiple faces detected, passing over frame")

while True:
    detect_face()
    if args.update: #If update flag is present, call update function
        update_model(emotions)
        break
    elif len(facedict) == 1: #otherwise it's regular a runtime, continue normally with emotion detection functionality
        recognize_emotion()
        break
