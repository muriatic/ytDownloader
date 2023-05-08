# ytDownloader
YouTube Downloader and MP4 to MP3 Converter

## NOTE:
Ensure when you download pytube that you change *client='ANDROID'* to *client='WEB'* on line 78 of innertube.py:
```
def __init__(self, client='ANDROID', use_oauth=False, allow_cache=True):
```
https://github.com/pytube/pytube/blob/da3141f3d937459cd7cfd9180970b9ec1d14bb5e/pytube/innertube.py#L78

## ALSO:
Change *client='ANDROID_EMBED'* to *client='WEB_EMBED'* on line 253 of __main__.py:
```
client='ANDROID_EMBED',
```
https://github.com/pytube/pytube/blob/da3141f3d937459cd7cfd9180970b9ec1d14bb5e/pytube/__main__.py#L253
