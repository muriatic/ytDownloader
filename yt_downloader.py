"""This Module Downloads Videos from YouTube and Will Convert MP4 Files to Audio"""
import traceback
import sys
import os
from urllib.parse import urlparse
from tkinter import Tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pytube import YouTube
from moviepy import editor as moviepy
import requests

# I don't know why this is necessary, but something about when this is compiled
# without a console causes an attribute error with std in/out I think,
# there are several solutions, this is the one I chose
# see https://github.com/python-eel/Eel/issues/654 for more

if __name__ == '__main__':
    # this may need fixing on compilation
    with open(os.devnull, 'w') as f: # pylint: disable=unspecified-encoding
        sys.stdout = f
        sys.stderr = f

# yes, pylint gets angry, but this needs to come after the above code
# otherwise eel doesn't get the right stdout, stderr (see above github page)
import eel # pylint: disable=wrong-import-position

### END OF IMPORT ###

class InvalidUrlException(Exception):
    """Raised when YouTube returns a non-200 status code"""


class NonYoutubeUrlException(Exception):
    """Raised when the url is not YouTube"""


class VideoUnavailableException(Exception):
    """Raised when the YouTube video is unavailable"""


class NoMP4FilesToConvertException(Exception):
    """Raised when there are no MP4 files in the current directory"""


class EndBeforeStartException(Exception):
    """Raised when the end time is before the start time"""

class NonVideoUrlException(Exception):
    """Raised when a non-video youtube url is entered"""

# error handling
def show_exception_and_exit(exc_type, exc_value, tb_object):
    """Catches Exceptions and Prevents the App from Auto Closing"""
    traceback.print_exception(exc_type, exc_value, tb_object)
    input("Press ENTER to exit...")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit


class UrlValidation():
    """Class for UrlValidation, returns clip value, status codes, and correct paths"""
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)

        # check if it is a clip
        self.is_clip = self.parsed_url.path.startswith("/clip")


    def partial_validation(self) -> None:
        """only validates based on the string itself, does not check if YouTube responds to it"""
        netloc = self.parsed_url.netloc
        path = self.parsed_url.path
        scheme = self.parsed_url.scheme

        check_field1 = netloc
        check_field2 = path

        if scheme == '':
            try:
                check_field1, check_field2 = path.split('/')
                check_field2 = '/' + check_field2
            except ValueError:
                check_field1 = path
                check_field2 = ''

        valid_prefixes = ("/watch", "/shorts", "/clip")

        # check if it is a YouTube url
        if check_field1 not in ("www.youtube.com", "youtu.be", "youtube.com"):
            raise NonYoutubeUrlException(f"url {self.url} is not a YouTube address")

        # check if it is a long video url (non youtu.be)
        if ((not check_field2.startswith(tuple(valid_prefixes)) and check_field1 != "youtu.be") or
            (check_field1 == "youtu.be" and check_field2 == '')):
            raise NonVideoUrlException(f"{self.url} is a non-video YouTube url")


    def full_url_validation(self) -> None:
        """Checks to see if YouTube actually provides a response"""
        request = requests.get(self.url, timeout=3)

        # check if the video is available
        if "Video unavailable" in request.text:
            raise VideoUnavailableException(
                f"the YouTube video at: {self.url} is unavailable; please check that your url is correct") #pylint: disable=line-too-long 

        # check to see if YouTube returns a good status code (200)
        if request.status_code != 200:
            raise InvalidUrlException(
                f"url {self.url} returned Status Code {request.status_code}")


class VideoData():
    """necessary Functions for downloading and converting the MP4s and cleaning up after"""
    def __init__(self, name_mp4: str, original_file_path: str = None) -> None:
        self.name_mp4 = name_mp4
        self.name = name_mp4.removesuffix('.mp4')
        self.original_file_path = original_file_path


    def download_video(self, url: str, audio_only: bool, file_format: str) -> int:
        """Download the video"""
        youtube = YouTube(url)
        if audio_only:
            video = youtube.streams.filter(only_audio=True).first()
            video.download(filename=(self.name+file_format))
        else:
            video = youtube.streams.get_highest_resolution()
            video.download(filename=self.name_mp4)
            
        return 0


    def convert_mp4(self, audio_type: str, clip: bool = False) -> None:
        """Convert the MP4 to the desired file type"""
        suffix = '_trim' if clip else ''

        end_name = self.name + suffix + audio_type
        dir_path = os.getcwd()

        video_path = self.original_file_path if self.original_file_path is not None else dir_path
        video_file_path = os.path.join(video_path, self.name_mp4)
        audio_file_path = os.path.join(dir_path, end_name)

        if os.path.exists(video_file_path):
            file_to_convert = moviepy.AudioFileClip(video_file_path)
            file_to_convert.write_audiofile(audio_file_path)
            file_to_convert.close()

        else:
            raise FileNotFoundError(f"File {self.name_mp4} not found")


    def clean_up(self, clip: bool = False, audio_only: bool = True) -> None:
        """Clean up any unwanted mp4s"""
        if os.path.exists(self.name_mp4) and (audio_only or clip):
            os.remove(self.name_mp4)

        trimmed_name = self.name + '_trim' + '.mp4'
        if clip and audio_only and os.path.exists(trimmed_name):
            os.remove(trimmed_name)


    def original_video_info(self, clip_url: str = '') -> tuple[str, int, int]:
        """opens chromedriver and will get the videoId, start_time_ms, end_time_ms"""
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        driver.get(clip_url)

        try:
            # find "accept all" button and submit...
            button = [
                button for button in driver.find_elements(by=By.TAG_NAME, value="button")
                if button.accessible_name and button.accessible_name.lower() == 'accept all'
            ][0]
            button.submit()
        except IndexError:
            pass

        timeout = 3
        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, 'html5-video-container ')
            )
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

        # oneliners to get the desired values, because Python...
        video_id = driver.page_source.split('"videoDetails":{"videoId":"')[1].split('"')[0]
        start_time_ms = int(driver.page_source.split('"startTimeMs":"')[1].split('"')[0])
        end_time_ms = int(driver.page_source.split('"endTimeMs":"')[1].split('"')[0])

        # closes the chromium instance
        driver.quit()

        # get non Clip url AFTER the driver has been closed
        original_video_url ="https://youtu.be/" + video_id

        start_time_sec, end_time_sec = start_time_ms / 1000, end_time_ms / 1000

        return original_video_url, start_time_sec, end_time_sec


    def trim_content(self, start_time_sec: float, end_time_sec: float) -> None:
        """Cuts the Video based on start_time_sec and end_time_sec"""
        video = moviepy.VideoFileClip(self.name_mp4)

        video = video.subclip(start_time_sec, end_time_sec)

        save_name = self.name + '_trim.mp4'
        video.write_videofile(save_name)
        video.close()


class MenuNav():
    """menu navigation that handles input"""
    def convert_existing_mp4(self, file_path: str, audio_type: str) -> None:
        """Split the total path into path and file"""
        # originally '/' which is how python gets the file location but now
        # it gets the file path with '\', so we search for that instead
        original_file_path, name_mp4 = file_path.rsplit('\\', 1)

        video_data = VideoData(name_mp4, original_file_path)
        video_data.convert_mp4(audio_type)
        video_data.clean_up()


    def download_yt_etc(self, url: str, name: str, file_format: str=None,
                        start_end: tuple[float, float] = (None, None)) -> bool:
        """File Name and Video URL"""
        start, end = start_end
        audio_only = file_format is not None
        clip = UrlValidation(url).is_clip

        audio_type = '.mp3' if file_format else '.wav'
        name_mp4 = name + '.mp4'

        video_data = VideoData(name_mp4)

        if None not in (start, end):
            is_downloaded = video_data.download_video(url, audio_only, audio_type)
            video_data.trim_content(start, end)
            clip = True
        elif clip:
            url, start, end = video_data.original_video_info(url)
            is_downloaded = video_data.download_video(url, audio_only, audio_type)
            video_data.trim_content(start, end)
        else:
            is_downloaded = video_data.download_video(url, audio_only, audio_type)

        video_data.clean_up(clip, audio_only)

        return is_downloaded


def main():
    """start local eel web server and expose PY functions to JS"""
    eel.init("web")


    @eel.expose
    def partial_validation_python(url: str) -> int:
        """Passes the url from JS to local validation function. Potentially unnecessary"""
        if url != '':
            try:
                UrlValidation(url).partial_validation()
                return 0
            except NonYoutubeUrlException:
                return -2
            except NonVideoUrlException:
                return -1
        else:
            return 1


    @eel.expose
    def download_video(url: str, file_name: str, file_format: str, start: float, end: float) -> int:
        """Passes JS args to local download function"""
        try:
            UrlValidation(url).full_url_validation()
        except VideoUnavailableException:
            return -1
        except InvalidUrlException:
            return -2

        if 'null' in (start, end):
            start, end = None, None

        return MenuNav().download_yt_etc(url, file_name, file_format, (start, end))


    @eel.expose
    def get_file_path() -> str:
        """Presents file explorer and return the filepath to JS"""
        root = Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        file = filedialog.askopenfile(mode='r', filetypes=[('MP4 Files', '*.mp4')])
        if file:
            filepath = os.path.abspath(file.name)

        return filepath


    @eel.expose
    def convert_file(file_path: str, audio_type: str) -> int:
        """Passes JS args to local Python conversion function"""
        MenuNav().convert_existing_mp4(file_path, audio_type)
        return 0

    # starts chrome
    # can add params like port, host, mode, size,
    eel.start("index.html")


if __name__ == '__main__':
    main()
