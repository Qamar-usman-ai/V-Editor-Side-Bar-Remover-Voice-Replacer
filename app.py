import streamlit as st
import edge_tts
import asyncio
import os
import moviepy.editor as mp 
from moviepy.video.fx.all import crop

# Helper to generate English TTS
async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_path)

st.set_page_config(page_title="Tab Remover & Voiceover", layout="wide")
st.title("✂️ Screen Record: Tab & Header Remover")

uploaded_file = st.file_uploader("Upload your Screen Recording", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Save the file
    with open("temp_input.mp4", "wb") as f:
        f.write(uploaded_file.read())

    st.video("temp_input.mp4")
    
    script_text = st.text_area("Type English Voiceover Script:", "Here is the demonstration of my project without the browser tabs visible.")

    # SIDEBAR CONTROLS FOR TOP/BOTTOM
    st.sidebar.header("📏 Remove Bars (Vertical)")
    # Increase 'top_crop' to remove your browser tabs
    top_crop = st.sidebar.slider("Remove from Top (px)", 0, 500, 100)
    bottom_crop = st.sidebar.slider("Remove from Bottom (px)", 0, 500, 0)
    
    st.sidebar.header("↔️ Remove Bars (Horizontal)")
    left_crop = st.sidebar.slider("Remove from Left (px)", 0, 500, 0)
    right_crop = st.sidebar.slider("Remove from Right (px)", 0, 500, 0)

    if st.button("🚀 Clean Video & Add Voice"):
        with st.spinner("Processing... Clipping the top tabs now."):
            try:
                # 1. Load Video
                clip = mp.VideoFileClip("temp_input.mp4")
                w, h = clip.size
                
                # 2. CROP LOGIC
                # x1, y1 = Top Left corner
                # x2, y2 = Bottom Right corner
                # To remove tabs: y1 must be > 0
                final_x1 = left_crop
                final_y1 = top_crop
                final_x2 = w - right_crop
                final_y2 = h - bottom_crop

                cropped_clip = crop(clip, x1=final_x1, y1=final_y1, x2=final_x2, y2=final_y2)
                
                # 3. Voice Generation
                voice_path = "temp_voice.mp3"
                asyncio.run(generate_voice(script_text, voice_path))
                
                # 4. Sound Replacement
                new_audio = mp.AudioFileClip(voice_path)
                
                # Version-safe audio setting
                if hasattr(cropped_clip, 'with_audio'):
                    final_video = cropped_clip.with_audio(new_audio)
                else:
                    final_video = cropped_clip.set_audio(new_audio)
                
                # 5. Export
                output_name = "clean_video.mp4"
                final_video.write_videofile(output_name, codec="libx264", audio_codec="aac")
                
                st.success("Success! The tabs are gone.")
                st.video(output_name)
                
                with open(output_name, "rb") as f:
                    st.download_button("📥 Download Clean Video", f, "no_tabs_video.mp4")
                    
            except Exception as e:
                st.error(f"Error: {e}")
