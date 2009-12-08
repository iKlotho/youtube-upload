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
import subprocess
from xml.etree import ElementTree

# python-gdata
import gdata.media
import gdata.geo
import gdata.youtube
import gdata.youtube.service

VERSION = "0.0.2"
DEVELOPER_KEY = 'AI39si7iJ5TSVP3U_j4g3GGNZeI6uJl6oPLMxiyMst24zo1FEgnLzcG4iSE0t2pLvi-O03cW918xz9JFaf_Hn-XwRTTK7i1Img'


def debug(obj):
    """Write obj to standard error"""
    sys.stderr.write("--- " + str(obj)+"\n")
    sys.stderr.flush()

def run(command, inputdata=None, **kwargs):
    """Run a command and return standard output"""
    debug(command)
    popen = subprocess.Popen(command, **kwargs)
    outputdata, errdata = popen.communicate(inputdata)
    return outputdata, errdata

def ffmpeg(*args):
    """Run ffmpeg command and return standard error output."""
    outputdata, errdata = run(["ffmpeg"] + list(args), stderr=subprocess.PIPE)
    return errdata

def split_video(video_path, length):
    """Split video in chunks (length seconds)."""
    errdata = ffmpeg("-i", video_path)
    strduration = re.search(r"Duration:\s+(.*?),", errdata, re.MULTILINE).group(1)
    duration = sum(factor*float(x) for (x, factor) in zip(strduration.split(":"), (60*60, 60, 1)))
    base, extension = os.path.splitext(os.path.basename(video_path))
    offsets = xrange(0, int(duration), length)
    if len(offsets) == 1:
        yield video_path 
    else:
        for index, offset in enumerate(offsets):
            output_path = "%s-%d%s" % (base, index+1, extension)
            ffmpeg("-y", "-i", video_path, "-sameq", "-ss", str(offset), 
                "-t", str(length), output_path)
            yield output_path

class Youtube:
    """Interface the Youtube API."""
        
    CATEGORIES_SCHEME = "http://gdata.youtube.com/schemas/2007/categories.cat"
    
    def __init__(self, email, password, source=None, client_id=None):
        """Login and preload available categories."""
        service = gdata.youtube.service.YouTubeService()
        service.email = email
        service.password = password
        service.source = source
        service.developer_key = DEVELOPER_KEY
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
        
        # Get response only as a validation mechanism
        post_url, token = self.service.GetFormUploadToken(video_entry)
        
        # If you want to use a POST upload instead:
        # curl -F token=token file=@file_to_send.avi post_url
         
        return self.service.InsertVideoEntry(video_entry, path)

    @classmethod
    def get_categories(cls):
        """Return categories dictionary with pairs (term, label)."""
        def _get_pair(element):
            if all(not(str(x.tag).endswith("deprecated")) for x in element.getchildren()):
                return (element.get("term"), element.get("label"))            
        xmldata = urllib.urlopen(cls.CATEGORIES_SCHEME).read()
        xml = ElementTree.XML(xmldata)
        return dict(filter(bool, map(_get_pair, xml)))

def main_upload(args):
    """Upload video to Youtube."""
    usage = """Usage: %prog [OPTIONS] EMAIL PASSWORD FILE TITLE DESCRIPTION CATEGORY KEYWORDS

    Upload videos to youtube."""
    parser = optparse.OptionParser(usage, version=VERSION)
    parser.add_option('-c', '--get-categories', dest='get_categories',
          action="store_true", default=False, help='Show categories')
    options, args0 = parser.parse_args(args)
    
    if options.get_categories:
        print " ".join(Youtube.get_categories().keys())
        return 0
    elif len(args0) != 7:
        parser.print_usage()
        return 1
    
    email, password, video_file, title, description, category, skeywords = args0    
    yt = Youtube(email, password)
    keywords = filter(bool, re.split('[,;\s]+', skeywords))
    videos = list(split_video(video_file, 60*9))
    for index, video_path in enumerate(videos):
        if len(videos) > 1:
            complete_title = "%s (%d/%d)" % (title, index+1, len(videos))
        else:
            complete_title = title
        entry = yt.upload_video(video_file, complete_title, description, category, keywords)
        url = entry.GetHtmlLink().href.replace("&feature=youtube_gdata", "")
        print url
   

if __name__ == '__main__':
    sys.exit(main_upload(sys.argv[1:]))
