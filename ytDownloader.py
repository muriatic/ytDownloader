from pytube import YouTube
import os
from moviepy.editor import *
import keyboard
from time import sleep
from urllib.parse import urlparse
import requests 

class InvalidLinkException(Exception):
    """Raised when the YouTube url does not exist"""
    pass


class NonYoutubeLinkException(Exception):
    """Raised when the url is not YouTube"""
    pass


def linkValidation(link):
    parsedUrl = urlparse(link)
    if parsedUrl.netloc != "www.youtube.com" and parsedUrl.netloc != "youtu.be":
        raise NonYoutubeLinkException(f"link {link} is not a YouTube address")

    if requests.get(link) != 200:
        raise InvalidLinkException(f"link {link} is not a valid YouTube address")
    

def download_video(video_url, name):
    nameMP4 = name + ".mp4"

    youtube = YouTube(video_url)

    print("Be patient. Downloading...")

    video = youtube.streams.get_highest_resolution()
    video.download(filename=nameMP4)

    print("Video Downloaded Successfully")


def convertMP4(name, type):
    nameMP4 = name + ".mp4"
    
    print(nameMP4)

    match type:
        case 'mp3':
            endName = name + ".mp3"
        case 'wav':
            endName = name + '.wav'

    dir_path = os.getcwd()

    video_file_path = os.path.join(dir_path, nameMP4)
    audio_file_path = os.path.join(dir_path, endName)

    if os.path.exists(video_file_path):

        FILETOCONVERT = AudioFileClip(video_file_path)
        FILETOCONVERT.write_audiofile(audio_file_path)

        FILETOCONVERT.close()
    
    else:
        raise FileNotFoundError(f"FileNotFoundError: file {nameMP4} not found")


def mp3ORmp4(name, link=''):
    key_event = keyboard.read_event(suppress=True)

    formatQuestion = key_event.name

    nameMP4 = name + '.mp4'

    sleep(1)

    match formatQuestion:
        case '0':
            if link != '':
                download_video(link, name)

            convertMP4(name, 'mp3')
        
        case '1':
            if link != '':
                download_video(link, name)

            convertMP4(name, 'wav')
        
        # case '3':
        #     if link != '':
        #         download_video(link, name)
        #     fileFormat = input("Type in file extension (e\nWarning: Experimental)")

        case 'esc':
            quit()

        case _:
            mp3ORmp4(name, link)

    if os.path.exists(nameMP4):
        os.remove(nameMP4)


def yes1():
    print("Files in Directory:")

    # get list of Files
    listOfFiles = []

    n = 0

    for file in os.listdir():
        if file.endswith(".mp4"):
            print(f"({n}) {file}")
            listOfFiles.append(file)
            n += 1

    # get name or position
    name = input("\nFile Name: \n>>> ")

    # try to convert to Integer
    try:
        position = int(name)
        file = listOfFiles[position].removesuffix('.mp4')

        print("\nFile Format: \n(0) .mp3 \n(1) .wav\n")

        mp3ORmp4(file)

    # if integer conversion fails with ValueError
    except ValueError:
        try:
            if name.endswith('.mp4'):
                name = name.removesuffix('.mp4')

            mp3ORmp4(name)
            
        except FileNotFoundError:
            print(f"FileNotFoundError: file {name}.mp4 does not exist")


def no1():
    link = input("Video URL: \n>>> ")

    linkValidation(link)

    name = input("File Name: \n>>> ")

    while True:    
        audioQuestion = input("Audio Only: \n>>> ").lower()

        if audioQuestion == "yes":
            
            print("File Format: \n(0) .mp3 \n(1) .wav\n")

            mp3ORmp4(name, link)

            break

        elif audioQuestion == "no":
            download_video(link, name)
            break

        else:
            continue

def question1():
    key_event = keyboard.read_event(suppress=True)
    
    MP4ToMP3Question = key_event.name
    
    sleep(1)

    match MP4ToMP3Question:
        case 'y':
            yes1()

        case 'Y':
            yes1()

        case '0':
            yes1()
        
        case 'n':
            no1()

        case 'N':
            no1()
        
        case '1':
            no1()
        
        case 'esc':
            quit()

        case _:
            question1()

def main():
    print("Press ESC at anytime to exit...\n")

    print("Would you like to use MP4 to Audio? \n0. (Y)\n1. (N)\n")
    
    question1()

    input("\nPress enter to close...")

if __name__ == '__main__':
    main()