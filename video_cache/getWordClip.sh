word=$1
videoUrl=$(curl https://www.signingsavvy.com/search/$word -s | grep -oE "media(.*)\.mp4" | head -1)

if [ ! -z "$videoUrl" ]
then
    echo "Found Video"
    curl -L signingsavvy.com/$videoUrl --output $word.mp4
    echo $videoUrl
    ffmpeg -i "$word.mp4" -vf drawtext=": text="$word": fontcolor=white: fontsize=24: box=1: boxcolor=black@0.5: boxborderw=5: x=(w-text_w)/2: y=(h-text_h)/1.5" -codec:a copy "$word-withCaption.mp4" -y
else
    echo "Found Video Recursively"
    newUrl=$(curl https://www.signingsavvy.com/search/$word -s | grep -oP "sign\/$word\/\d*\/\d*" | head -1)
    echo $newUrl
    videoUrl=$(curl https://www.signingsavvy.com/$newUrl -s | grep -oE "media(.*)\.mp4" | head -1)
    echo $videoUrl
    curl -L signingsavvy.com/$videoUrl --output $word.mp4
    ffmpeg -i "$word.mp4" -vf drawtext=": text="$word": fontcolor=white: fontsize=24: box=1: boxcolor=black@0.5: boxborderw=5: x=(w-text_w)/2: y=(h-text_h)/1.5" -codec:a copy "$word-withCaption.mp4" -y
fi