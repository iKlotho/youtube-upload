#!/usr/bin/python
#
# Youtube-upload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Youtube-upload is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Youtube-upload.  If not, see <http://www.gnu.org/licenses/>.

"""
Simple script to upload videos to Youtube.

Dependencies: python-gdata (>= 1.2.4)
"""

import os
import re
import sys
import urllib
import optparse
import itertools
import subprocess
from xml.etree import ElementTree

# python-gdata (>= 1.2.4)
import gdata.media
import gdata.geo
import gdata.youtube
import gdata.youtube.service

VERSION = "0.1"
DEVELOPER_KEY = "AI39si7iJ5TSVP3U_j4g3GGNZeI6uJl6oPLMxiyMst24zo1FEgnLzcG4iSE0t2pLvi-O03cW918xz9JFaf_Hn-XwRTTK7i1Img"

def debug(obj):
    """Write obj to standard error."""
    sys.stderr.write("--- " + str(obj) + "\n")
    sys.stderr.flush()

def run(command, inputdata=None, **kwargs):
    """Run a command and return standard output"""
    debug("run: %s" % " ".join(command))
    popen = subprocess.Popen(command, **kwargs)
    outputdata, errdata = popen.communicate(inputdata)
    return outputdata, errdata

def ffmpeg(*args):
    """Run ffmpeg command and return standard error output."""
    outputdata, errdata = run(["ffmpeg"] + list(args), stderr=subprocess.PIPE)
    return errdata

def get_video_duration(video_path):
    """Return video duration in seconds."""
    errdata = ffmpeg("-i", video_path)
    strduration = re.search(r"Duration:\s*(.*?),", errdata).group(1)
    return sum(factor*float(value) for (factor, value) in 
        zip((60*60, 60, 1), strduration.split(":")))

def split_video(video_path, length, max_size=None, chunk_rewind=0):
    """Split video in chunks and yield path of splitted videos."""
    total_duration = get_video_duration(video_path)
    if total_duration <= length and os.path.getsize(video_path) <= max_size:
        yield video_path
        return
    base, extension = os.path.splitext(os.path.basename(video_path))
    offset = 0
    debug("split_video: %s, total_duration=%02.f" % (video_path, total_duration))
    for index in itertools.count(1): 
        debug("split_video: index=%d, offset=%s" % (index, offset))
        output_path = "%s-%d.mkv" % (base, index)
        args = ["-y", "-i", video_path]
        if max_size:
            args += ["-fs", str(int(max_size))]
        args += ["-sameq", "-ss", str(offset), "-t", str(length), output_path]
        ffmpeg(*args)
        yield output_path
        duration = get_video_duration(output_path)
        if offset + duration >= total_duration:
            break 
        offset += duration - chunk_rewind

def split_youtube_video(video_path):
    """Split video to match Youtube restrictions (<100Mb and < 10mins)."""
    return split_video(video_path, 60*9, max_size=99e6, chunk_rewind=10)

class Youtube:
    """Interface the Youtube API."""        
    CATEGORIES_SCHEME = "http://gdata.youtube.com/schemas/2007/categories.cat"
    
    def __init__(self, developer_key, email, password, source=None, client_id=None):
        """Login and preload available categories."""
        service = gdata.youtube.service.YouTubeService()
        service.email = email
        service.password = password
        service.source = source
        service.developer_key = developer_key
        service.client_id = client_id
        service.ProgrammaticLogin()
        self.service = service
        self.categories = self.get_categories()
        
    def upload_video(self, path, title, description, category, keywords=None, location=None):
        """Upload a video to youtube along with some metadata."""
        assert self.service, "Youtube service object is not set"
        if category not in self.categories:
            valid = " ".join(self.categories.keys())
            raise ValueError("Invalid category '%s' (accepted: %s)" % (category, valid))
                 
        media_group = gdata.media.Group(
            title=gdata.media.Title(text=title),
            description=gdata.media.Description(description_type='plain', text=description),
            keywords=gdata.media.Keywords(text=", ".join(keywords or [])),
            category=gdata.media.Category(
                text=category,
                label=self.categories[category],
                scheme=self.CATEGORIES_SCHEME),
            player=None)
        if location:            
            where = gdata.geo.Where()
            where.set_location(location)
        else: 
            where = None
        video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group, geo=where)
        
        # Get response only as a way to validate meta-data
        post_url, token = self.service.GetFormUploadToken(video_entry)
        
        # To use a POST upload instead (shell example):
        # curl -F token=TOKEN file=@PATH_TO_VIDEO POST_URL         
        return self.service.InsertVideoEntry(video_entry, path)

    @classmethod
    def get_categories(cls):
        """Return categories dictionary with pairs (term, label)."""
        def get_pair(element):
            """Return pair (term, label) for a (non-deprecated) XML element."""
            if all(not(str(x.tag).endswith("deprecated")) for x in element.getchildren()):
                return (element.get("term"), element.get("label"))            
        xmldata = urllib.urlopen(cls.CATEGORIES_SCHEME).read()
        xml = ElementTree.XML(xmldata)
        return dict(filter(bool, map(get_pair, xml)))

    
def main_upload(arguments):
    """Upload video to Youtube."""
    usage = """Usage: %prog [OPTIONS] EMAIL PASSWORD FILE TITLE DESCRIPTION CATEGORY KEYWORDS

    Upload videos to youtube."""
    parser = optparse.OptionParser(usage, version=VERSION)
    parser.add_option('-c', '--get-categories', dest='get_categories',
          action="store_true", default=False, help='Show categories')
    parser.add_option('-s', '--split-only', dest='split_only',
          action="store_true", default=False, help='Show videos without uploading them')
    options, args = parser.parse_args(arguments)
    
    if options.get_categories:
        print " ".join(Youtube.get_categories().keys())
        return 0    
    if options.split_only:
        video_path, = args
        for path in split_youtube_video(video_path):
            print path
        return 0    
    elif len(args) != 7:
        parser.print_usage()
        return 1
    
    email, password, video_path, title, description, category, skeywords = args    
    yt = Youtube(DEVELOPER_KEY, email, password)
    keywords = filter(bool, re.split('[,;\s]+', skeywords))
    videos = list(split_youtube_video(video_path))
    for index, splitted_video_path in enumerate(videos):
        if len(videos) > 1:
            complete_title = "%s [%d/%d]" % (title, index+1, len(videos))
        else:
            complete_title = title
        entry = yt.upload_video(splitted_video_path, complete_title, 
            description, category, keywords)
        url = entry.GetHtmlLink().href.replace("&feature=youtube_gdata", "")
        print url
   
if __name__ == '__main__':
    sys.exit(main_upload(sys.argv[1:]))
