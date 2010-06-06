#!/bin/bash
#
# This script is designed to be used with youtube-upload with option -u enabled:
#
# $ youtube-upload -u [ARGS] | upload_with_curl.sh
#
set -e

get_video_id() {
  grep "^Location: " | head -n1 | grep -o "id=[^&]\+" | cut -d"=" -f2-
}

while IFS="|" read FILE TOKEN POST_URL; do
  REDIRECT_URL="http://code.google.com/p/youtube-upload"
  VIDEO_ID=$(curl -i -F "token=$TOKEN" -F "file=@$FILE" \
    "$POST_URL?nexturl=$REDIRECT_URL" | get_video_id)
  echo "http://www.youtube.com/watch?v=$VIDEO_ID"
done
