import streamlit as st
import edge_tts
import asyncio
import os
# Updated imports for MoviePy 2.0+
from moviepy import VideoFileClip, AudioFileClip
from moviepy.video.fx import Crop

# Helper to generate English TTS
async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_path)

st.set_page_config(page_title="Video Polisher", layout="wide")
st.title("🎬 Professional Video & Voice Replacer")

uploaded_file = st.file_uploader("Upload your screen recording", type=["mp4", "mov", "avi"])

if uploaded_file:
    with open("temp_input.mp4", "wb") as f:
        f.write(uploaded_file.read())

    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Original Video")
        st.video("temp_input.mp4")

    # Settings
    script_text = st.text_area("English Voiceover Script:", "Hello! This is a high-quality voiceover for my screen recording.")
    
    st.sidebar.header("Crop Settings (Remove Sidebars)")
    left_crop = st.sidebar.number_input("Crop Left (px)", value=0)
    right_crop = st.sidebar.number_input("Crop Right (px)", value=0)

    if st.button("Generate Final Video"):
        with st.spinner("Processing video and voice..."):
            try:
                # 1. Load Clip
                clip = VideoFileClip("temp_input.mp4")
                w, h = clip.size
                
                # 2. Crop logic (MoviePy 2.0 syntax)
                # x1, y1 is top-left | x2, y2 is bottom-right
                cropped_clip = clip.effects.apply(Crop(x1=left_crop, y1=0, x2=w-right_crop, y2=h))
                
                # 3. Voiceover
                voice_path = "temp_voice.mp3"
                asyncio.run(generate_voice(script_text, voice_path))
                
                # 4. Attach Audio
                new_audio = AudioFileClip(voice_path)
                final_clip = cropped_clip.with_audio(new_audio)
                
                # 5. Export
                output_path = "final_polished_video.mp4"
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                
                with col2:
                    st.success("Processing Complete!")
                    st.video(output_path)
                    with open(output_path, "rb") as f:
                        st.download_button("Download Video", f, file_name="polished_video.mp4")

            except Exception as e:
                st.error(f"Error: {e}")
