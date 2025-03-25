import streamlit as st
import whisper

from googleapiclient.discovery import build
import os
import time

# 🔑 Google & YouTube API Credentials
GOOGLE_API_KEY = "AIzaSyCjOvC0gJbXRLipkHnbouVYREO5V5oHPjE"  # Replace with your API key
SEARCH_ENGINE_ID = "504a51815585741bf"  # Replace with your Custom Search Engine ID
YOUTUBE_API_KEY = "AIzaSyCE5Pbq3MqcFXeI4h23LTK7hSmeuYLr6o8"  # Replace with your YouTube API key

# 🎙 Load Whisper Model
import streamlit as st
import whisper

@st.cache_resource  # Load model once and reuse it
def load_whisper_model():
    return whisper.load_model("base")  # Use "base" or "tiny" to reduce memory

model = load_whisper_model()

@st.cache_data(ttl=3600)  # Cache results for 1 hour
def transcribe_audio(audio_path):
    return model.transcribe(audio_path)


# 🌟 Streamlit Page Config
st.set_page_config(page_title="AI Audio Search", layout="wide")
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #4CAF50;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        animation: fadeIn 1.5s ease-in-out;
    }
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #555;
        animation: slideUp 1.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# 🎯 Title & Description
st.markdown("<div class='title'>🔍 AI Audio Search</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload an audio file to transcribe and search its content on Google & YouTube</div>", unsafe_allow_html=True)

# 📂 Sidebar
st.sidebar.title("🎛 Options")
st.sidebar.write("Customize your experience.")

# 📥 Upload Audio File
audio_file = st.file_uploader("🎵 Upload an audio file", type=["mp3", "wav", "m4a"])

if audio_file:
    st.sidebar.success("✅ Audio file uploaded!")
    
    # 🎵 Save File Temporarily
    audio_path = "temp_audio." + audio_file.name.split(".")[-1]
    with open(audio_path, "wb") as f:
        f.write(audio_file.getbuffer())
    
    # ▶️ Play Uploaded Audio
    st.audio(audio_path, format="audio/mp3")
    
    # 📝 Transcription Animation
    with st.spinner("📝 Transcribing your audio..."):
        time.sleep(2)  # Fake loading effect
        result = model.transcribe(audio_path)
        transcription = result["text"]
    
    # 🎙 Display Transcription
    st.subheader("🎙 Transcription")
    st.info(transcription)

    # 🔍 Google Search Function (Using API)
    def google_search(query, num_results=10):
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(q=query[:100], cx=SEARCH_ENGINE_ID, num=num_results).execute()  # Google query limit
        return [item["link"] for item in result.get("items", [])]

    # 🔍 Fetch Google Search Results
    st.subheader("🌎 Google Search Results")
    google_results = google_search(transcription, num_results=10)

    # 🔄 Horizontal Scroll for Google Results
    st.markdown("""
        <style>
        .scroll-container {
            display: flex;
            overflow-x: auto;
            white-space: nowrap;
            gap: 10px;
            padding: 10px;
        }
        .scroll-container a {
            display: inline-block;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 10px;
            text-decoration: none;
            color: #007bff;
            font-size: 16px;
            min-width: 250px;
        }
        </style>
        <div class="scroll-container">
    """, unsafe_allow_html=True)

    for link in google_results:
        st.markdown(f"<a href='{link}' target='_blank'>{link}</a>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ▶️ YouTube Search Function
    def youtube_search(query, max_results=10):
        service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = service.search().list(q=query, part="snippet", maxResults=max_results, type="video")
        response = request.execute()
        return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in response.get("items", [])]

    # 🔍 Fetch YouTube Results
    youtube_results = youtube_search(transcription, max_results=10)
    st.subheader("🎥 YouTube Search Results")

    # 🔄 Horizontal Scroll for YouTube Results
    st.markdown("""
        <style>
        .youtube-scroll-container {
            display: flex;
            overflow-x: auto;
            white-space: nowrap;
            gap: 10px;
            padding: 10px;
        }
        .youtube-scroll-container iframe {
            border-radius: 10px;
            width: 300px;
            height: 200px;
        }
        </style>
        <div class="youtube-scroll-container">
    """, unsafe_allow_html=True)

    for video_url in youtube_results:
        video_id = video_url.split("v=")[-1]
        st.markdown(f"""
            <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 🎯 Direct YouTube Search Button
    youtube_search_url = f"https://www.youtube.com/results?search_query={'+'.join(transcription.split())}"
    st.markdown(f"""
        <div style="text-align:center; margin-top:20px;">
            <a href="{youtube_search_url}" target="_blank" style="font-size:18px; padding:10px 20px; background:#ff0000; color:white; text-decoration:none; border-radius:5px;">🎥 View Full Search Results</a>
        </div>
    """, unsafe_allow_html=True)

    # 🗑 Cleanup Temporary File
    os.remove(audio_path)
