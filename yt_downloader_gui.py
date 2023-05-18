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

        #check if it is a YouTube link
        if netloc not in ("www.youtube.com", "youtu.be", "youtube.com"):
            raise NonYoutubeLinkException(f"link {self.link} is not a YouTube address")

        # check if it is a traditional video
        # videos path start with /watch or nothing if the netloc is youtu.be
        if not (path.startswith("/watch") or path.startswith("/shorts")) and netloc != "youtu.be":
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


    def download_video(self, link) -> None:
        """Download the video"""
        download_link = link

        youtube = YouTube(download_link)

        video = youtube.streams.get_highest_resolution()
        video.download(filename=self.name_mp4)

        return True


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
        link_validation(link).full_link_validation()
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


    def convert_button(self, URL, file_name, start, end, custom_yes, custom_no):
        try:
            link_validation(URL).partial_validation()
        except NonYoutubeLinkException:
            return True
        except NonVideoLinkException:
            return True
        except InvalidLinkException:
            return True

        if '' not in (URL, file_name, start, end) and custom_yes:
            try:
                if int(start) < int(end):
                    return False
                else:
                    return True
            except ValueError:
                return True

        elif '' not in (URL, file_name) and custom_no:
            return False

        else:
            return True


    def create_window(self):
        buttonSize = (23,2)
        doubleButtonSize = (48,2)
        inputFieldSize1 = 30
        inputFieldSize2 = 5

        sg.set_options(font=("Courier New", 12))
        # sg.theme('SandyBeach')
        sg.ChangeLookAndFeel('Dark')
        # sg.theme_background_color('#FFFFFF')

        layout1 = [
            [
                sg.Text("What would you like to do?")
            ],
            [
                sg.Button("Convert MP4 to Audio", key='convertMP4', s=buttonSize),
                sg.Button("Download a YouTube Video", key='downloadYTVideo', s=buttonSize)
            ],
            [
                sg.Button("Exit", key='Exit', s=doubleButtonSize)
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
            [sg.Text("File Format: ")],
            [sg.Text("Custom Timestamps? ")],
            [sg.Text("Times: ", key='timeStamps')]
        ]

        col3_2_2 = [
            [
                sg.Column([
                    [sg.Radio("Yes", 'audioOnly', key='audioOnlyTrue', enable_events=True)],
                    [sg.Radio(".mp3", group_id="fileFormat", key='fileFormat1', default=True)],
                    [sg.Radio("Yes", 'customTimestamps', key="_CUSTOMTIMESTAMPSYES_", enable_events=True)],
                    [sg.Input("", disabled=True, key='timeStampsStart', size=inputFieldSize2, enable_events=True)]
                ]),
                sg.Column([
                    [sg.Radio("No", 'audioOnly', key='audioOnlyFalse', default=True, enable_events=True)],
                    [sg.Radio(".wav", group_id="fileFormat", key='fileFormat2', default=False)],
                    [sg.Radio("No", 'customTimestamps', key='_CUSTOMTIMESTAMPSNO_', enable_events=True, default=True)],
                    [sg.Input("", disabled=True, key='timeStampsEnd', size=inputFieldSize2, enable_events=True)]
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
            [sg.Button("Convert", key='Convert', disabled=True, s=doubleButtonSize)],
            [sg.Multiline("Downloaded Successfully", key='successMSG', s=doubleButtonSize, background_color='green', text_color='white', justification='c', visible=False)]
        ]

        layout = [
            [
                sg.Column(layout1, key='-home-', element_justification='center'), 
                sg.Column(layout2, visible=False, key='-convertMP4-', element_justification='center'),
                sg.Column(layout3, visible=False, key='-downloadYTVideo-', element_justification='center')
            ]
        ]

        window = sg.Window(title="ytDownloader", layout=layout, margins=(300, 200), resizable=True, finalize=True)

        layout = 1

        while True:
            event, values = window.read()
            print(event, values)
            if event == None or "Exit" in event:
                break

            for key in ['fileFormat1', 'fileFormat2']:
                window[key].update(disabled=(not values['audioOnlyTrue']))
                window[key].update(disabled=(values['audioOnlyFalse']))
                

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
                MenuNav().convert_existing_mp4(file_path=values['-FILEPATH-'], audio_type='.mp3')

            if event == '-convertToWAV-' and values['-FILEPATH-'] != '':
                MenuNav().convert_existing_mp4(file_path=values['-FILEPATH-'], audio_type='.wav')

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

            # check if the input is an integer and remove the non-integer values
            if event == 'timeStampsStart' and values['timeStampsStart'] and values['timeStampsStart'][-1] not in ('0123456789'):
                window['timeStampsStart'].update(values['timeStampsStart'][:-1])

            if event == 'timeStampsEnd' and values['timeStampsEnd'] and values['timeStampsEnd'][-1] not in ('0123456789'):
                window['timeStampsEnd'].update(values['timeStampsEnd'][:-1])

            window['Convert'].update(disabled=self.convert_button(values['URL'], values['fileName'], values['timeStampsStart'], values['timeStampsEnd'], values['_CUSTOMTIMESTAMPSYES_'], values['_CUSTOMTIMESTAMPSNO_']))

            for key in ['_CUSTOMTIMESTAMPSYES_', '_CUSTOMTIMESTAMPSNO_']:
                if values['URL'] != '':
                    try:
                        window['_CUSTOMTIMESTAMPSYES_'].update(disabled=link_validation(values['URL']).is_clip())
                        window['_CUSTOMTIMESTAMPSNO_'].update(disabled=link_validation(values['URL']).is_clip())
                    except:
                        pass

            if event == 'Convert':
                
                # check if they want custom time stamps
                if values['_CUSTOMTIMESTAMPSYES_']:
                    window['successMSG'].update(background_color='blue')
                    success = self.download_yt_etc(link=values['URL'], name=values['fileName'], audio_only=values['audioOnlyTrue'], file_format=values['fileFormat1'], start=values['timeStampsStart'], end=values['timeStampsEnd'])

                else: 
                    window['successMSG'].update(background_color='blue')
                    success = self.download_yt_etc(link=values['URL'], name=values['fileName'], audio_only=values['audioOnlyTrue'], file_format=values['fileFormat1'])

                if success:
                    window['successMSG'].update(visible=True, background_color='green')


        window.close()


if __name__ == '__main__':
    MenuNav().create_window()
