from pytube import YouTube
import os
from moviepy.editor import *

def download_video(video_url, name):
    nameMP4 = name + ".mp4"

    youtube = YouTube(video_url, '''use_oauth=True, allow_oauth_cache=True''')

    print("Be patient. Downloading...")

    video = youtube.streams.get_highest_resolution()
    video.download(filename=nameMP4)

    print("Video Downloaded Successfully")

def MP4ToMP3(name):
    nameMP4 = name + ".mp4"
    nameMP3 = name + ".mp3"

    video_file_path = os.path.join(dir_path, nameMP4)
    audio_file_path = os.path.join(dir_path, nameMP3)

    if os.path.exists(video_file_path):
        FILETOCONVERT = AudioFileClip(video_file_path)
        FILETOCONVERT.write_audiofile(audio_file_path)

        FILETOCONVERT.close()

        return nameMP4
    
    else:
        raise ValueError(f"File {nameMP4} Does Not Exist")
    

dir_path = os.path.dirname(os.path.realpath(__file__))

while True:
    MP4toMP3Question = str(input("Would you like to use MP4 to MP3? \n")).lower()

    if MP4toMP3Question == "yes":
        name = str(input("File Name (excluding File Extension): \n>>> "))


        MP4ToMP3(name)

        break

    elif MP4toMP3Question == "no":
        link = str(input("Video URL: \n>>> "))
        name = str(input("File Name: \n>>> "))

        while True:    
            audioQuestion = str(input("Audio Only: \n>>> ")).lower()

            if audioQuestion == "yes":
                download_video(link, name)
                nameMP4 = str(MP4ToMP3(name))

                print(nameMP4)
                if os.path.exists(nameMP4):
                    os.remove(nameMP4)

                break

            elif audioQuestion == "no":
                download_video(link, name)
                break

            else:
                continue
        
        break

    else: 
        continue