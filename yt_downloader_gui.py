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
import PySimpleGUI as sg




### END OF IMPORT ###

class InvalidLinkException(Exception):
    """Raised when YouTube returns a non-200 status code"""


class NonYoutubeLinkException(Exception):
    """Raised when the url is not YouTube"""


class VideoUnavailableException(Exception):
    """Raised when the YouTube video is unavailable or it is a non-video link"""


class NoMP4FilesToConvertException(Exception):
    """Raised when there are no MP4 files in the current directory"""


class EndBeforeStartException(Exception):
    """Raised when the end time is before the start time"""

# error handling
def show_exception_and_exit(exc_type, exc_value, tb_object):
    """Catches Exceptions and Prevents the App from Auto Closing"""
    traceback.print_exception(exc_type, exc_value, tb_object)
    input("Press ENTER to exit...")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit


def link_validation(link) -> bool:
    """Tests to make sure the link is valid and if successful, returns whether it is a clip"""
    parsed_url = urlparse(link)
    netloc = parsed_url.netloc
    path = parsed_url.path
    #check if it is a YouTube link
    if netloc not in ("www.youtube.com", "youtu.be", "youtube.com"):
        raise NonYoutubeLinkException(f"link {link} is not a YouTube address")

    request = requests.get(link, timeout=3)

    # check if it is a clip
    # clips path start with /clip
    if parsed_url.path.startswith("/clip"):
        return True

    # check if it is a traditional video
    # videos path start with /watch or nothing if the netloc is youtu.be
    if not (path.startswith("/watch") or path.startswith("/shorts")) and netloc != "youtu.be":
        raise VideoUnavailableException(f"{link} is a non-video YouTube link")

    # check if the video is available
    if "Video unavailable" in request.text:
        raise VideoUnavailableException(
            f"the YouTube video at: {link} is unavailable; please check that your link is correct")

    # check to see if YouTube returns a good status code (200)
    if request.status_code != 200:
        raise InvalidLinkException(f"link {link} returned Status Code {request.status_code}")

    return False


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

    def custom_timestamp(self, start, end) -> None:
        """Takes a custom timestamp and will cut accordingly"""


class Functions():
    """necessary Functions for downloading and converting the MP4s and cleaning up after"""
    # class videos():
    def __init__(self, nameMP4, original_file_path=None):
        self.name_mp4 = nameMP4
        self.name = nameMP4.removesuffix('.mp4')
        self.original_file_path = original_file_path


    def download_video(self, link) -> None:
        """Download the video"""
        download_link = link

        youtube = YouTube(download_link)

        print("Be patient. Downloading...")

        video = youtube.streams.get_highest_resolution()
        video.download(filename=self.name_mp4)

        print("Video Downloaded Successfully")


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
    """menu navigation with question poser and skeleton navs"""
    # def __init__(self):
    #     self.question_dictionary = {}
    #     self.question_dictionary["Codes"] = [
    #         'question_1', 'question_2_yes', 'question_2_no_1', 'question_2_no_2', 
    #         'question_2_no_3', 'question_2_no_3_1', 'question_2_no_3_2', 
    #         'question_2_no_4', 'question_3']
    #     self.question_dictionary["Question"] = [
    #         "Would you like to convert an existing MP4 to Audio? \n0. (Y)\n1. (N)\n", 
    #         "File Name: \n>>> ", "Video URL: \n>>> ", "File Name: \n>>> ", 
    #         "Would you like to cut the video? \n0. (Y)\n1. (N)\n", "Start Time (s): \n>>> ",
    #         "End Time (s): \n>>> ", "Audio Only ('Yes' or 'No'): \n", 
    #         "File Format: \n(0) .mp3 \n(1) .wav"]
    #     self.question_dictionary["Accepted Answers"] = [
    #         [['y', 'yes', '0'], ['n', 'no', '1']], False, False, False,
    #         [['yes', 'y', '1'], ['no', 'n', '0']], False, False,
    #         [['yes', 'y', '1'], ['no', 'n', '0']], [['0', '.mp3', 'mp3'], ['1', '.wav', 'wav']]]

    # def question_poser(self, question_code: str) -> any:
    #     """POSING QUESTIONS"""
    #     position = self.question_dictionary["Codes"].index(question_code)
    #     question = self.question_dictionary["Question"][position]

    #     response = ''

    #     answers = self.question_dictionary["Accepted Answers"][position]

    #     while True:
    #         response = input(question)

    #         # checks if the question has answers list, if not just returns the response;
    #         # NO need to run any of the logic again
    #         if not answers:
    #             return response

    #         try:
    #             int(response)
    #         except ValueError:
    #             response = response.lower()

    #         valid_response = any(response in i for i in answers)

    #         if valid_response:
    #             break

    #     if response in answers[0]:
    #         return True

    #     return False


    def question_3(self, name, link='', clip=False) -> None:
        """File Format: .mp3 or .wav"""
        # format_question = self.question_poser('question_3')

        audio_type = '.mp3'

        # if not format_question:
        #     audio_type = '.wav'

        if clip:
            clips_instance = ClippedContent(link)
            link = clips_instance.original_video_link
            Functions(name).download_video(link)
            clips_instance.trim_content(name)

        elif link != '':
            Functions(name).download_video(link)

        Functions(name).convert_mp4(audio_type, clip)


    def question_2_yes(self, file_path, audio_type) -> None:
        """File Name"""
        # split the total path into path and file 
        original_file_path, nameMP4 = file_path.rsplit('/', 1)

        Functions(nameMP4, original_file_path).convert_mp4(audio_type)
        # # get list of Files
        # list_of_files = []

        # for file in os.listdir():
        #     if file.endswith(".mp4"):
        #         list_of_files.append(file)

        # if len(list_of_files) == 0:
        #     dir_path = os.getcwd()
        #     raise NoMP4FilesToConvertException(
        #         f"there are no MP4 files available to be converted in the directory: [{dir_path}]")

        # print("Files in Directory:")
        # for count, file in enumerate(list_of_files):
        #     print(f"({count}) {file}")

        # name = self.question_poser(self.question_2_yes.__name__)

        # try to convert to Integer
        # try:
        #     position = int(name)
        #     file = list_of_files[position].removesuffix('.mp4')

        #     self.question_3(file)

        # # if integer conversion fails with ValueError
        # except ValueError:
        #     try:
        #         if name.endswith('.mp4'):
        #             name = name.removesuffix('.mp4')

        #         self.question_3(name)

        #     except FileNotFoundError:
        #         print(f"FileNotFoundError: file {name}.mp4 does not exist")


    def question_2_no(self) -> None:
        """File Name and Video URL"""
        link = self.question_poser('question_2_no_1')

        clip = link_validation(link)

        name = self.question_poser('question_2_no_2')

        audio_question = self.question_poser('question_2_no_4')

        custom = False

        if not clip : custom = self.question_poser('question_2_no_3')

        if custom:
            start = int(self.question_poser('question_2_no_3_1'))
            end = int(self.question_poser('question_2_no_3_2'))
            if start >= end:
                raise EndBeforeStartException(
                    f"your end time: {end}, is before your start time: {start}")

        if audio_question:
            self.question_3(name, link, clip)

            Functions(name).clean_up(clip)

        elif clip:
            clips_instance = ClippedContent(link)
            link = clips_instance.original_video_link
            Functions(name).download_video(link)
            clips_instance.trim_content(name)
            Functions(name).clean_up(clip, False)

        else:
            Functions(name).download_video(link)

        if custom:
            ClippedContent(link, custom).trim_content(name, start, end)
            Functions(name).clean_up(custom, False)


    def question_1(self) -> None:
        """Convert existing MP4?"""
        answer = self.question_poser('question_1')

        if answer:
            self.question_2_yes()
        else:
            self.question_2_no()


def create_window():
    buttonSize = (23,2)
    inputFieldSize1 = 30
    inputFieldSize2 = 5

    sg.set_options(font=("Courier New", 12))
    sg.theme('DarkTeal2')

    layout1 = [
        [
            sg.Text("What would you like to do?")
        ],
        [
            sg.Button("Convert MP4 to Audio", key='convertMP4', s=buttonSize),
            sg.Button("Download a YouTube Video", key='downloadYTVideo', s=buttonSize)
        ],
        [
            sg.Button("Exit", key='Exit', s=buttonSize)
        ]
    ]

    layout2 = [
        [
            sg.Text("Select a File to Convert: "),
            sg.Input(key='_FILEBROWSE_', enable_events=True, size=inputFieldSize1, disabled=True),
            sg.T(),
            sg.FileBrowse(target='_FILEBROWSE_', key='-FILEPATH-', file_types=(("MP4 Files", "*.mp4")))
        ],
        [
            sg.Button("Convert to MP3", key='-convertToMP3-', s=buttonSize, disabled=True),
            sg.Button("Convert to WAV", key='-convertToWAV-', s=buttonSize, disabled=True)
        ],
        [
            sg.Button("Back", key='Back', s=buttonSize),
            sg.Button("Exit", key='Exit', s=buttonSize)
        ]
    ]

    col3_1_1 = [
        [sg.Text("Video URL   >>>")],
        [sg.Text("File Name   >>>")]
    ]

    col3_1_2 = [
        [
            sg.Input(size=inputFieldSize1, key='URL', enable_events=True)
        ],
        [
            sg.Input(size=inputFieldSize1, key='fileName', enable_events=True)
        ]
    ]

    col3_2_1 = [
        [sg.Text("Audio Only? ")],
        [sg.Text("Custom Timestamps? ")],
        [sg.Text("Times: ", key='timeStamps')],
        [sg.Text("File Format: ")]
    ]

    col3_2_2 = [
        [
            sg.Column([
                [sg.Radio("Yes", 'audioOnly', key='audioOnly')],
                [sg.Radio("Yes", 'customTimestamps', key="_CUSTOMTIMESTAMPSYES_", enable_events=True)],
                [sg.Input("", disabled=True, key='timeStampsStart', size=inputFieldSize2, enable_events=True)],
                [sg.Radio(".mp3", "fileFormat", key='fileFormat', default=True)]
            ]),
            sg.Column([
                [sg.Radio("No", 'audioOnly', default=True)],
                [sg.Radio("No", 'customTimestamps', key='_CUSTOMTIMESTAMPSNO_', enable_events=True, default=True)],
                [sg.Input("", disabled=True, key='timeStampsEnd', size=inputFieldSize2, enable_events=True)],
                [sg.Radio(".wav", "fileFormat")]
            ])
        ]
    ]

    layout3 = [
        [sg.Column([
            [
                sg.Column(col3_1_1),
                sg.Column(col3_1_2)
            ],
            [
                sg.Column(col3_2_1),
                sg.Column(col3_2_2)
            ]
        ])],
        [sg.Column([[
            sg.Button("Back", key='Back', s=buttonSize),
            sg.Button("Exit", key='Exit', s=buttonSize)
        ]])],
        [sg.Button("Convert", key='convert', disabled=True)]
    ]

    layout = [
        [
            sg.Column(layout1, key='-home-', element_justification='center'), 
            sg.Column(layout2, visible=False, key='-convertMP4-', element_justification='center'),
            sg.Column(layout3, visible=False, key='-downloadYTVideo-', element_justification='center')
        ]
    ]

    window = sg.Window(title="ytDownloader", layout=layout, margins=(300, 200))

    layout = 1

    while True:
        event, values = window.read()
        print(event, values)
        if event == None or "Exit" in event:
            break
        
        if 'Back' in event:
            window['-convertMP4-'].update(visible=False)
            window['-downloadYTVideo-'].update(visible=False)
            window['-home-'].update(visible=True)


        if event == 'convertMP4':
            window['-home-'].update(visible=False)
            window['-convertMP4-'].update(visible=True) 
        
        if values['_FILEBROWSE_'] != '':
            window['-convertToMP3-'].update(disabled=False)
            window['-convertToWAV-'].update(disabled=False)

        if event == '-convertToMP3-' and values['-FILEPATH-'] != '':
            # NEED TO CHANGE __INIT__ to handle the FILE path, find nameMP4 and name
            MenuNav().question_2_yes(file_path=values['-FILEPATH-'], audio_type='.mp3')

        if event == '-convertToWAV-' and values['-FILEPATH-'] != '':
            MenuNav().question_2_yes(file_path=values['-FILEPATH-'], audio_type='.wav')

        if event == 'downloadYTVideo':
            window['-home-'].update(visible=False)
            window['-downloadYTVideo-'].update(visible=True)

        if values['_CUSTOMTIMESTAMPSYES_']:
            window['timeStamps'].update()
            window['timeStampsStart'].update(disabled=False)
            window['timeStampsEnd'].update(disabled=False)
            # disable convert until start and end is filled

        if values['_CUSTOMTIMESTAMPSNO_']:
            window['timeStamps'].update()
            window['timeStampsStart'].update(disabled=True)
            window['timeStampsEnd'].update(disabled=True)

        # maybe find an input field with only numbers
        if '' not in (values['URL'], values['fileName'], values['timeStampsStart'], values['timeStampsEnd']) and int(values['timeStampsStart']) < int(values['timeStampsEnd']):
            window['convert'].update(disabled=False)
        else:
            window['convert'].update(disabled=True)

        if event == 'convert':
            customTimeStamp = values['_CUSTOMTIMESTAMPSYES_']
            if '' not in (values['timeStampsStart'], values['timeStampsEnd']):
                start, end = values['timeStampsStart'], values['timeStampsEnd']
                # maybe send to the questions logic now??
                print("DO FUNCTION WITH: ", values['URL'], values['fileName'], values['audioOnly'], customTimeStamp, start, end, not values['fileFormat'])
            else: 

                print("DO FUNCTION WITH: ", values['URL'], values['fileName'], values['audioOnly'], customTimeStamp, not values['fileFormat'])

    window.close()


if __name__ == '__main__':
    create_window()
    # MenuNav().question_1()
