import scrapetube

videos = scrapetube.get_channel("UCNYw8CUPcrAEy9TbHV2Pr5A")

for video in videos:
    with open("video_ids.txt", "a", encoding="utf-8") as f:
        f.write(video["videoId"] + "\n")
