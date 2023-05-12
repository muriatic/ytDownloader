import unittest
import shutil
import os
import sys

sys.path.append('../ytDownloader')

import ytDownloader as ytD

errorLinks_Responses = {
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
nameTrimMP4 = name + '_trim' + '.mp4'
nameMP4 = '__TEST__.mp4'

clip = True

testVideo = 'https://www.youtube.com/watch?v=s7wLYzRJt3s&ab_channel=Programmersarealsohuman'

testClip = 'https://www.youtube.com/clip/UgkxU2HSeGL_NvmDJ-nQJrlLwllwMDBdGZFs'

cwd = os.getcwd()


def filterByFalse(pair):
        key, value = pair
        if value == 'False':
            return True
        else:
            return False


def moveFile(fileName):
    # testAssets directory 
    fileName_Path = 'testAssets/' + fileName

    rawName = fileName.removesuffix('.mp4')

    if os.path.isfile(fileName_Path):
        shutil.copy(fileName_Path, cwd)
    else: 
        # if the file is not found in the testAssets folder, attempt to download it, 
        # and place it in the testAssets folder
        print(fileName, "not found in /testAssets. Attempting to download the video")
        ytD.functions.downloadVideo(testVideo, rawName)
        shutil.copy(os.path.join(cwd, fileName), fileName_Path)


## tests do not necessarily run in order so they should be standalone
class TestytDownloader(unittest.TestCase):
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
        if os.path.exists(nameMP4):
            os.remove(nameMP4)
        if os.path.exists(nameTrimMP4):
            os.remove(nameTrimMP4)

    def test_linkValidation(self):
        # check that youtube links that aren't video links are stopped
        # check that youtube links that aren't video links are stopped
        # check if invalid youtube link that returns Video Unavailable is caught
        # check if page returns status code not 200 (example returns error code: 404)
        
        n = 0
        for n in range(len(errorLinks_Responses)):
            # test for NonYoutubeLinkException converting the string to code with eval()
            # gets the items from the dict, converts it to a list, then accesses the nth couple and then the 1st or 2nd value
            
            link = (list(errorLinks_Responses.items())[n][0])
            returnValue = eval(list(errorLinks_Responses.items())[n][1])

            # print("Testing Link:", link, '\n')

            with self.assertRaises(returnValue):
                ytD.linkValidation(link)
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
            self.assertEqual(ytD.linkValidation(link), 
                                returnValue
                            )
            print("\nValid Link Test", n, "PASSED!")

    
    def test_downloadVideo(self):
        # creates a space between the "." and the next line
        print("\n")
        nameMP4 = name + '.mp4'

        # get just the list of valid links that DONT return True since those are clips and WONT be handled properly here
        validLinks = list(dict(filter(filterByFalse, validLinks_Results.items())).keys())


        n = 0
        for link in validLinks:
            # print("Testing Link:", link, '\n')
            
            # downloads the video
            ytD.functions.downloadVideo(link, name)

            # checks if the file was generated
            self.assertTrue(os.path.isfile(nameMP4))
            print("Download Test", n, "PASSED!\n")
            n += 1

    # def test_convertMP4(self):
    #     # creates a space between the "." and the next line
    #     print("\n")
    #     # since we need an MP4 we will move one from the testAssets folder
    #     moveFile(nameMP4)
        
    #     typesList = ['mp3', 'wav']
    #     n = 0
    #     for type in typesList:
    #         # run as clip (means it needs to find 'name_trim.mp4')
    #         ytD.functions.convertMP4(name, type, clip)
    #       # we know the suffix will be '_trim'
    #         suffix = '_trim'

    #         match type:
    #             case 'mp3':
    #                 fileName = name + suffix + ".mp3"
    #             case 'wav':
    #                 fileName = name + suffix + '.wav'

    #         # checks if the file was generated
    #         self.assertTrue(os.path.isfile(fileName))
    #         print("convertMP4 Test", n, "PASSED!\n")
    #         n += 1

    #         if os.path.exists(fileName):
    #             os.remove(fileName)

    #         # run as normal video; simply dont have to send in clip because default is False
    #         ytD.functions.convertMP4(name, type)
            
    #       # we know the suffix with be ''
    #         suffix = ''

    #         match type:
    #             case 'mp3':
    #                 fileName = name + suffix + ".mp3"
    #             case 'wav':
    #                 fileName = name + suffix + '.wav'

    #         # checks if the file was generated
    #         self.assertTrue(os.path.isfile(fileName))
    #         print("convertMP4 Test", n, "PASSED!\n")
    #         n += 1

    #         # delete MP3 and WAV
    #         if os.path.exists(fileName):
    #             os.remove(fileName)


    # def test_cleanUp(self):
    #     n = 0


    #     # move both 
    #     moveFile(nameMP4)
    #     moveFile(nameTrimMP4)

    #     """NON CLIP VIDEO AND CONVERTING TO AUDIO"""
    #     ytD.functions.cleanUp(name, False, True)

    #     # ensure original MP4 was removed
    #     self.assertFalse(os.path.isfile(nameMP4))

    #     # ensure it doesn't the clip which was outside of it's scope
    #     self.assertTrue(os.path.isfile(nameTrimMP4))
    #     print("cleanUp Test", n, "PASSED!\n")
    #     n += 1


    #     # move both even if they were already there
    #     moveFile(nameMP4)
    #     moveFile(nameTrimMP4)

    #     """NON CLIP VIDEO AND NOT CONVERTING TO AUDIO"""
    #     ytD.functions.cleanUp(name, False, False)

    #     # ensure original MP4 is untouched
    #     self.assertTrue(os.path.isfile(nameMP4))

    #     # ensure it doesn't the clip which was outside of it's scope
    #     self.assertTrue(os.path.isfile(nameTrimMP4))
    #     print("cleanUp Test", n, "PASSED!\n")
    #     n += 1


    #     # move both even if they were already there
    #     moveFile(nameMP4)
    #     moveFile(nameTrimMP4)

    #     """CLIP VIDEO AND CONVERTING TO AUDIO"""
    #     ytD.functions.cleanUp(name, True, True)
        
    #     # ensure original MP4 was deleted
    #     self.assertFalse(os.path.isfile(nameMP4))

    #     # ensure clip was deleted
    #     self.assertFalse(os.path.isfile(nameTrimMP4))
    #     print("cleanUp Test", n, "PASSED!\n")
    #     n += 1


    #     # move both even if they were already there
    #     moveFile(nameMP4)
    #     moveFile(nameTrimMP4)

    #     """CLIP VIDEO AND NOT CONVERTING TO AUDIO"""
    #     ytD.functions.cleanUp(name, True, False)

    #     # ensure original MP4 was deleted
    #     self.assertFalse(os.path.isfile(nameMP4))

    #     # ensure clip was not deleted
    #     self.assertTrue(os.path.isfile(nameTrimMP4))
    #     print("cleanUp Test", n, "PASSED!\n")
    #     n += 1

    # need error handles for this???
    # maybe compare the sample to another video to check they are the same????
    # def test_trimContent(self):
    #     _clipInstance = ytD.clippedContent(testClip)
    #     link = _clipInstance.originalVideoLink

    #     self.assertEqual("https://youtu.be/NiXD4xVJM5Y", link)

    #     print("True Video Link Test PASSED!")

    #     ytD.functions.downloadVideo(link, name)

    #     self.assertTrue(os.path.isfile(nameMP4))

    #     _clipInstance.trimContent(name)

    #     self.assertTrue(os.path.isfile(nameTrimMP4))

    #     print("Trimmed Video Download Test PASSED!")
        

if __name__ == '__main__':
    unittest.main()
