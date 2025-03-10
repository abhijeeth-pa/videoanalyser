import streamlit as st
import cv2
import google.generativeai as genai
import numpy as np
import tempfile
import shutil
import os

# Configure Google Gemini AI
genai.configure(api_key="AIzaSyChhQb_kDorVIfvz66u6gFO8EsOuYvzGag")
mymodel = genai.GenerativeModel("gemini-1.5-flash")
mychat = mymodel.start_chat()

st.title("🎥 Video Analyzer with AI")

# Initialize session state variables
if "cap" not in st.session_state:
    st.session_state.cap = None
if "output" not in st.session_state:
    st.session_state.output = None
if "recording" not in st.session_state:
    st.session_state.recording = False
if "video_path" not in st.session_state:
    st.session_state.video_path = "video.mp4"

# Start Recording
if st.button("🎬 Start Recording"):
    st.session_state.cap = cv2.VideoCapture(0)  # Open camera
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    st.session_state.output = cv2.VideoWriter(st.session_state.video_path, fourcc, 20.0, (640, 480))
    st.session_state.recording = True

# Stop Recording
if st.button("🛑 Stop Recording") and st.session_state.cap is not None:
    st.session_state.recording = False
    st.session_state.cap.release()
    st.session_state.output.release()
    st.session_state.cap = None
    st.session_state.output = None
    st.video(st.session_state.video_path)  # Display recorded video

# Display real-time video feed
stframe = st.empty()

if st.session_state.recording and st.session_state.cap is not None:
    while st.session_state.recording:
        ret, frame = st.session_state.cap.read()
        if not ret:
            break
        st.session_state.output.write(frame)
        stframe.image(frame, channels="BGR")  # Show video feed

# Process video with Gemini AI
question = st.text_input("💬 Ask AI about the video")

if question and st.button("🚀 Analyze"):
    try:
        # Save video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_video_path = temp_file.name

        shutil.move(st.session_state.video_path, temp_video_path)  # Move video safely

        # Extract a frame to send to Gemini AI
        cap = cv2.VideoCapture(temp_video_path)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame_path = "frame.jpg"
            cv2.imwrite(frame_path, frame)  # Save extracted frame

            # Upload extracted frame to Gemini AI
            myimage = genai.upload_file(frame_path)
            response = mychat.send_message([myimage, question])
            st.write("🤖 AI Response:", response.text)
        else:
            st.error("❌ Failed to extract a frame from the video.")

    except Exception as e:
        st.error(f"⚠️ An unexpected error occurred: {e}")
