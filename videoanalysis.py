import streamlit as st
import google.generativeai as genai
import tempfile
import os
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

# Configure Google Gemini AI
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your actual API key
mymodel = genai.GenerativeModel("gemini-1.5-flash")
mychat = mymodel.start_chat()

st.title("🎥 Video Analyzer with AI")

# Initialize session state
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "video_frames" not in st.session_state:
    st.session_state.video_frames = []  # Store video frames for saving

# Upload Video Option
video_file = st.file_uploader("📂 Upload a video", type=["mp4"])

if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        st.session_state.video_path = temp_video.name

    st.video(st.session_state.video_path)  # Display uploaded video

# Live Recording (Works in Deployed Environments)
st.subheader("📹 Record Video (Cloud-Compatible)")

# Function to store recorded frames
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")  # Convert to NumPy array
    st.session_state.video_frames.append(img)  # Save frame
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="video_recorder",
    mode=WebRtcMode.SENDRECV,  # Enables proper recording
    media_stream_constraints={"video": True, "audio": False},  # Video only
    video_frame_callback=video_frame_callback,
)

# ✅ Save recorded video once recording stops
if not webrtc_ctx.state.playing and len(st.session_state.video_frames) > 0:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_recorded_video:
        import cv2
        height, width, _ = st.session_state.video_frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_recorded_video.name, fourcc, 20.0, (width, height))

        for frame in st.session_state.video_frames:
            out.write(frame)

        out.release()
        st.session_state.video_path = temp_recorded_video.name
        st.session_state.video_frames = []  # Reset frames after saving

if st.session_state.video_path:
    st.video(st.session_state.video_path)

# AI Video Analysis (Original Code Restored)
question = st.text_input("💬 Ask AI about the video")

if question and st.button("🚀 Analyze"):
    try:
        myvideo = genai.upload_file(st.session_state.video_path)

        # ✅ Ensure file is in ACTIVE state before analysis
        if myvideo.state != "ACTIVE":
            st.error("⚠️ File upload failed. Please try again.")
        else:
            response = mychat.send_message([myvideo, question])
            st.write("🤖 AI Response:", response.text)

    except Exception as e:
        st.error(f"⚠️ An unexpected error occurred: {e}")
