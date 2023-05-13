import unittest
import shutil
import os
import sys

sys.path.append('../ytDownloader')

import yt_downloader as ytD

error_links_responses = {
    # non YouTube Link ... raises NonYouTubeLinkException
    'https://www.python.org/' : 'ytD.NonYoutubeLinkException',
    # channel link ... raises VideoUnavailableException
    'https://www.youtube.com/@programmersarealsohuman5909' : 'ytD.VideoUnavailableException',
    # invalid link ... raises VideoUnavailableException
    'https://youtu.be/s7wLYzRJt32' : 'ytD.VideoUnavailableException',
    # 404 link ... raises InvalidLinkException
    'https://www.youtube.com/watch(123' :'ytD.InvalidLinkException'
}

validLinks_Results = {
    # clip link ... returns True
    'https://www.youtube.com/clip/UgkxU2HSeGL_NvmDJ-nQJrlLwllwMDBdGZFs' : 'True',
    # standard video w/ watch?v= and &ab_channel= ... returns False
    'https://www.youtube.com/watch?v=s7wLYzRJt3s&ab_channel=Programmersarealsohuman' : 'False',
    # standard video w/ watch?v= and w/o &ab_channel ... returns False
    'https://www.youtube.com/watch?v=s7wLYzRJt3s' : 'False',
    # short video link ... returns False
    'https://youtu.be/s7wLYzRJt3s' : 'False',
    # YT Shorts video link ... returns False
    'https://www.youtube.com/shorts/W_tw5_WEHDU' : 'False'
}

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

    raw_name = file_name.removesuffix('.mp4')

    if os.path.isfile(file_name_path):
        shutil.copy(file_name_path, cwd)
    else: 
        # if the file is not found in the testAssets folder, attempt to download it, 
        # and place it in the testAssets folder
        print(file_name, "not found in /testAssets. Attempting to download the video")
        ytD.Functions(raw_name).download_video(test_video)
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
            
        

    def test_link_validation(self):
        # check that youtube links that aren't video links are stopped
        # check that youtube links that aren't video links are stopped
        # check if invalid youtube link that returns Video Unavailable is caught
        # check if page returns status code not 200 (example returns error code: 404)
        
        n = 0
        for n in range(len(error_links_responses)):
            # test for NonYoutubeLinkException converting the string to code with eval()
            # gets the items from the dict, converts it to a list, then accesses the nth couple and then the 1st or 2nd value
            
            link = (list(error_links_responses.items())[n][0])
            returnValue = eval(list(error_links_responses.items())[n][1])

            # print("Testing Link:", link, '\n')

            with self.assertRaises(returnValue):
                ytD.link_validation(link)
            print("\nInvalid Link Test", n, "PASSED!")


        # test clip link
        # test standard YouTube video link 
        # test standard YouTube video link less channel
        # test short video link
        # test YT Shorts video link

        n = 0 
        for n in range(len(validLinks_Results)):
            link = (list(validLinks_Results.items())[n][0])
            returnValue = eval(list(validLinks_Results.items())[n][1])

            # print("Testing Link:", link, '\n')
            self.assertEqual(ytD.link_validation(link), 
                                returnValue
                            )
            print("\nValid Link Test", n, "PASSED!")

    
    def test_download_video(self):
        # creates a space between the "." and the next line
        print("\n")
        name_mp4 = name + '.mp4'

        # get just the list of valid links that DONT return True since those are clips and WONT be handled properly here
        validLinks = list(dict(filter(filter_by_false, validLinks_Results.items())).keys())


        n = 0
        for link in validLinks:
            # print("Testing Link:", link, '\n')
            
            # downloads the video
            ytD.Functions(name).download_video(link)

            # checks if the file was generated
            self.assertTrue(os.path.isfile(name_mp4))
            print("Download Test", n, "PASSED!\n")
            n += 1

    def test_convert_mp4(self):
        # creates a space between the "." and the next line
        print("\n")
        # since we need an MP4 we will move one from the testAssets folder
        move_file(name_mp4)
        
        typesList = ['.mp3', '.wav']
        n = 0
        for type in typesList:
            # run as clip (means it needs to find 'name_trim.mp4')
            ytD.Functions(name).convert_mp4(type, clip)
            
            # '_trim'

            file_name = name + '_trim' + type

            # checks if the file was generated
            self.assertTrue(os.path.isfile(file_name))
            print("convertMP4 Test", n, "PASSED!\n")
            n += 1

            if os.path.exists(file_name):
                os.remove(file_name)

            # run as normal video; simply dont have to send in clip because default is False
            ytD.Functions(name).convert_mp4(type)
            
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
        ytD.Functions(name).clean_up(False, True)

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
        ytD.Functions(name).clean_up(False, False)

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
        ytD.Functions(name).clean_up(True, True)
        
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
        ytD.Functions(name).clean_up(True, False)

        # ensure original MP4 was deleted
        self.assertFalse(os.path.isfile(name_mp4))

        # ensure clip was not deleted
        self.assertTrue(os.path.isfile(name_trim_mp4))
        print("cleanUp Test", n, "PASSED!\n")
        n += 1

    # need error handles for this???
    # maybe compare the sample to another video to check they are the same????
    def test_trim_content(self):
        clip_instance = ytD.ClippedContent(test_clip)
        link = clip_instance.original_video_link

        self.assertEqual("https://youtu.be/NiXD4xVJM5Y", link)

        print("True Video Link Test PASSED!")

        ytD.Functions(name).download_video(link)

        self.assertTrue(os.path.isfile(name_mp4))

        clip_instance.trim_content(name)

        self.assertTrue(os.path.isfile(name_trim_mp4))

        print("Trimmed Video Download Test PASSED!")


if __name__ == '__main__':
    unittest.main(failfast=True)
