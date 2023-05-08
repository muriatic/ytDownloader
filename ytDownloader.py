from pytube import YouTube
import os
from moviepy.editor import *
import keyboard

def download_video(video_url, name):
    nameMP4 = name + ".mp4"

    youtube = YouTube(video_url) # use_oauth=True, allow_oauth_cache=True

    print("Be patient. Downloading...")

    video = youtube.streams.get_highest_resolution()
    video.download(filename=nameMP4)

    print("Video Downloaded Successfully")

dir_path = os.getcwd() # os.path.dirname(os.path.realpath(__file__))

def convertMP4ToMP3(name):
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
        raise FileNotFoundError

# def conversion(name):
#     print("What file would you ")

def question():
    key_event = keyboard.read_event(suppress=True)
    
    MP4ToMP3Question = key_event.name


    match MP4ToMP3Question:
        case 'y':
            print("Select File to Convert:")
            
            listOfFiles = []

            n = 0
            
            # get list of Files
            for file in os.listdir():
                if file.endswith(".mp4"):
                    print(f"({n}) {file}")
                    listOfFiles.append(file)
                    n += 1

            # get name or position
            name = str(input("\nFile Name (excluding File Extension): \n>>> "))

            # try to convert to Integer
            try:
                position = int(name)
                file = listOfFiles[position].removesuffix('.mp4')
                convertMP4ToMP3(file)

            except ValueError:
                try:
                    convertMP4ToMP3(name)
                    
                except FileNotFoundError:
                    print(f"FileNotFoundError: file {name}.mp4 does not exist")
            
        
        case 'n':
            link = str(input("Video URL: \n>>> "))
            name = str(input("File Name: \n>>> "))

            while True:    
                audioQuestion = str(input("Audio Only: \n>>> ")).lower()

                if audioQuestion == "yes":
                    download_video(link, name)
                    nameMP4 = str(convertMP4ToMP3(name))

                    if os.path.exists(nameMP4):
                        os.remove(nameMP4)

                    break

                elif audioQuestion == "no":
                    download_video(link, name)
                    break

                else:
                    continue
        
        case 'esc':
            return 0

        case _:
            question()

def main():
    print("Press ESC at anytime to exit...\n")

    print("Would you like to use MP4 to MP3? \n1. (Y)\n2. (N)\n")
    
    question()

    input("\nPress enter to close...")

if __name__ == '__main__':
    main()