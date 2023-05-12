from pytube import YouTube
import os
from moviepy.editor import *
from urllib.parse import urlparse
import requests 

"""Download your browser's version of ChromeDriver from https://chromedriver.chromium.org/downloads"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

### END OF IMPORT ###

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


def linkValidation(link) -> bool:
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
    if not (parsedUrl.path.startswith("/watch") or parsedUrl.path.startswith("/shorts")) and netloc != "youtu.be":
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

        # get non Clip link AFTER the driver has been closed
        self.originalVideoLink ="https://youtu.be/" + self.video_id
   

    def trimContent(self, name) -> None:
        nameMP4 = name + '.mp4'

        startTimeSec, endTimeSec = self.startTimeMs / 1000, self.endTimeMs / 1000

        video = VideoFileClip(nameMP4)

        video = video.subclip(startTimeSec, endTimeSec)

        saveName = name + '_trim.mp4'

        video.write_videofile(saveName)

        video.close()

    
class functions():
    # class videos():
    def __init__(self, name):
        self.nameMP4 = name + '.mp4'
        self.name = name


    """Download the video"""
    def downloadVideo(self, link) -> None:
        downloadLink = link

        youtube = YouTube(downloadLink)

        print("Be patient. Downloading...")

        video = youtube.streams.get_highest_resolution()
        video.download(filename=self.nameMP4)

        print("Video Downloaded Successfully")


    """Convert the MP4 to the desired file type"""
    def convertMP4(self, type, clip=False) -> None:
        suffix = '_trim' if clip else ''

        endName = self.name + suffix + type

        dir_path = os.getcwd()

        video_file_path = os.path.join(dir_path, self.nameMP4)
        audio_file_path = os.path.join(dir_path, endName)

        if os.path.exists(video_file_path):

            FILETOCONVERT = AudioFileClip(video_file_path)
            FILETOCONVERT.write_audiofile(audio_file_path)

            FILETOCONVERT.close()
        
        else:
            raise FileNotFoundError(f"FileNotFoundError: file {self.nameMP4} not found")

        
    def cleanUp(self, clip=False, audioOnly=True) -> None:
        if os.path.exists(self.nameMP4) and (audioOnly or clip):
            os.remove(self.nameMP4)
        
        trimmedName = self.name + '_trim' + '.mp4'
        if clip and audioOnly and os.path.exists(trimmedName):
            os.remove(trimmedName)


class menuNav():
    def __init__(self):
        self.questionDictionary = {}
        self.questionDictionary["Codes"] = ['Q1', 'Q2Y', 'Q2N1', 'Q2N2', 'Q2N3', 'Q3']
        self.questionDictionary["Question"] = ["Would you like to convert an existing MP4 to Audio? \n0. (Y)\n1. (N)\n", "File Name: \n>>> ", "Video URL: \n>>> ", "File Name: \n>>> ", "Audio Only ('Yes' or 'No'): \n", "File Format: \n(0) .mp3 \n(1) .wav"]
        self.questionDictionary["Accepted Answers"] = [[['y', 'yes', '0'], ['n', 'no', '1']], False, False, False, [['yes', 'y', '1'], ['no', 'n', '0']], [['0', '.mp3', 'mp3'], ['1', '.wav', 'wav']]]

    """POSING QUESTIONS"""
    def questionPoser(self, questionCode: str) -> any:
        position = self.questionDictionary["Codes"].index(questionCode)
        question = self.questionDictionary["Question"][position]
        
        response = ''
        
        answers = self.questionDictionary["Accepted Answers"][position]

        while True:
            response = input(question)

            # checks if the question has answers list, if not just returns the response; NO need to run any of the logic again 
            if not answers:
                return response

            try:
                int(response)
            except ValueError:
                response = response.lower()         
            
            validResponse = any(response in i for i in answers)

            if validResponse:
                break

        if response in answers[0]:
            return True
        
        return False
    

    def Q3(self, name, link='', clip=False) -> None:
        formatQuestion = self.questionPoser('Q3')

        type = '.mp3'

        if not formatQuestion:
            type = '.wav'

        if clip:
            _clipsInstance = clippedContent(link)
            link = _clipsInstance.originalVideoLink
            functions(name).downloadVideo(link)
            _clipsInstance.trimContent(name)
                
        elif link != '':
            functions(name).downloadVideo(link)

        functions(name).convertMP4(type, clip)


    def Q2Y(self) -> None:
        # get list of Files
        listOfFiles = []

        for file in os.listdir():
            if file.endswith(".mp4"):
                listOfFiles.append(file)

        if len(listOfFiles) == 0:
            dir_path = os.getcwd()
            raise NoMP4FilesToConvertException(f"there are no MP4 files available to be converted in the directory: [{dir_path}]")

        n = 0
        print("Files in Directory:")
        for file in listOfFiles:
            print(f"({n}) {file}")
            n += 1

        name =self.questionPoser(self.Q2Y.__name__)

        # try to convert to Integer
        try:
            position = int(name)
            file = listOfFiles[position].removesuffix('.mp4')

            self.Q3(file)

        # if integer conversion fails with ValueError
        except ValueError:
            try:
                if name.endswith('.mp4'):
                    name = name.removesuffix('.mp4')

                self.Q3(name)
                
            except FileNotFoundError:
                print(f"FileNotFoundError: file {name}.mp4 does not exist")


    def Q2N(self) -> None:
        link = self.questionPoser('Q2N1')

        clip = linkValidation(link)

        name = self.questionPoser('Q2N2')

        audioQuestion = self.questionPoser('Q2N3')

        if audioQuestion:
            self.Q3(name, link, clip)

            functions(name).cleanUp(clip)
        elif clip:
            _clipsInstance = clippedContent(link)
            link = _clipsInstance.originalVideoLink
            functions(name).downloadVideo(link)
            _clipsInstance.trimContent(name)
            functions(name).cleanUp(clip, False)    
        else:
            functions(name).downloadVideo(link)


    def Q1(self) -> None:
        answer = self.questionPoser('Q1')

        if answer:
            self.Q2Y()
        else:
            self.Q2N()


if __name__ == '__main__':
    menuNav().Q1()
