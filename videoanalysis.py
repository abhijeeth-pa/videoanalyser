import streamlit as st
import google.generativeai as genai
import tempfile
import os
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# Configure Google Gemini AI
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your actual API key
mymodel = genai.GenerativeModel("gemini-1.5-flash")
mychat = mymodel.start_chat()

st.title("🎥 Video Analyzer with AI")

# Initialize session state
if "video_path" not in st.session_state:
    st.session_state.video_path = None

# Upload Video Option
video_file = st.file_uploader("📂 Upload a video", type=["mp4"])

if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        st.session_state.video_path = temp_video.name

    st.video(st.session_state.video_path)  # Display uploaded video

# Live Recording Option (Works in Cloud)
st.subheader("📹 Record Video")

webrtc_ctx = webrtc_streamer(
    key="video_recorder",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=None,
    async_processing=True,
)

if webrtc_ctx.video_receiver:
    video_frames = webrtc_ctx.video_receiver.frames
    if video_frames:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_recorded_video:
            temp_recorded_video.write(video_frames[0].to_ndarray(format="bgr24").tobytes())
            st.session_state.video_path = temp_recorded_video.name

if st.session_state.video_path:
    st.video(st.session_state.video_path)

# AI Video Analysis
question = st.text_input("💬 Ask AI about the video")

if question and st.button("🚀 Analyze"):
    try:
        myvideo = genai.upload_file(st.session_state.video_path)  # Upload video
        response = mychat.send_message([myvideo, question])
        st.write("🤖 AI Response:", response.text)
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
