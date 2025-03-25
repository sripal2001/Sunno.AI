import streamlit as st
import whisper
from googleapiclient.discovery import build
import os
import time

# 🌟 Streamlit Page Config (Must be first Streamlit command)
st.set_page_config(page_title="Sunno - AI Audio Search", layout="wide")

# 🔑 Google & YouTube API Credentials
GOOGLE_API_KEY = "AIzaSyCjOvC0gJbXRLipkHnbouVYREO5V5oHPjE"  
SEARCH_ENGINE_ID = "504a51815585741bf"  
YOUTUBE_API_KEY = "AIzaSyCE5Pbq3MqcFXeI4h23LTK7hSmeuYLr6o8" 

# 🎙 Load Whisper Model
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

@st.cache_data(ttl=3600)
def transcribe_audio(audio_path):
    return model.transcribe(audio_path)

# 🎯 Title & Description
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🎧 Sunno - AI-Powered Audio Search</h1>",
    unsafe_allow_html=True,
)
st.write("Upload an audio file to transcribe and search inside it.")
st.markdown("<div style='text-align: center;'>🔍 Search Google & YouTube</div>", unsafe_allow_html=True)

# 📂 Sidebar
st.sidebar.title("🔍 Sunno - AI Audio Search")
st.sidebar.write("Find words inside audio instantly.")

# 📥 Upload Audio File
uploaded_file = st.file_uploader("Upload your audio file for Sunno to process", type=["mp3", "wav", "mp4"])

if uploaded_file:
    st.sidebar.success("✅ Audio file uploaded!")

    # 🎵 Save File Temporarily
    audio_path = "temp_audio." + uploaded_file.name.split(".")[-1]
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # ▶️ Play Uploaded Audio
    st.audio(audio_path, format="audio/mp3")

    # 📝 Transcription
    with st.spinner("📝 Transcribing your audio..."):
        time.sleep(2)  # Fake loading effect
        result = model.transcribe(audio_path)
        transcription = result["text"]

    # 🎙 Display Transcription
    st.subheader("🎙 Transcription")
    st.info(transcription)

    # 🔍 Google Search Function
    def google_search(query, num_results=10):
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(q=query[:100], cx=SEARCH_ENGINE_ID, num=num_results).execute()
        return [item["link"] for item in result.get("items", [])]

    # 🔍 Fetch Google Search Results
    st.subheader("🌎 Google Search Results")
    google_results = google_search(transcription, num_results=10)

    for link in google_results:
        st.markdown(f"- 🔗 [Google Result]({link})", unsafe_allow_html=True)

    # ▶️ YouTube Search Function
    def youtube_search(query, max_results=10):
        service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = service.search().list(q=query, part="snippet", maxResults=max_results, type="video")
        response = request.execute()
        return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in response.get("items", [])]

    # 🔍 Fetch YouTube Results
    youtube_results = youtube_search(transcription, max_results=10)
    st.subheader("🎥 YouTube Search Results")

    for video_url in youtube_results:
        video_id = video_url.split("v=")[-1]
        st.markdown(
            f'<iframe width="300" height="200" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>',
            unsafe_allow_html=True,
        )

    # 🎯 Direct YouTube Search Button
    youtube_search_url = f"https://www.youtube.com/results?search_query={'+'.join(transcription.split())}"
    st.markdown(
        f'<div style="text-align:center; margin-top:20px;">'
        f'<a href="{youtube_search_url}" target="_blank" style="font-size:18px; padding:10px 20px; background:#ff0000; color:white; text-decoration:none; border-radius:5px;">🎥 View Full Search Results</a>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # 🗑 Cleanup Temporary File
    os.remove(audio_path)
