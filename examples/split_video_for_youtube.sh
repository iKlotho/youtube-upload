#!/bin/bash
set -e

debug() { 
  echo "$@" >&2 
}

# Returns duration (in seconds) of video using ffmpeg.
# $1: video path
get_video_duration() {
  read H M S DS < \
    <(ffmpeg -i "$1" 2>&1 | 
      grep -m1 "^[[:space:]]*Duration:" | 
      cut -d":" -f2- | 
      cut -d"," -f1 | 
      sed "s/[:\.]/ /g")
  echo $((H*3600 + M*60 + S))      
}

# Main

VIDEO=$1
CHUNK_DURATION=900

EXTENSION=${VIDEO##*.}
BASENAME=$(basename "$VIDEO" ".$EXTENSION")
DURATION=$(get_video_duration "$VIDEO")

if test $DURATION -le $CHUNK_DURATION; then
  debug "no need to split, $DURATION <= $CHUNK_DURATION"
  echo "$VIDEO"
  exit 0
fi

debug "input file: $VIDEO ($DURATION seconds)"
seq 0 $CHUNK_DURATION $DURATION | cat -n | while read INDEX OFFSET; do
  debug "$VIDEO: from position $OFFSET take $CHUNK_DURATION seconds"
  OUTPUT_FILE="${BASENAME}.part${INDEX}.avi"
  # using "-vcodec copy" I get unplayable videos, why?  
  ffmpeg -v 1 -i "$VIDEO" -ss $OFFSET -t $CHUNK_DURATION -sameq \
         -y "$OUTPUT_FILE" </dev/null 
  echo "$OUTPUT_FILE"
done
