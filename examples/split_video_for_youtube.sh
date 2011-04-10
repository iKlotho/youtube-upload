#!/bin/bash
#
# Split a video file suitable for standard users in Youtube (<15')
#
#   $ bash split_video_for_youtube.sh video.avi
#   video.part1.mkv
#   video.part2.mkv
#
#   $ youtube-upload [OPTIONS] video.part*.mkv
#

# Echo to standard error
debug() { 
  echo "$@" >&2 
}

# Returns duration (in seconds) of a video $1 (uses ffmpeg).
get_video_duration() {
  OUTPUT=$(ffmpeg2 -i "$1" -vframes 1 -f rawvideo -y /dev/null 2>&1) ||
    { debug -e "get_video_duration: error running ffmpeg:\n$OUTPUT"; return 1; }
  DURATION=$(echo "$OUTPUT" | grep -m1 "^[[:space:]]*Duration:" |
    cut -d":" -f2- | cut -d"," -f1 | sed "s/[:\.]/ /g") || 
    { debug -e "get_video_duration: error parsing duration:\n$OUTPUT"; return 1; }
  read HOURS MINUTES SECONDS DECISECONDS <<< "$DURATION"
  expr $HOURS \* 3600 + $MINUTES \* 60 + $SECONDS      
}

main() {
  set -e -u -o pipefail
  CHUNK_DURATION=$((60*15))
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
  debug "start  split: $VIDEO ($DURATION seconds)"
  seq 0 $CHUNK_DURATION $DURATION | cat -n | while read INDEX OFFSET; do
    debug "$VIDEO: from position $OFFSET take $CHUNK_DURATION seconds"
    OUTPUT_FILE="${BASENAME}.part${INDEX}.mkv"
    # If I use "-vcodec copy" I get unplayable videos, why?  
    ffmpeg -v 1 -sameq -vcodec copy -acodec copy "$@" \
           -i "$VIDEO" -ss $OFFSET -t $CHUNK_DURATION -y "$OUTPUT_FILE" </dev/null 
    echo "$OUTPUT_FILE"
  done
}

if test "$NOEXEC" != 1; then
  main "$@"
fi
