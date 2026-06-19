import os
import re
import time
import yt_dlp
import tempfile
import glob
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()
api_key = st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None
if not api_key:
    api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
SPAM_WORDS = [
    'subscribe', 'like', 'comment', 'share', 'notification',
    'bell icon', 'channel', 'video', 'watch', 'click',
    'सब्सक्राइब', 'लाइक', 'कमेंट', 'शेयर', 'चैनल',
    'instagram', 'facebook', 'twitter', 'telegram'
]

COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def clean_transcript(text):
    lines = text.split('.')
    cleaned = []
    for line in lines:
        line_lower = line.lower()
        is_spam = any(spam in line_lower for spam in SPAM_WORDS)
        is_short = len(line.split()) < 5
        if not is_spam and not is_short:
            cleaned.append(line)
    return '. '.join(cleaned)

def translate_to_english(text):
    words = text.split()
    chunks = [' '.join(words[i:i+800]) for i in range(0, len(words), 800)]
    translated = []

    for i, chunk in enumerate(chunks):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Translate the following Hindi text to English. Keep technical terms in English. Only return the translated text, nothing else.\n\nText: {chunk}"}]
            )
            translated.append(response.choices[0].message.content)

            # Avoid hammering Groq — wait between chunks
            if i < len(chunks) - 1:
                time.sleep(1.5)

        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                time.sleep(5)  # back off hard on rate limit
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": f"Translate the following Hindi text to English. Keep technical terms in English. Only return the translated text, nothing else.\n\nText: {chunk}"}]
                    )
                    translated.append(response.choices[0].message.content)
                except:
                    translated.append(chunk)  # fallback: keep original chunk
            else:
                raise e

    return ' '.join(translated)

def parse_vtt(content):
    content = re.sub(r'WEBVTT.*?\n', '', content)
    content = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}.*', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'^\d+$', '', content, flags=re.MULTILINE)
    content = re.sub(r'NOTE.*?\n', '', content)
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    return ' '.join(deduped)

def load_youtube(url, translate=False):
    video_id = extract_video_id(url)
    if not video_id:
        return None, "❌ Invalid YouTube URL.", None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            use_cookies = os.path.exists(COOKIES_PATH)

            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'hi'],
                'subtitlesformat': 'vtt',
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
            }

            if use_cookies:
                ydl_opts['cookiefile'] = COOKIES_PATH

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            vtt_files = glob.glob(os.path.join(tmpdir, '*.vtt'))

            if not vtt_files:
                return None, "❌ No subtitles/transcript found for this video. The video may have captions disabled.", None

            chosen_file = None
            language = 'unknown'

            for f in vtt_files:
                if '.en.' in f or f.endswith('.en.vtt'):
                    chosen_file = f
                    language = 'english'
                    break

            if not chosen_file:
                for f in vtt_files:
                    if '.hi.' in f or f.endswith('.hi.vtt'):
                        chosen_file = f
                        language = 'hindi'
                        break

            if not chosen_file:
                chosen_file = vtt_files[0]
                language = 'unknown'

            with open(chosen_file, 'r', encoding='utf-8') as f:
                raw_vtt = f.read()

            full_text = parse_vtt(raw_vtt)

            if not full_text or len(full_text.strip()) < 50:
                return None, "❌ Transcript was empty after processing. Try a different video.", None

            full_text = clean_transcript(full_text)

            if translate and language == 'hindi':
                full_text = translate_to_english(full_text)
                language = 'translated to english'

            return full_text, None, language

    except Exception as e:
        return None, f"❌ Error: {str(e)}", None