import streamlit as st
import edge_tts
import asyncio
import os
from moviepy import VideoFileClip
import moviepy.video.fx as fx  # Access crop via fx.crop
# Helper to generate English TTS
async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_path)

st.title("Video Editor & Voice Replacer")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

if uploaded_file:
    with open("temp_input.mp4", "wb") as f:
        f.write(uploaded_file.read())

    st.video("temp_input.mp4")

    if st.button("Process Video"):
        with st.spinner("Cropping and translating..."):
            # 1. Load and Crop
            clip = VideoFileClip("temp_input.mp4")
            (w, h) = clip.size
            
            # Example: Crop 200 pixels from left and right to remove bars
            # Adjust x1, y1, x2, y2 based on your specific sidebar width
            cropped_clip = crop(clip, x1=200, y1=0, x2=w-200, y2=h)
            
            # 2. Voice Overlay (Example Text)
            # In a full app, you might use Whisper to transcribe the original first
            en_text = "This is the updated English voiceover for your video."
            asyncio.run(generate_voice(en_text, "temp_voice.mp3"))
            
            # 3. Combine
            from moviepy.editor import AudioFileClip
            new_audio = AudioFileClip("temp_voice.mp3")
            final_clip = cropped_clip.set_audio(new_audio)
            
            final_clip.write_videofile("output.mp4", codec="libx264", audio_codec="aac")
            
            st.success("Done!")
            st.video("output.mp4")
            
            with open("output.mp4", "rb") as file:
                st.download_button("Download Edited Video", file, "edited_video.mp4")
