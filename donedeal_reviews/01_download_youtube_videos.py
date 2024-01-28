import json
import os
from typing import List
from pytube import YouTube, exceptions
import moviepy.editor as mp

# Initialize an empty dictionary to store video details
video_dict_path = os.path.join("data", "video_dict.json")
if os.path.exists(video_dict_path):
    with open(video_dict_path, "r", encoding="utf-8") as json_file:
        video_dict = json.load(json_file)
else:
    video_dict = {}

# Create a data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")


def download_audio(video_ids: List[str]):
    for video_id in video_ids:
        is_in_dict = video_dict.get(video_id) is not None
        if is_in_dict and video_dict[video_id]["is_downloaded"] is True:
            print(f"Video id {video_id} has already been downloaded, skipping...")
            continue

        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            yt = YouTube(url)

            # Access and print metadata
            print(f"Title: {yt.title}")
            print(f"Author: {yt.author}")
            print(f"Thumbnail URL: {yt.thumbnail_url}")
            print(f"Channel ID:: {yt.channel_id}")
            print(f"Channel URL: {yt.channel_url}")

            # Store metadata in video_dict
            video_dict[video_id] = {
                "title": yt.title,
                "url": url,
                "thumbnail": yt.thumbnail_url,
                "author": yt.author,
                "channel_id": yt.channel_id,
                "channel_url": yt.channel_url,
            }

            # Try to get the mp4 audio stream
            audio_stream = yt.streams.filter(
                only_audio=True, file_extension="mp4"
            ).first()

            # Define the output path within the 'data' directory
            output_path = os.path.join("data", f"{video_id}")

            if audio_stream:
                # Download the mp4 audio stream
                audio_stream.download(
                    output_path=output_path, filename=f"{video_id}.mp4"
                )

                # Convert mp4 to mp3
                audio_clip = mp.AudioFileClip(
                    os.path.join(output_path, f"{video_id}.mp4")
                )
                audio_clip.write_audiofile(
                    os.path.join(output_path, f"{video_id}.mp3"), codec="mp3"
                )

                print(
                    f"MP4 audio downloaded and converted to mp3 for video id: {video_id}"
                )
            else:
                # If mp4 is not available, try webm
                audio_stream = yt.streams.filter(
                    only_audio=True, file_extension="webm"
                ).first()

                if audio_stream:
                    # Download the webm audio stream
                    audio_stream.download(
                        output_path=output_path, filename=f"{video_id}.webm"
                    )

                    # Convert webm to mp3
                    audio_clip = mp.AudioFileClip(
                        os.path.join(output_path, f"{video_id}.webm")
                    )
                    audio_clip.write_audiofile(
                        os.path.join(output_path, f"{video_id}.mp3"), codec="mp3"
                    )

                    print(
                        f"WebM audio downloaded and converted to mp3 for video id: {video_id}"
                    )
                else:
                    print(f"No audio stream found for video id: {video_id}")

                video_dict[video_id]["is_downloaded"] = True
        except (exceptions.PytubeError, OSError) as e:
            print(f"An error occurred while processing video id {video_id}: {e}")

    # Write video_dict to a JSON file within the 'data' directory
    with open(
        os.path.join("data", "video_dict.json"), "w", encoding="utf-8"
    ) as json_file:
        json.dump(video_dict, json_file)


# Read video IDs from a text file and store them in a list
with open("video_ids.txt", "r", encoding="utf-8") as file:
    video_ids_to_download = [line.strip() for line in file]

download_audio(video_ids_to_download)
