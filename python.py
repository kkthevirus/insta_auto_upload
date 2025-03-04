# Import necessary libraries
import os
import re
import logging
import gdown
import shutil
import cv2
import numpy as np
import time
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from tqdm import tqdm
from instagrapi import Client
import mimetypes

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Define constants
TELEGRAM_BOT_TOKEN = ""
INSTAGRAM_USERNAME = "0"
INSTAGRAM_PASSWORD = "d"

# Helper functions
def extract_file_id(url):
    match = re.search(r"https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

async def download_file(url):
    file_id = extract_file_id(url)
    if not file_id:
        return None, "❌ Invalid Google Drive Link!"

    download_dir = os.getcwd()
    download_url = f"https://drive.google.com/uc?id={file_id}"
    temp_file = os.path.join(download_dir, file_id)

    try:
        output_file = gdown.download(download_url, temp_file, quiet=False)
        if not output_file:
            return None, "❌ Download failed!"

        final_file = os.path.join(download_dir, f"{file_id}.mp4")
        shutil.move(output_file, final_file)
        return final_file, None
    except Exception as e:
        return None, f"❌ Download failed: {str(e)}"

def process_clip(input_clip, output_folder, index):
    resized_clip = os.path.join(output_folder, f"resized_part-{index}.mp4")
    final_clip = os.path.join(output_folder, f"final_part-{index}.mp4")
    renamed_clip = os.path.join(output_folder, f"part-{index}.mp4")

    resize_video(input_clip, resized_clip)
    add_text_overlay(resized_clip, final_clip, f"Part-{index}")

    os.remove(input_clip)
    os.remove(resized_clip)
    os.rename(final_clip, renamed_clip)
    return renamed_clip

def split_and_process_video(input_video, output_folder, clip_duration=90):
    os.makedirs(output_folder, exist_ok=True)
    video = VideoFileClip(input_video)
    video_duration = video.duration
    num_clips = int(video_duration // clip_duration) + (1 if video_duration % clip_duration else 0)

    for i in tqdm(range(num_clips), desc="Processing Clips", unit="clip"):
        start_time = i * clip_duration
        end_time = min((i + 1) * clip_duration, video_duration)
        subclip = video.subclip(start_time, end_time)

        temp_path = os.path.join(output_folder, f"part-{i+1}.mp4")
        subclip.write_videofile(temp_path, codec="libx264", audio_codec="aac")
        process_clip(temp_path, output_folder, i+1)

    print("✅ Processing Completed!")

def resize_video(input_video, output_video):
    target_width, target_height = 1080, 1920
    video = VideoFileClip(input_video)
    original_width, original_height = video.size

    scale = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    resized_video = video.resize(newsize=(new_width, new_height))

    def add_padding(frame):
        padded_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        frame_resized = cv2.resize(frame, (new_width, new_height))
        padded_frame[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = frame_resized
        return padded_frame

    final_video = resized_video.fl_image(add_padding)
    final_video.write_videofile(output_video, fps=video.fps, codec="libx264", audio_codec="aac")

def add_text_overlay(input_video, output_video, text):
    video = VideoFileClip(input_video)
    txt_clip = TextClip(text, fontsize=70, color='white', font='Arial-Bold',
                        size=(1080, 100), method='caption', bg_color='black')
    y_offset = 250
    txt_clip = txt_clip.set_position(("center", y_offset)).set_duration(video.duration)
    final = CompositeVideoClip([video, txt_clip])
    final.write_videofile(output_video, codec="libx264", audio_codec="aac")

def upload_videos(video_folder):
    cl = Client()
    try:
        cl.load_settings("session.json")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings("session.json")
    except:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings("session.json")

    videos = sorted(
        [f for f in os.listdir(video_folder) if f.startswith("part-") and f.endswith(".mp4")],
        key=lambda x: int(re.search(r'part-(\d+)', x).group(1))
    )

    for video in videos:
        video_path = os.path.join(video_folder, video)
        part_number = int(re.search(r'part-(\d+)', video).group(1))
        caption = f"Part {part_number} of the series! 🎬🔥 #AutoUpload"

        try:
            print(f"📤 Uploading {video}...")
            cl.video_upload(video_path, caption=caption)
            print(f"✅ {video} uploaded successfully!")
            os.remove(video_path)
            print(f"🗑 {video} deleted successfully!")
            time.sleep(random.randint(600, 1800))
        except Exception as e:
            print(f"❌ Failed to upload {video}: {e}")

# Telegram bot handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 Send me a **Google Drive link**, and I'll download the file as .mp4!")

async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    file_path, error = await download_file(user_message)

    if error:
        await update.message.reply_text(error)
    else:
        await update.message.reply_text(f"✅ File downloaded: `{file_path}`", parse_mode="Markdown")
        output_folder = "reels"
        split_and_process_video(file_path, output_folder)
        await update.message.reply_text("✅ Video processing complete! Check the 'reels' folder.")
        upload_videos(output_folder)

# Main function
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
