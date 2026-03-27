import streamlit as st
import edge_tts
import asyncio
import os
import moviepy.editor as mp  # This works for most installations
from moviepy.video.fx.all import crop

# Helper to generate English TTS
async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_path)

st.set_page_config(page_title="Video Editor", layout="wide")
st.title("🎬 Screen Record Polisher")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Save the uploaded file locally
    with open("temp_input.mp4", "wb") as f:
        f.write(uploaded_file.read())

    st.video("temp_input.mp4")
    
    script_text = st.text_area("English Script for Voiceover:", "This is a polished screen recording with a new voice.")

    # Sidebar for adjustments
    st.sidebar.header("Crop Settings")
    left_crop = st.sidebar.slider("Crop Left (px)", 0, 800, 200)
    right_crop = st.sidebar.slider("Crop Right (px)", 0, 800, 200)

    if st.button("🚀 Process Video"):
        with st.spinner("Removing sidebars and adding voice..."):
            try:
                # 1. Load Video
                clip = mp.VideoFileClip("temp_input.mp4")
                w, h = clip.size
                
                # 2. Universal Crop (Works on old and new MoviePy)
                # x1=left, y1=top, x2=right, y2=bottom
                cropped_clip = crop(clip, x1=left_crop, y1=0, x2=w-right_crop, y2=h)
                
                # 3. Generate Audio
                voice_path = "temp_voice.mp3"
                asyncio.run(generate_voice(script_text, voice_path))
                
                # 4. Add Audio
                new_audio = mp.AudioFileClip(voice_path)
                
                # Compatibility check for setting audio
                if hasattr(cropped_clip, 'with_audio'):
                    final_clip = cropped_clip.with_audio(new_audio)
                else:
                    final_clip = cropped_clip.set_audio(new_audio)
                
                # 5. Save Output
                output_name = "final_video.mp4"
                final_clip.write_videofile(output_name, codec="libx264", audio_codec="aac", fps=24)
                
                st.success("Done!")
                st.video(output_name)
                
                with open(output_name, "rb") as f:
                    st.download_button("Download Polished Video", f, "final_output.mp4")
                    
            except Exception as e:
                st.error(f"Error occurred: {e}")
