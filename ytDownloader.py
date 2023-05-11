from pytube import YouTube
import os
from moviepy.editor import *
import keyboard
from time import sleep
from urllib.parse import urlparse
import requests 

"""Download your browser's version of ChromeDriver from https://chromedriver.chromium.org/downloads"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


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

    r = requests.get(link)

    # check if it is a clip 
    # clips path start with /clip
    if parsedUrl.path.startswith("/clip"):
        return True

    # check if it is a traditional video
    # videos path start with /watch or nothing if the netloc is youtu.be
    if not parsedUrl.path.startswith("/watch") and netloc != "youtu.be":
        raise VideoUnavailableException(f"{link} is a non-video YouTube link")
    
    # check if the video is available
    elif "Video unavailable" in r.text:
        raise VideoUnavailableException(f"the YouTube video at: {link} is unavailable; please check that your link is correct")

    # check to see if YouTube returns a good status code (200)
    elif r.status_code != 200:
        raise InvalidLinkException(f"link {link} returned Status Code {r.status_code}")
    
    return False


class clippedContent():
    """opens chromedriver and will get the videoId, startTimeMs, endTimeMs"""
    def __init__(self, video_url):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        driver.get(video_url)

        try:    
            # find "accept all" button and submit...
            b = [b for b in driver.find_elements(by=By.TAG_NAME, value="button") if b.accessible_name and b.accessible_name.lower() == 'accept all'][0]
            b.submit()
        except:
            pass

        # https://stackoverflow.com/a/26567563/12693728: wait for page to be loaded. retrieving video id sometimes fails...suppose because of async resources are not being loaded in a deterministic order/time...assume that when the video container is ready, the page is fully loaded...
        timeout = 3
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'html5-video-container '))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

        video_id = driver.page_source.split('"videoDetails":{"videoId":"')[1]
        self.video_id = video_id.split('"')[0]
        # print(video_id)

        startTimeMs = driver.page_source.split('"startTimeMs":"')[1]
        self.startTimeMs = int(startTimeMs.split('"')[0])

        endTimeMs = driver.page_source.split('"endTimeMs":"')[1]
        self.endTimeMs = int(endTimeMs.split('"')[0])

        driver.quit()
   

    def trimContent(self, name):
        nameMP4 = name + '.mp4'

        startTimeSec, endTimeSec = self.startTimeMs / 1000, self.endTimeMs / 1000

        video = VideoFileClip(nameMP4)

        video = video.subclip(startTimeSec, endTimeSec)

        saveName = name + '_trim.mp4'

        video.write_videofile(saveName)

        video.close()

    
class functions():
    """Download the video, getting the original video link if necessary"""
    def download_video(link, name, clip=False):
        downloadLink = link

        # get non Clip link
        if clip:
            downloadLink = "https://youtu.be/" + clippedContent(link).video_id

        nameMP4 = name + ".mp4"

        youtube = YouTube(downloadLink)

        print("Be patient. Downloading...")

        video = youtube.streams.get_highest_resolution()
        video.download(filename=nameMP4)

        print("Video Downloaded Successfully")

    """Convert the MP4 to the desired file type"""
    def convertMP4(name, type, clip=False):
        nameMP4 = name + ".mp4"

        suffix = '_trim' if clip else ''

        match type:
            case 'mp3':
                endName = name + suffix + ".mp3"
            case 'wav':
                endName = name + suffix + '.wav'

        dir_path = os.getcwd()

        video_file_path = os.path.join(dir_path, nameMP4)
        audio_file_path = os.path.join(dir_path, endName)

        if os.path.exists(video_file_path):

            FILETOCONVERT = AudioFileClip(video_file_path)
            FILETOCONVERT.write_audiofile(audio_file_path)

            FILETOCONVERT.close()
        
        else:
            raise FileNotFoundError(f"FileNotFoundError: file {nameMP4} not found")
        
    def cleanUp(name, clip=False):
        nameMP4 = name + '.mp4'

        if os.path.exists(nameMP4):
            os.remove(nameMP4)
        
        trimmedName = name + '_trim' + '.mp4'
        if clip and os.path.exists(trimmedName):
            os.remove(trimmedName)


class questions():
    """File Format"""
    def mp3ORwav(self, name, link='', clip=False):
        formatQuestion = input("")

        nameMP4 = name + '.mp4'

        sleep(1)

        # compare it to the tuple
        if formatQuestion in {'0', '.mp3', 'mp3'}:
            if link != '':
                functions.download_video(link, name, clip)

            if clip:
                clippedContent(link).trimContent(name)

            functions.convertMP4(name, 'mp3', clip)
        
        elif formatQuestion in {'1', '.wav', 'wav'}:
            if link != '':
                functions.download_video(link, name, clip)

            if clip:
                clippedContent(link).trimContent(name)

            functions.convertMP4(name, 'wav', clip)

        else:
            self.mp3ORwav(name, link, clip)

        
    def yes1(self):

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

            print("\nFile Format: \n(0) .mp3 \n(1) .wav")

            self.mp3ORwav(file)

        # if integer conversion fails with ValueError
        except ValueError:
            try:
                if name.endswith('.mp4'):
                    name = name.removesuffix('.mp4')

                self.mp3ORwav(name)
                
            except FileNotFoundError:
                print(f"FileNotFoundError: file {name}.mp4 does not exist")


    def no1(self):
        link = input("Video URL: \n>>> ")

        clip = linkValidation(link)

        name = input("File Name: \n>>> ")

        while True:    
            audioQuestion = input("Audio Only ('Yes' or 'No'): \n>>> ").lower()

            if audioQuestion == "yes":
                
                print("File Format: \n(0) .mp3 \n(1) .wav")

                self.mp3ORwav(name, link, clip)

                break

            elif audioQuestion == "no":
                functions.download_video(link, name, clip)

                # trim the clip
                if clip:
                    clippedContent(link).trimContent(name)

                break

            else:
                continue
        
        functions.cleanUp(name, clip)


    def question1(self):    
        MP4ToMP3Question = input("")
        
        sleep(1)

        if MP4ToMP3Question in {'y', 'Y', '0'}:
            self.yes1()

        elif MP4ToMP3Question in {'n', 'N', '1'}:
            self.no1()

        else:
            self.question1


    def __init__(self):
        print("Would you like to convert an existing MP4 to Audio? \n0. (Y)\n1. (N)\n")
        
        self.question1()

        print("Press ANY KEY to close or R to run again")
        
        key_event = keyboard.read_event(suppress=True)
        
        rerun = key_event.name
        
        match rerun:
            case 'R':
                self.main()

            case 'r':
                self.main()
            
            case _:
                quit()
        

if __name__ == '__main__':
    questions()