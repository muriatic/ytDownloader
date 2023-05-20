"""This Module Downloads Videos from YouTube and Will Convert MP4 Files to Audio"""
import traceback
import sys
import os
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pytube import YouTube
from moviepy import editor as moviepy
import requests
import eel

### END OF IMPORT ###

class InvalidLinkException(Exception):
    """Raised when YouTube returns a non-200 status code"""


class NonYoutubeLinkException(Exception):
    """Raised when the url is not YouTube"""


class VideoUnavailableException(Exception):
    """Raised when the YouTube video is unavailable"""


class NoMP4FilesToConvertException(Exception):
    """Raised when there are no MP4 files in the current directory"""


class EndBeforeStartException(Exception):
    """Raised when the end time is before the start time"""

class NonVideoLinkException(Exception):
    """Raised when a non-video youtube link is entered"""

# error handling
def show_exception_and_exit(exc_type, exc_value, tb_object):
    """Catches Exceptions and Prevents the App from Auto Closing"""
    traceback.print_exception(exc_type, exc_value, tb_object)
    input("Press ENTER to exit...")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit


class link_validation():
    def __init__(self, link):
        self.link = link
        self.parsed_url = urlparse(link)

    def is_clip(self) -> bool:
        """Tests to make sure the link is valid and if successful, returns whether it is a clip"""        
        # check if it is a clip
        # clips path start with /clip
        if self.parsed_url.path.startswith("/clip"):
            return True
        
        return False
    

    def partial_validation(self) -> None:
        parsed_url = urlparse(self.link)

        netloc = parsed_url.netloc
        path = parsed_url.path
        scheme = parsed_url.scheme

        check_field1 = netloc
        check_field2 = path

        if scheme == '':
            try:
                check_field1, check_field2 = path.split('/')
                check_field2 = '/' + check_field2
            except ValueError:
                check_field1 = path
                check_field2 = ''
        
        # check if it is a YouTube link
        if check_field1 not in ("www.youtube.com", "youtu.be", "youtube.com"):
            raise NonYoutubeLinkException(f"link {self.link} is not a YouTube address")

        # check if it is a traditional video
        # videos path start with /watch or nothing if the netloc is youtu.be
        elif not (check_field2.startswith("/watch") or check_field2.startswith("/shorts") or check_field2.startswith("/clip")) and check_field1 != "youtu.be":
            raise NonVideoLinkException(f"{self.link} is a non-video YouTube link")
        
        elif check_field1 == "youtu.be" and check_field2 == '':
            raise NonVideoLinkException(f"{self.link} is a non-video YouTube link")



    def full_link_validation(self) -> None:
        request = requests.get(self.link, timeout=3)

        # check if the video is available
        if "Video unavailable" in request.text:
            raise VideoUnavailableException(
                f"the YouTube video at: {self, self.link} is unavailable; please check that your link is correct")

        # check to see if YouTube returns a good status code (200)
        if request.status_code != 200:
            raise InvalidLinkException(f"link {self, self.link} returned Status Code {request.status_code}")


class ClippedContent():
    """opens chromedriver and will get the videoId, start_time_ms, end_time_ms"""
    def __init__(self, video_url = '', custom = False):
        if not custom:
            options = webdriver.ChromeOptions()
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--test-type")
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)

            driver.get(video_url)

            try:
                # find "accept all" button and submit...
                button = [button for button in driver.find_elements(by=By.TAG_NAME, value="button")
                    if button.accessible_name and button.accessible_name.lower() == 'accept all'][0]
                button.submit()
            except IndexError:
                pass

            # https://stackoverflow.com/a/26567563/12693728: wait for page to be loaded
            timeout = 3
            try:
                element_present = EC.presence_of_element_located(
                    (By.CLASS_NAME, 'html5-video-container '))
                WebDriverWait(driver, timeout).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")

            video_id = driver.page_source.split('"videoDetails":{"videoId":"')[1]
            self.video_id = video_id.split('"')[0]
            # print(video_id)

            start_time_ms = driver.page_source.split('"startTimeMs":"')[1]
            self.start_time_ms = int(start_time_ms.split('"')[0])

            end_time_ms = driver.page_source.split('"endTimeMs":"')[1]
            self.end_time_ms = int(end_time_ms.split('"')[0])

            driver.quit()

            # get non Clip link AFTER the driver has been closed
            self.original_video_link ="https://youtu.be/" + self.video_id


    def trim_content(self, name, start_time_sec=-1, end_time_sec=-1) -> None:
        """Cuts the Video based on start_time_ms and end_time_ms"""
        name_mp4 = name + '.mp4'

        if start_time_sec == -1 and end_time_sec == -1:
            start_time_sec, end_time_sec = self.start_time_ms / 1000, self.end_time_ms / 1000

        video = moviepy.VideoFileClip(name_mp4)

        video = video.subclip(start_time_sec, end_time_sec)

        save_name = name + '_trim.mp4'

        video.write_videofile(save_name)

        video.close()


class VideoData():
    """necessary Functions for downloading and converting the MP4s and cleaning up after"""
    # class videos():
    def __init__(self, nameMP4, original_file_path=None):
        self.name_mp4 = nameMP4
        self.name = nameMP4.removesuffix('.mp4')
        self.original_file_path = original_file_path


    def download_video(self, link) -> int:
        """Download the video"""
        download_link = link

        youtube = YouTube(download_link)

        video = youtube.streams.get_highest_resolution()
        video.download(filename=self.name_mp4)

        return 0


    def convert_mp4(self, audio_type, clip=False) -> None:
        """Convert the MP4 to the desired file type"""
        suffix = '_trim' if clip else ''

        end_name = self.name + suffix + audio_type

        dir_path = os.getcwd()

        video_path = self.original_file_path if self.original_file_path != None else dir_path

        video_file_path = os.path.join(video_path, self.name_mp4)
        audio_file_path = os.path.join(dir_path, end_name)

        if os.path.exists(video_file_path):

            file_to_convert = moviepy.AudioFileClip(video_file_path)
            file_to_convert.write_audiofile(audio_file_path)

            file_to_convert.close()

        else:
            raise FileNotFoundError(f"FileNotFoundError: file {self.name_mp4} not found")


    def clean_up(self, clip=False, audio_only=True) -> None:
        """Clean up any unwanted mp4s"""
        if os.path.exists(self.name_mp4) and (audio_only or clip):
            os.remove(self.name_mp4)

        trimmed_name = self.name + '_trim' + '.mp4'
        if clip and audio_only and os.path.exists(trimmed_name):
            os.remove(trimmed_name)


class MenuNav():
    """menu navigation that handles input"""
    def convert_existing_mp4(self, file_path, audio_type) -> None:
        """File Name"""
        # split the total path into path and file 
        original_file_path, nameMP4 = file_path.rsplit('/', 1)

        functions = VideoData(nameMP4, original_file_path)

        functions.convert_mp4(audio_type)
        functions.clean_up()


    def download_yt_etc(self, link, name, audio_only, file_format, start=None, end=None) -> None:
        """File Name and Video URL"""

        # maybe have this activate/deactivate convert button with a try, except block
        clip = link_validation(link).is_clip()
        audio_type = '.mp3' if file_format else '.wav'

        nameMP4 = name + '.mp4'

        functions = VideoData(nameMP4=nameMP4)
        
        custom = None not in (start, end)

        if custom:
            ClippedContent(link, custom).trim_content(name, start, end)
            clip, audio_only = custom

        elif clip:
            clips_instance = ClippedContent(link)
            link = clips_instance.original_video_link
            downloaded = functions.download_video(link)
            clips_instance.trim_content(name)
            
        else:
            downloaded = functions.download_video(link)

        if audio_only:
            # now that we have the downloaded video lets convert it 
            functions.convert_mp4(audio_type, clip)

        functions.clean_up(clip, audio_only)

        return downloaded


# start eel local web server 
eel.init("web")

@eel.expose
def partial_validation(URL):
    if URL != '':
        try:
            link_validation(URL).partial_validation()
            return 0
        except NonYoutubeLinkException:
            return -2
        except NonVideoLinkException:
            return -1
    else:
        return 1

@eel.expose
def download_video(url, fileName, audio_only, fileFormat, start, end) -> int:
    try:
        link_validation(url).full_link_validation()
    except VideoUnavailableException:
        return -1
    except InvalidLinkException:
        return -2
    
    if 'null' in (start, end):
        start, end = None

    return MenuNav().download_yt_etc(url, fileName, audio_only, fileFormat, start, end)
    

# starts chrome
# can add params like port, host, mode, size, 
eel.start("index.html")

sys.exit(-1)

# if __name__ == '__main__':
#     MenuNav()
