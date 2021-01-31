#!/bin/bash
start=$SECONDS
input=$1
rm mylist.txt

while IFS= read -r line
do
  echo $line | sed 's/ //g' | sed 's/$/-withCaption.mp4/' | sed 's/^/file /' >> mylist.txt
  ./getWordClip.sh $line
done < "$input"

ffmpeg -f concat -safe 0 -i mylist.txt -c copy OUTPUT.mp4 -y

duration=$(( SECONDS - start ))
echo "This took "
echo $duration
echo "seconds to run."