import streamlit as st
import edge_tts
import asyncio
import os
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.fx.all import crop

# Helper to generate English TTS
async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_path)

st.set_page_config(page_title="Pro Video Editor", layout="centered")
st.title("🎥 Screen Record Polisher")
st.subheader("Remove sidebars and replace voiceover")

uploaded_file = st.file_uploader("Upload your screen recording", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Save temp file
    with open("temp_input.mp4", "wb") as f:
        f.write(uploaded_file.read())

    st.video("temp_input.mp4")
    
    # Text Input for Voiceover
    script_text = st.text_area("Paste your English script here:", 
                               "Welcome to this tutorial. Today we are looking at this screen recording.")

    # Sidebar settings for cropping
    st.sidebar.header("Crop Settings")
    left_crop = st.sidebar.slider("Crop Left (pixels)", 0, 500, 200)
    right_crop = st.sidebar.slider("Crop Right (pixels)", 0, 500, 200)

    if st.button("🚀 Process & Enhance Video"):
        with st.spinner("Processing... This may take a minute."):
            try:
                # 1. Load Clip
                clip = VideoFileClip("temp_input.mp4")
                w, h = clip.size
                
                # 2. Apply Crop (Removes side bars)
                # x1, y1 is top-left | x2, y2 is bottom-right
                cropped_clip = crop(clip, x1=left_crop, y1=0, x2=w-right_crop, y2=h)
                
                # 3. Generate Voiceover
                voice_path = "temp_voice.mp3"
                asyncio.run(generate_voice(script_text, voice_path))
                
                # 4. Combine Audio and Video
                new_audio = AudioFileClip(voice_path)
                
                # Optional: Loop or trim audio to match video length
                if new_audio.duration > cropped_clip.duration:
                    new_audio = new_audio.subclip(0, cropped_clip.duration)
                
                final_clip = cropped_clip.set_audio(new_audio)
                
                # 5. Write Output
                output_file = "polished_video.mp4"
                final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)
                
                st.success("Video Polished Successfully!")
                st.video(output_file)
                
                with open(output_file, "rb") as file:
                    st.download_button("📥 Download Polished Video", file, "final_video.mp4")

            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Cleanup (Optional)
                if os.path.exists("temp_voice.mp3"): os.remove("temp_voice.mp3")
