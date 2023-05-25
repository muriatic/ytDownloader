import unittest
import shutil
import os
import sys

sys.path.append('../ytDownloader')

import yt_downloader as ytD

error_partial_validation_urls = {
    ### partial validation urls:
    # non YouTube Url ... raises NonYouTubeUrlException
    'https://www.python.org/' : 'ytD.NonYoutubeUrlException',
    # non video url (channel url) ... raises NonVideoUrlException
    'https://www.youtube.com/@programmersarealsohuman5909' : 'ytD.NonVideoUrlException',
    # shortened YT url but no info
    'youtu.be' : 'ytD.NonVideoUrlException'
}

error_full_validation_urls = {
    ### full validation urls:
    # invalid url ... raises VideoUnavailableException
    'https://youtu.be/s7wLYzRJt32' : 'ytD.VideoUnavailableException',
    # 404 url ... raises InvalidUrlException
    'https://www.youtube.com/watch(123' :'ytD.InvalidUrlException'
}

validUrls = [
    # standard video w/ watch?v= and &ab_channel=
    'https://www.youtube.com/watch?v=s7wLYzRJt3s&ab_channel=Programmersarealsohuman',
    # standard video w/ watch?v= and w/o &ab_channel
    'https://www.youtube.com/watch?v=s7wLYzRJt3s',
    # short video url
    'https://youtu.be/s7wLYzRJt3s',
    # YT Shorts video url
    'https://www.youtube.com/shorts/W_tw5_WEHDU'
]

clip_url = 'https://www.youtube.com/clip/UgkxU2HSeGL_NvmDJ-nQJrlLwllwMDBdGZFs'

name = '__TEST__'
name_trim_mp4 = name + '_trim' + '.mp4'
name_mp4 = '__TEST__.mp4'

clip = True

test_video = 'https://www.youtube.com/watch?v=s7wLYzRJt3s&ab_channel=Programmersarealsohuman'

test_clip = 'https://www.youtube.com/clip/UgkxU2HSeGL_NvmDJ-nQJrlLwllwMDBdGZFs'

cwd = os.getcwd()


def filter_by_false(pair):
    key, value = pair
    if value == 'False':
        return True
    else:
        return False


def move_file(file_name):
    # testAssets directory
    file_name_path = '.tools/testAssets/' + file_name

    if os.path.isfile(file_name_path):
        shutil.copy(file_name_path, cwd)
    else:
        # if the file is not found in the testAssets folder, attempt to download it,
        # and place it in the testAssets folder
        print(file_name, "not found in /testAssets. Attempting to download the video")
        ytD.VideoData(file_name).download_video(test_video)
        shutil.copy(os.path.join(cwd, file_name), file_name_path)


## tests do not necessarily run in order so they should be standalone
class Testyt_downloader(unittest.TestCase):
    # runs at the very end
    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree("__pycache__")
            # os.remove
        except OSError:
            pass

        print("\nPASSED!!")

    def tearDown(self):
        try:
            if os.path.exists(name_mp4):
                os.remove(name_mp4)
            if os.path.exists(name_trim_mp4):
                os.remove(name_trim_mp4)
        except:
            pass


    def test_url_validation(self):
        # check that youtube urls that aren't video urls are stopped
        # check that youtube urls that aren't video urls are stopped
        # check if invalid youtube url that returns Video Unavailable is caught
        # check if page returns status code not 200 (example returns error code: 404)

        n = 0

        # test partial validation
        for url, value in error_partial_validation_urls.items():
            # convert it to an actual error message
            returnValue = eval(value)

            # print("Testing Url:", url, '\n')

            with self.assertRaises(returnValue):
                ytD.UrlValidation(url).partial_validation()
            print("\nPartial Validation Url Test", n, "PASSED!")
            n += 1

        n = 0
        # test full url validation
        for url, value in error_full_validation_urls.items():
            # convert it to an actual error message
            returnValue = eval(value)

            # print("Testing Url:", url, '\n')

            with self.assertRaises(returnValue):
                ytD.UrlValidation(url).full_url_validation()
            print("\nFull Validation Url Test", n, "PASSED!")
            n += 1



        # test standard YouTube video url
        # test standard YouTube video url less channel
        # test short video url
        # test YT Shorts video url

        n = 0
        for url in validUrls:
            # print("Testing Url:", url, '\n')
            # simply call the function, if any error occurs, we know it didn't work
            ytD.UrlValidation(url).partial_validation()

            print("\nValid Url Test", n, "PASSED!")
            n += 1

        # test if clip url is recognized
        self.assertEqual(ytD.UrlValidation(clip_url).is_clip, True)
        print("\nClip Test PASSED!")


    def test_download_video(self):
        for n, url in enumerate(validUrls):
            # print("Testing Url:", url, '\n')

            # downloads the video
            ytD.VideoData(name_mp4).download_video(url)

            # checks if the file was generated
            self.assertTrue(os.path.isfile(name_mp4))
            print("Download Test", n, "PASSED!\n")

            if os.path.exists(name_mp4):
                os.remove(name_mp4)

    def test_convert_mp4(self):
        # creates a space between the "." and the next line
        print("\n")
        # since we need an MP4 we will move one from the testAssets folder
        move_file(name_mp4)

        typesList = ['.mp3', '.wav']
        n = 0
        for type in typesList:
            # run as clip (means it needs to find 'name_trim.mp4')
            ytD.VideoData(name_mp4).convert_mp4(type, clip)

            # '_trim'

            file_name = name + '_trim' + type

            # checks if the file was generated
            self.assertTrue(os.path.isfile(file_name))
            print("convertMP4 Test", n, "PASSED!\n")
            n += 1

            if os.path.exists(file_name):
                os.remove(file_name)

            # run as normal video; simply dont have to send in clip because default is False
            ytD.VideoData(name_mp4).convert_mp4(type)

            # no suffix

            file_name = name + type

            # checks if the file was generated
            self.assertTrue(os.path.isfile(file_name))
            print("convertMP4 Test", n, "PASSED!\n")
            n += 1

            # delete MP3 and WAV
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_cleanUp(self):
        n = 0


        # move both
        move_file(name_mp4)
        move_file(name_trim_mp4)

        """NON CLIP VIDEO AND CONVERTING TO AUDIO"""
        ytD.VideoData(name_mp4).clean_up(False, True)

        # ensure original MP4 was removed
        self.assertFalse(os.path.isfile(name_mp4))

        # ensure it doesn't the clip which was outside of it's scope
        self.assertTrue(os.path.isfile(name_trim_mp4))
        print("cleanUp Test", n, "PASSED!\n")
        n += 1


        # move both even if they were already there
        move_file(name_mp4)
        move_file(name_trim_mp4)

        """NON CLIP VIDEO AND NOT CONVERTING TO AUDIO"""
        ytD.VideoData(name_mp4).clean_up(False, False)

        # ensure original MP4 is untouched
        self.assertTrue(os.path.isfile(name_mp4))

        # ensure it doesn't the clip which was outside of it's scope
        self.assertTrue(os.path.isfile(name_trim_mp4))
        print("cleanUp Test", n, "PASSED!\n")
        n += 1


        # move both even if they were already there
        move_file(name_mp4)
        move_file(name_trim_mp4)

        """CLIP VIDEO AND CONVERTING TO AUDIO"""
        ytD.VideoData(name_mp4).clean_up(True, True)

        # ensure original MP4 was deleted
        self.assertFalse(os.path.isfile(name_mp4))

        # ensure clip was deleted
        self.assertFalse(os.path.isfile(name_trim_mp4))
        print("cleanUp Test", n, "PASSED!\n")
        n += 1


        # move both even if they were already there
        move_file(name_mp4)
        move_file(name_trim_mp4)

        """CLIP VIDEO AND NOT CONVERTING TO AUDIO"""
        ytD.VideoData(name_mp4).clean_up(True, False)

        # ensure original MP4 was deleted
        self.assertFalse(os.path.isfile(name_mp4))

        # ensure clip was not deleted
        self.assertTrue(os.path.isfile(name_trim_mp4))
        print("cleanUp Test", n, "PASSED!\n")
        n += 1

    # need error handles for this???
    # maybe compare the sample to another video to check they are the same????
    def test_trim_content(self):
        video_data = ytD.VideoData(name_mp4)
        url, start, end = video_data.original_video_info(test_clip)

        self.assertEqual("https://youtu.be/NiXD4xVJM5Y", url)

        print("True Video Url Test PASSED!")

        video_data.download_video(url)

        video_data.trim_content(start, end)

        self.assertTrue(os.path.isfile(name_mp4))

        self.assertTrue(os.path.isfile(name_trim_mp4))

        print("Trimmed Video Download Test PASSED!")


if __name__ == '__main__':
    unittest.main(failfast=True)
