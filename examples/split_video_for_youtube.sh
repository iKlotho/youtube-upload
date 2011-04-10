#!/bin/bash
#
# Split a video file suitable for standard users in Youtube (<15')
#
#   $ bash split_video_for_youtube.sh video.avi
#   video.part1.avi
#   video.part2.avi
#
#   $ youtube-upload [OPTIONS] video.part*.avi
#

# Echo to standard error
debug() { 
  echo "$@" >&2 
}

# Returns duration (in seconds) of a video $1 (uses ffmpeg).
get_video_duration() {
  local DURATION=$(ffmpeg -i "$1" 2>&1 |
    grep -m1 "^[[:space:]]*Duration:" |
    cut -d":" -f2- |
    cut -d"," -f1 |
    sed "s/[:\.]/ /g")
  read HOURS MINUTES SECONDS DECISECONDS <<< "$DURATION"
  expr $HOURS \* 3600 + $MINUTES \* 60 + $SECONDS      
}

main() {
  set -e
  CHUNK_DURATION=$((60*15))
  FFMPEG_DEFAULT_OPTIONS="-v 1 -sameq"

  if test $# -eq 0; then
    debug "Usage: $(basename $0) VIDEO [EXTRA_OPTIONS_FOR_FFMPEG]"
    exit 1
  fi

  VIDEO=$1
  shift 1

  DURATION=$(get_video_duration "$VIDEO")

  if test $DURATION -le $CHUNK_DURATION; then
    debug "no need to split, duartion $DURATION <= $CHUNK_DURATION"
    echo "$VIDEO"
    exit 0
  fi

  EXTENSION=${VIDEO##*.}
  BASENAME=$(basename "$VIDEO" ".$EXTENSION")           
  debug "start split: $VIDEO ($DURATION seconds)"
  seq 0 $CHUNK_DURATION $DURATION | cat -n | while read INDEX OFFSET; do
    debug "$VIDEO: from position $OFFSET take $CHUNK_DURATION seconds"
    OUTPUT_FILE="${BASENAME}.part${INDEX}.avi"
    # If I use "-vcodec copy" I get unplayable videos, why?  
    ffmpeg $FFMPEG_DEFAULT_OPTIONS "$@" -i "$VIDEO" -ss $OFFSET -t $CHUNK_DURATION \
           -y "$OUTPUT_FILE" </dev/null 
    echo "$OUTPUT_FILE"
  done
}

if test "$NOEXEC" != 1; then
  main "$@"
fi
