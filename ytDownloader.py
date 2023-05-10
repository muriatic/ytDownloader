from pytube import YouTube
import os
from moviepy.editor import *
import keyboard
from time import sleep
from urllib.parse import urlparse
import requests 


class InvalidLinkException(Exception):
    """Raised when YouTube returns a non-200 status code"""
    pass


class NonYoutubeLinkException(Exception):
    """Raised when the url is not YouTube"""
    pass


class VideoUnavailableException(Exception):
    """Raised when the YouTube video is unavailable or it is a non-video link"""
    pass


class NoMP4FilesToConvertException(Exception):
    """Raised when there are no MP4 files in the current directory"""
    pass

# error handling
def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press ENTER to exit...")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit


def linkValidation(link):
    parsedUrl = urlparse(link)
    
    netloc = parsedUrl.netloc
    #check if it is a YouTube link
    if netloc != "www.youtube.com" and netloc != "youtu.be" and netloc != "youtube.com":
        raise NonYoutubeLinkException(f"link {link} is not a YouTube address")

    print(parsedUrl)

    r = requests.get(link)

    # check if it is a clip or video 
    # clips path start with /clip; videos path start with /watch or nothing if the netloc is youtu.be
    if not(parsedUrl.path.startswith("/watch") or parsedUrl.path.startswith("/clip")) and netloc != "youtu.be":
        raise VideoUnavailableException(f"{link} is a non-video YouTube link")
    
    # check if the video is available
    elif "Video unavailable" in r.text:
        raise VideoUnavailableException(f"the YouTube video at: {link} is unavailable; please check that your link is correct")

    # check to see if YouTube returns a good status code (200)
    elif r.status_code != 200:
        raise InvalidLinkException(f"link {link} returned Status Code {r.status_code}")
    
    print(r.text)
    

"""
short share:
https://youtu.be/                       NiXD4xVJM5Y

long share:
https://www.youtube.com/watch?v=        NiXD4xVJM5Y         &ab_channel=JamieDupuis

CLIPS

https://youtube.com/clip/   Ugkx    c8KaNg8mSIP9WM3idtxMuBRjEpwvUyr8     0     -    15      (   15   )
https://youtube.com/clip/   Ugkx    buL4bGfKiQNMZoP5Rr_a38_cUbi9_4tZ     15    -    30      (   15   )
https://youtube.com/clip/   Ugkx    Wg134ml4MFitqmZOgeSbG88CBj7cRoCk     30    -    45      (   15   )
https://youtube.com/clip/   Ugkx    D7rDzyX2pYJtK6AwDob13HRWKuyqUJZv     04.2  -    19.2    (   12.7 )
""" 


# linkValidation('https://www.youtube.com/watch?v=ZAEM2NZ9EIg&ab_channel=costdiamonds')
# linkValidation('https://youtube.com/clip/Ugkx2f_tTWRE9rTFUYJgwvZHutTFDD9KTQn3')
# linkValidation('https://youtu.be/BQS4kLal7-k')
# linkValidation('https://www.youtube.com/channel/UCpJpFOOAcyumWjDTCzGpd9g')
# quit()


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

    # get list of Files
    listOfFiles = []

    n = 0

    for file in os.listdir():
        if file.endswith(".mp4"):
            listOfFiles.append(file)

    if len(listOfFiles) == 0:
        dir_path = os.getcwd()
        raise NoMP4FilesToConvertException(f"there are no MP4 files available to be converted in the directory: [{dir_path}]")

    print("Files in Directory:")
    for file in listOfFiles:
        print(f"({n}) {file}")
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
        audioQuestion = input("Audio Only ('Yes' or 'No'): \n>>> ").lower()

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

    print("Would you like to convert an existing MP4 to Audio? \n0. (Y)\n1. (N)\n")
    
    question1()

    print("Press R to run again, or ESC to close")
    
    key_event = keyboard.read_event(suppress=True)
    
    rerun = key_event.name
    
    match rerun:
        case 'R':
            main()
        
        case _:
            quit()
        

if __name__ == '__main__':
    main()