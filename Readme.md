# Introduction #

_Youtube-upload_ is a command-line script that uploads videos to Youtube. If a video does not comply with Youtube limitations (<15mins for a normal user) you must split it before using ffmpeg or any other tool. _Youtube-upload_ should work on any platform (GNU/Linux, BSD, OS X, Windows, ...) that runs Python.

# Dependencies #

  * [python 2.6 or 2.7](http://www.python.org)
  * [python-gdata](http://code.google.com/p/gdata-python-client) (>= 1.2.4)

Note: You must have logged in at least once into your Youtube account prior to uploading any videos.

# Download & Install #

  * [Stable release](http://code.google.com/p/youtube-upload/downloads/list):

```
$ wget http://youtube-upload.googlecode.com/files/youtube-upload-VERSION.tgz
$ tar xvzf youtube-upload-VERSION.tgz
$ cd youtube-upload-VERSION
$ sudo python setup.py install
```

  * [From repository](http://code.google.com/p/youtube-upload/source/checkout):

```
$ svn checkout http://youtube-upload.googlecode.com/svn/trunk/ youtube-upload
$ cd youtube-upload
$ sudo python setup.py install
```

  * If you don't want (or you can't) install software on the computer, run it directly from sources:

```
$ cd youtube-upload-VERSION
$ python youtube_upload/youtube_upload.py ...
```

# Usage examples #

**Upload a video:**

```
$ youtube-upload --email=myemail@gmail.com --password=mypassword \
                 --title="A.S. Mutter" --description="A.S. Mutter plays Beethoven" \
                 --category=Music --keywords="mutter, beethoven" anne_sophie_mutter.flv
www.youtube.com/watch?v=pxzZ-fYjeYs
```

**Upload a video with a description from file (_description.txt_):**

```
$ youtube-upload --email=myemail@gmail.com --password=mypassword \
                 --title="A.S. Mutter" --description="$(< \description.txt)" \
                 --category=Music --keywords="mutter, beethoven" anne_sophie_mutter.flv
www.youtube.com/watch?v=pxzZ-fYjeYs
```

**Upload the video using the Youtube API:**

```
$ youtube-upload --api-upload [OTHER OPTIONS] file.flv
```

If you set explicitly the `--api-upload` options or `pycurl` isn't installed, the original Youtube API will be used to upload the video file. This method is not recommended because it does not shows the nice progressbar.

**Upload a splited video:**

```
$ youtube-upload [OPTIONS] --title="TITLE" video.part1.avi video.part2.avi
www.youtube.com/watch?v=pxzZ-fYjeYs # title: TITLE [1/2]
www.youtube.com/watch?v=pxzZ-fYsdff # title: TITLE [2/2]
```

**Add a video to a playlist:**

```
$ youtube-upload [OPTIONS] --add-to-playlist=http://gdata.youtube.com/feeds/api/playlists/7986C428284A40A1 http://www.youtube.com/watch?v=Zpqu97l3G1U
```

Note that the argument must be the video URL (not a local file) and the playlist is the URL of the feed (with no prefix "PL").

**Get available categories:**

```
$ youtube-upload --get-categories
Tech Education Animals People Travel Entertainment Howto Sports Autos Music News Games Nonprofit Comedy Film
```

**Split a video with _ffmpeg_**

Youtube currently limits videos to <2Gb and <15' for almost all users. You can use the Bash example script to split it before uploading:

```
$ bash examples/split_video_for_youtube.sh video.avi
video.part1.avi
video.part2.avi
video.part3.avi
```

**Upload videos with _curl_**

The script uses pycurl by default (when available) to upload the video, but if you need to tweak the upload parameters take a look at the Bash script included with the sources ([examples/upload\_with\_curl.sh](http://code.google.com/p/youtube-upload/source/browse/trunk/examples/upload_with_curl.sh)). This command, for example, would upload _somevideo.flv_ with a limit rate of 100KBytes:

```
$ youtube-upload --get-upload-form-info [OPTIONS] | bash examples/upload_with_curl.sh --limit-rate 100k
```

**Upload a non-public (private/unlisted) video:**

```
$ youtube-upload --private ...
```

```
$ youtube-upload --unlisted ...
```

**Get password from standard input**

```
$ cat password.txt | youtube-upload -p - ....
```

**Use a HTTP proxy**

Set environment variables **http\_proxy** and **https\_proxy**:

```
$ export http_proxy=http://user:password@host:port
$ export https_proxy=http://user:password@host:port
$ youtube-upload ....

```

**Update metadata (title or description).**

Set new title for video:

```
$ youtube-upload --email=EMAIL --password=PASSWORD --update-metadata --title "new title" www.youtube.com/watch?v=pxzZ-fYjeYs
```

# Caveats #

## Validate your credentials ##
Before you upload a video using the script, do it manually to make sure everything is ok (you have a valid user/password and an associated channel). See [issue57](https://code.google.com/p/youtube-upload/issues/detail?id=57) for more details.

## Using two-step verification ##

If you are using [two-step verification](https://support.google.com/accounts/answer/180744?hl=en) issue an application-specific password and use it in the script as if it was your real password. See [issue111](https://code.google.com/p/youtube-upload/issues/detail?id=111) for more details.

## Sign in using App Passwords ##

An App password is a 16-digit passcode that gives an app or device permission to access your Google Account. If you use 2-Step-Verification and are seeing a “password incorrect” error when trying to access your Google Account, an App password may solve the problem.

https://support.google.com/accounts/answer/185833?hl=en

## Progressbar ##

You need both packages **python-progressbar** and **pycurl** installed to see the progress bar when uploading a video.

# Feedback #

Use the [issues tracker](http://code.google.com/p/youtube-upload/issues/) to report bugs or suggest improvements.