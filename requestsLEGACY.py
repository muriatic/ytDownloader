class clippedContent():
    def __init__(self, link):
        print(link)
        self.r = requests.get(link)


    def originalVideoID(self):
        # get the source code
        source = str(self.r.content)

        print(str(self.r.content))
        print(self.r.status_code)

        # these are the endpoints in which the videoID is enclosed
        start = "\"videoDetails\":{\"videoId\":\""
        end = '\"'

        # gets everything right of videoDetails
        videoID = source.split(start)[1]

        # gets everything left of the quote
        videoID = videoID.split(end)[0]
        

        # trying to find the videoID which looks like this
        # "videoDetails":{"videoId":"NiXD4xVJM5Y"

        source = self.source

        originalVideoLink = "https://youtu.be/" + videoID

        return originalVideoLink
    

    def getClipStartAndEndPoint(self):
        # Trying to find a string formatted like this
        # "startTimeMs":"0","endTimeMs":"15000"}
        
        
        # cuts off startTimeMs, adds it back but gets everything right of it
        # try:
        source = str(self.r.content)

        start = "startTimeMs"
        end = "}"
        s = start + source.split(start)[1]
        
        # for some reason, the source code will sometimes just not get the info, IDK why; if that happens I will just repoll
        # except IndexError:
        #     self.getClipStartAndEndPoint()

        # cuts of the } sign but gets everything left of it
        s = s.split(end)[0]

        # remove unnecessary quotes
        s = s.replace('\"', '')

        # get startTimeMs and endTimeMs
        startTimeMs, endTimeMs = s.split(',')
        startTimeMs, endTimeMs = startTimeMs.split(':')[1], endTimeMs.split(':')[1]

        # return integer representation
        return int(startTimeMs), int(endTimeMs)
    

    def trimContent(self, name):
        startTimeMs, endTimeMs = self.getClipStartAndEndPoint()

        nameMP4 = name + '.mp4'

        startTimeSec, endTimeSec = startTimeMs / 1000, endTimeMs / 1000

        video = VideoFileClip(nameMP4)

        video = video.subclip(startTimeSec, endTimeSec)

        saveName = name + '_trim.mp4'

        video.write_videofile(saveName)