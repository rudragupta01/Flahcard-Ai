import streamlit as st
import os
import tempfile
import csv
import io
import random

st.set_page_config(
    page_title="FlashMind",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:           #FAF7F2;
    --bg-card:      #FFFFFF;
    --bg-warm:      #F5EFE6;
    --border:       #E8DDD0;
    --border-dark:  #C9B99A;
    --accent:       #C07B4A;
    --accent-soft:  #F0E0CC;
    --accent-hover: #A8622F;
    --green:        #4A7C5F;
    --green-soft:   #D6EDE1;
    --red:          #B85450;
    --red-soft:     #F5DADA;
    --text-primary: #2C1F0E;
    --text-secondary: #7A6248;
    --text-muted:   #B0967A;
    --radius-sm:    10px;
    --radius-md:    16px;
    --radius-lg:    24px;
    --shadow:       0 2px 12px rgba(100, 60, 20, 0.08);
    --shadow-md:    0 4px 24px rgba(100, 60, 20, 0.12);
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 5rem !important; max-width: 900px; }

.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 0 1.8rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}
.topbar-logo {
    font-family: 'Lora', serif; font-size: 1.3rem; font-weight: 600;
    color: var(--text-primary); letter-spacing: -0.02em;
}
.topbar-logo span { color: var(--accent); }
.topbar-tag {
    font-size: 0.72rem; color: var(--text-muted);
    background: var(--bg-warm); border: 1px solid var(--border);
    padding: 0.25rem 0.75rem; border-radius: 999px;
}
.page-title {
    font-family: 'Lora', serif; font-size: clamp(1.8rem, 4vw, 2.6rem);
    font-weight: 600; color: var(--text-primary); line-height: 1.25;
    margin: 0 0 0.6rem; letter-spacing: -0.02em;
}
.page-sub {
    color: var(--text-secondary); font-size: 1rem; line-height: 1.65;
    max-width: 480px; margin-bottom: 2.5rem;
}
[data-testid="stTabs"] [role="tablist"] {
    background: var(--bg-warm); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 4px; gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important; font-size: 0.88rem !important;
    padding: 0.45rem 1rem !important; transition: all 0.18s ease;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--bg-card) !important; color: var(--text-primary) !important;
    box-shadow: var(--shadow) !important;
}
.input-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 2rem; margin-top: 1rem; box-shadow: var(--shadow);
}
.section-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: var(--bg) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important; color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.95rem !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--border-dark) !important; box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: var(--bg) !important; border-color: var(--border) !important;
    color: var(--text-primary) !important; border-radius: var(--radius-sm) !important;
}
[data-testid="stFileUploader"] {
    background: var(--bg-warm) !important; border: 2px dashed var(--border-dark) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stSlider"] > div { accent-color: var(--accent) !important; }
[data-testid="stCheckbox"] { color: var(--text-secondary) !important; }
[data-testid="stWidgetLabel"] p, label { color: var(--text-secondary) !important; font-size: 0.88rem !important; }
.stButton > button {
    background: var(--accent) !important; color: white !important; border: none !important;
    border-radius: var(--radius-sm) !important; font-weight: 600 !important;
    font-size: 0.92rem !important; padding: 0.6rem 1.6rem !important;
    transition: all 0.18s ease !important; box-shadow: 0 2px 8px rgba(192, 123, 74, 0.25) !important;
}
.stButton > button:hover {
    background: var(--accent-hover) !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(192, 123, 74, 0.35) !important;
}
.btn-got-it button { background: var(--green) !important; box-shadow: 0 2px 8px rgba(74, 124, 95, 0.25) !important; }
.btn-got-it button:hover { background: #3a6349 !important; }
.btn-need-review button { background: var(--red) !important; box-shadow: 0 2px 8px rgba(184, 84, 80, 0.25) !important; }
.btn-need-review button:hover { background: #9e3f3b !important; }
[data-testid="stDownloadButton"] button {
    background: transparent !important; border: 1px solid var(--border-dark) !important;
    color: var(--text-secondary) !important; font-weight: 500 !important; box-shadow: none !important;
}
[data-testid="stDownloadButton"] button:hover { background: var(--bg-warm) !important; transform: none !important; }
[data-testid="stProgress"] > div > div { background: var(--accent) !important; border-radius: 999px !important; }
[data-testid="stProgress"] > div { background: var(--border) !important; border-radius: 999px !important; }
.flashcard {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.5rem 1.8rem;
    margin-bottom: 0.8rem; box-shadow: var(--shadow); transition: all 0.18s ease;
}
.flashcard:hover { border-color: var(--border-dark); box-shadow: var(--shadow-md); transform: translateY(-1px); }
.card-number { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem; }
.card-question { font-family: 'Lora', serif; font-size: 1.05rem; font-weight: 500; color: var(--text-primary); line-height: 1.55; margin-bottom: 0.9rem; }
.card-divider { height: 1px; background: var(--border); margin-bottom: 0.9rem; }
.card-answer-label { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.3rem; }
.card-answer { font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6; }
.study-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 3rem 2.5rem; text-align: center;
    box-shadow: var(--shadow-md); margin: 1rem 0 1.5rem;
}
.study-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 1rem; }
.study-question { font-family: 'Lora', serif; font-size: 1.4rem; font-weight: 500; color: var(--text-primary); line-height: 1.45; max-width: 560px; margin: 0 auto; }
.study-answer { font-size: 1rem; color: var(--text-secondary); max-width: 520px; margin: 0 auto; line-height: 1.7; }
.answer-box {
    background: var(--bg-warm); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.5rem 2rem; text-align: center; margin: 0.5rem 0 1.5rem;
}
.score-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 3rem 2rem; text-align: center;
    box-shadow: var(--shadow-md); margin-top: 1rem;
}
.score-number { font-family: 'Lora', serif; font-size: 4rem; font-weight: 600; color: var(--accent); line-height: 1; margin-bottom: 0.4rem; }
.score-label { color: var(--text-secondary); font-size: 1rem; }
.quiz-option button {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    color: var(--text-primary) !important; border-radius: var(--radius-sm) !important;
    font-weight: 400 !important; text-align: left !important; box-shadow: var(--shadow) !important;
}
.quiz-option button:hover { border-color: var(--border-dark) !important; background: var(--bg-warm) !important; transform: translateY(-1px) !important; }
.quiz-correct button { background: var(--green-soft) !important; border: 1px solid var(--green) !important; color: var(--green) !important; }
.quiz-wrong button { background: var(--red-soft) !important; border: 1px solid var(--red) !important; color: var(--red) !important; }
[data-testid="stAlert"] { background: var(--bg-warm) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; color: var(--text-secondary) !important; }
.gen-counter { font-family: 'Lora', serif; font-size: 2.5rem; font-weight: 600; text-align: center; color: var(--accent); }
.warm-divider { height: 1px; background: var(--border); margin: 2rem 0; }
.cards-header { display: flex; align-items: baseline; justify-content: space-between; margin: 2rem 0 1rem; }
.cards-title { font-family: 'Lora', serif; font-size: 1.2rem; font-weight: 600; color: var(--text-primary); }
.cards-badge { font-size: 0.75rem; color: var(--text-muted); background: var(--bg-warm); border: 1px solid var(--border); padding: 0.2rem 0.65rem; border-radius: 999px; }
#confetti-canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
function launchConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const colors = ['#C07B4A','#4A7C5F','#E8DDD0','#B85450','#F0E0CC','#7A6248'];
    const particles = Array.from({length: 70}, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height * 0.4,
        r: Math.random() * 5 + 3,
        color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 5,
        vy: Math.random() * -7 - 2,
        alpha: 1, rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 8
    }));
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.x += p.vx; p.y += p.vy; p.vy += 0.22;
            p.alpha -= 0.016; p.rotation += p.rotSpeed;
            if (p.alpha <= 0) return;
            ctx.save(); ctx.globalAlpha = p.alpha; ctx.fillStyle = p.color;
            ctx.translate(p.x, p.y); ctx.rotate(p.rotation * Math.PI / 180);
            ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 1.5); ctx.restore();
        });
        if (particles.some(p => p.alpha > 0)) requestAnimationFrame(draw);
        else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    draw();
}
document.addEventListener('click', function(e) {
    if (e.target && e.target.innerText && e.target.innerText.includes('Got it'))
        launchConfetti();
});
</script>
<canvas id="confetti-canvas"></canvas>
""", unsafe_allow_html=True)

# ── Imports ────────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import cm
from reportlab.lib import colors as rl_colors

from flashcard_generator import run_full_pipeline, generate_quiz, run_multi_pdf_pipeline
from youtube_loader import load_youtube
from rag_pipeline import load_embedding_model
from spaced_repetition import record_result, get_due_cards, get_box_summary

with st.spinner("Loading..."):
    load_embedding_model()

# ── PDF generator ──────────────────────────────────────────────────────────
def generate_pdf(cards):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=18, textColor=rl_colors.HexColor('#2C1F0E'), spaceAfter=6, fontName='Times-Bold')
    card_num_style = ParagraphStyle('CardNum', parent=styles['Normal'],
        fontSize=8, textColor=rl_colors.HexColor('#B0967A'), spaceAfter=4, fontName='Helvetica')
    question_style = ParagraphStyle('Question', parent=styles['Normal'],
        fontSize=12, textColor=rl_colors.HexColor('#2C1F0E'), spaceAfter=6, fontName='Times-Roman', leading=16)
    answer_label_style = ParagraphStyle('AnswerLabel', parent=styles['Normal'],
        fontSize=8, textColor=rl_colors.HexColor('#B0967A'), spaceAfter=3, fontName='Helvetica')
    answer_style = ParagraphStyle('Answer', parent=styles['Normal'],
        fontSize=11, textColor=rl_colors.HexColor('#7A6248'), spaceAfter=4, fontName='Times-Roman', leading=15)
    story = []
    story.append(Paragraph("FlashMind AI — Flashcards", title_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor('#E8DDD0')))
    story.append(Spacer(1, 0.4*cm))
    for i, card in enumerate(cards):
        source = f" · {card['source']}" if card.get('source') else ""
        story.append(Paragraph(f"CARD {i+1} OF {len(cards)}{source.upper()}", card_num_style))
        story.append(Paragraph(card['question'], question_style))
        story.append(Paragraph("ANSWER", answer_label_style))
        story.append(Paragraph(card['answer'], answer_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=rl_colors.HexColor('#E8DDD0')))
        story.append(Spacer(1, 0.4*cm))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ── Session state ──────────────────────────────────────────────────────────
for key, val in {
    "flashcards": [], "study_index": 0, "show_answer": False,
    "got_it": [], "need_review": [], "study_done": False,
    "quiz_questions": [], "quiz_index": 0, "quiz_score": 0,
    "quiz_done": False, "quiz_answer_shown": False, "quiz_selected": None,
    "study_started": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def reset_study():
    st.session_state.study_index = 0
    st.session_state.show_answer = False
    st.session_state.got_it = []
    st.session_state.need_review = []
    st.session_state.study_done = False

def reset_quiz():
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_done = False
    st.session_state.quiz_answer_shown = False
    st.session_state.quiz_selected = None

def reset_chromadb():
    from rag_pipeline import _store
    _store["chunks"] = []
    _store["embeddings"] = None
    _store["sources"] = []

def get_difficulty_hint(d):
    if d == "Easy":
        return "Focus on definitions, basic facts, and key terms. Questions should be straightforward fill-in or short recall."
    elif d == "Hard":
        return "Focus on application, inference, comparison, and analysis. Questions should challenge deeper understanding and critical thinking."
    return "Balance definition questions with conceptual 'why' and 'how' questions."

# ── Top bar ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">Flash<span>Mind</span></div>
    <div class="topbar-tag">AI study assistant</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<h1 class="page-title">Your personal<br>study companion.</h1>
<p class="page-sub">Drop in a PDF, paste some notes, or share a YouTube link — and get flashcards ready to study in seconds.</p>
""", unsafe_allow_html=True)

tab_gen, tab_study, tab_quiz = st.tabs(["✦  Generate", "○  Study", "◇  Quiz"])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — GENERATE
# ════════════════════════════════════════════════════════════════════
with tab_gen:
    input_tab_pdf, input_tab_text, input_tab_yt = st.tabs(["PDF", "Text", "YouTube"])

    with input_tab_pdf:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Drop your PDFs here (you can select multiple)", type=["pdf"], accept_multiple_files=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1: num_cards_pdf = st.slider("How many cards?", 5, 20, 10, key="slider_pdf")
        with col2: difficulty_pdf = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="diff_pdf")
        with col3: topic_pdf = st.text_input("Topic (optional)", placeholder="e.g. Neural Networks", key="topic_pdf")
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_files:
            st.markdown(f"<p style='color:var(--text-muted); font-size:0.85rem;'>{len(uploaded_files)} file(s) selected</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Generate flashcards →", key="gen_pdf"):
                reset_chromadb(); reset_study(); reset_quiz()
                progress_placeholder = st.empty()
                temp_paths = []
                try:
                    file_paths_with_names = []
                    for f in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(f.read())
                            temp_paths.append(tmp.name)
                            file_paths_with_names.append((tmp.name, f.name))
                    with st.spinner(f"Reading {len(uploaded_files)} PDF(s)..."):
                        if len(uploaded_files) == 1:
                            cards = run_full_pipeline(pdf_path=temp_paths[0],
                                topic=topic_pdf if topic_pdf.strip() else "key concepts",
                                num_cards=num_cards_pdf, difficulty_hint=get_difficulty_hint(difficulty_pdf))
                            for c in cards: c['source'] = uploaded_files[0].name
                        else:
                            cards = run_multi_pdf_pipeline(file_paths_with_names,
                                topic=topic_pdf if topic_pdf.strip() else "key concepts",
                                num_cards=num_cards_pdf, difficulty_hint=get_difficulty_hint(difficulty_pdf))
                    st.session_state.flashcards = cards
                    st.session_state.quiz_questions = []
                    st.session_state.study_started = False
                    import time
                    for i in range(1, len(cards) + 1):
                        progress_placeholder.markdown(f'<div class="gen-counter">{i} of {len(cards)} cards ready</div>', unsafe_allow_html=True)
                        time.sleep(0.07)
                    progress_placeholder.empty()
                    st.success(f"Done! {len(cards)} flashcards are ready.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                finally:
                    for p in temp_paths: os.unlink(p)

    with input_tab_text:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        text_input = st.text_area("Paste your notes here", height=200,
            placeholder="Lecture notes, book excerpts, articles — anything you want to learn from.")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1: num_cards_text = st.slider("How many cards?", 5, 20, 10, key="slider_text")
        with col2: difficulty_text = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="diff_text")
        with col3: topic_text = st.text_input("Topic (optional)", placeholder="e.g. Photosynthesis", key="topic_text")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate flashcards →", key="gen_text"):
            if not text_input.strip():
                st.warning("Paste some text first.")
            else:
                reset_chromadb(); reset_study(); reset_quiz()
                progress_placeholder = st.empty()
                try:
                    with st.spinner("Building your flashcards..."):
                        cards = run_full_pipeline(input_text=text_input,
                            topic=topic_text if topic_text.strip() else "key concepts",
                            num_cards=num_cards_text, difficulty_hint=get_difficulty_hint(difficulty_text))
                    st.session_state.flashcards = cards
                    st.session_state.quiz_questions = []
                    st.session_state.study_started = False
                    import time
                    for i in range(1, len(cards) + 1):
                        progress_placeholder.markdown(f'<div class="gen-counter">{i} of {len(cards)} cards ready</div>', unsafe_allow_html=True)
                        time.sleep(0.07)
                    progress_placeholder.empty()
                    st.success(f"Done! {len(cards)} flashcards are ready.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    with input_tab_yt:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        yt_url = st.text_input("YouTube link", placeholder="https://www.youtube.com/watch?v=...")
        translate_hindi = st.checkbox("Translate Hindi → English", value=False)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1: num_cards_yt = st.slider("How many cards?", 5, 20, 10, key="slider_yt")
        with col2: difficulty_yt = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="diff_yt")
        with col3: topic_yt = st.text_input("Topic (optional)", placeholder="e.g. Recursion", key="topic_yt")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate flashcards →", key="gen_yt"):
            if not yt_url.strip():
                st.warning("Paste a YouTube URL first.")
            else:
                reset_chromadb(); reset_study(); reset_quiz()
                progress_placeholder = st.empty()
                with st.spinner("Fetching transcript..."):
                    transcript, error, lang = load_youtube(yt_url, translate=translate_hindi)
                if error:
                    st.error(error)
                else:
                    st.info(f"Transcript found — language: {lang}")
                    try:
                        with st.spinner("Building your flashcards..."):
                            cards = run_full_pipeline(input_text=transcript,
                                topic=topic_yt if topic_yt.strip() else "key concepts",
                                num_cards=num_cards_yt, difficulty_hint=get_difficulty_hint(difficulty_yt))
                        st.session_state.flashcards = cards
                        st.session_state.quiz_questions = []
                        st.session_state.study_started = False
                        import time
                        for i in range(1, len(cards) + 1):
                            progress_placeholder.markdown(f'<div class="gen-counter">{i} of {len(cards)} cards ready</div>', unsafe_allow_html=True)
                            time.sleep(0.07)
                        progress_placeholder.empty()
                        st.success(f"Done! {len(cards)} flashcards are ready.")
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

    if st.session_state.flashcards:
        cards = st.session_state.flashcards
        st.markdown('<div class="warm-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="cards-header">
            <div class="cards-title">Your flashcards</div>
            <div class="cards-badge">{len(cards)} cards</div>
        </div>
        <p style="color:var(--text-muted); font-size:0.82rem; margin-bottom:1.2rem;">Click any card to see the answer</p>
        """, unsafe_allow_html=True)
        cards_html = ""
        for i, card in enumerate(cards):
            source_tag = f"<span style='color:var(--text-muted); font-weight:400;'> · {card['source']}</span>" if card.get('source') else ""
            cards_html += f"""
            <div class="flashcard">
                <div class="card-number">Card {i+1} of {len(cards)}{source_tag}</div>
                <div class="card-question">{card['question']}</div>
                <div class="card-divider"></div>
                <div class="card-answer-label">Answer</div>
                <div class="card-answer">{card['answer']}</div>
            </div>"""
        st.markdown(cards_html, unsafe_allow_html=True)
        pdf_data = generate_pdf(cards)
        st.download_button("↓ Download as PDF", data=pdf_data, file_name="flashcards.pdf", mime="application/pdf")

# ════════════════════════════════════════════════════════════════════
# TAB 2 — STUDY MODE
# ════════════════════════════════════════════════════════════════════
with tab_study:
    cards = st.session_state.flashcards
    if not cards:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📖</div>
            <div style="font-family: Lora, serif; font-size: 1.15rem; font-weight: 500; color: #2C1F0E; margin-bottom:0.4rem;">Nothing to study yet</div>
            <div style="font-size: 0.9rem; color: #7A6248;">Go to Generate, add some content, and come back here.</div>
        </div>""", unsafe_allow_html=True)
    elif not st.session_state.study_started:
        due_cards = get_due_cards(cards)
        box_summary = get_box_summary()
        mastered = box_summary.get(5, 0)
        st.markdown(f"""
        <div style="padding: 1.5rem 0;">
            <div style="font-family: Lora, serif; font-size: 1.2rem; font-weight: 500; color: #2C1F0E; margin-bottom:0.5rem;">{len(due_cards)} of {len(cards)} cards due for review</div>
            <div style="color: #7A6248; font-size: 0.9rem; margin-bottom: 1.5rem;">{mastered} cards mastered across all your sessions</div>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Study due cards ({len(due_cards)})", use_container_width=True, disabled=len(due_cards) == 0):
                st.session_state.flashcards = due_cards if due_cards else cards
                st.session_state.study_started = True
                reset_study(); st.rerun()
        with col2:
            if st.button("Study all cards", use_container_width=True):
                st.session_state.study_started = True
                reset_study(); st.rerun()
    elif st.session_state.study_done:
        got = len(st.session_state.got_it)
        total = got + len(st.session_state.need_review)
        pct = int((got / total) * 100) if total else 0
        emoji = "🎉" if pct == 100 else "👍" if pct >= 70 else "📚"
        st.markdown(f"""
        <div class="score-card">
            <div style="font-size:2rem; margin-bottom:0.8rem;">{emoji}</div>
            <div class="score-number">{pct}%</div>
            <div class="score-label">{got} of {total} cards — you got it</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.need_review:
            if st.button("Review weak cards again"):
                st.session_state.flashcards = st.session_state.need_review
                reset_study(); st.rerun()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to overview"):
                st.session_state.study_started = False; reset_study(); st.rerun()
        with col2:
            if st.button("Generate new cards"):
                st.session_state.flashcards = []; st.session_state.study_started = False
                reset_study(); st.rerun()
    else:
        idx = st.session_state.study_index
        card = cards[idx]
        total = len(cards)
        st.progress(idx / total)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="study-card">
            <div class="study-label">Question {idx + 1} of {total}</div>
            <div class="study-question">{card['question']}</div>
        </div>""", unsafe_allow_html=True)
        if not st.session_state.show_answer:
            if st.button("Show answer", use_container_width=True):
                st.session_state.show_answer = True; st.rerun()
        else:
            st.markdown(f"""
            <div class="answer-box">
                <div style="font-size:0.65rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:0.6rem;">Answer</div>
                <div class="study-answer">{card['answer']}</div>
            </div>""", unsafe_allow_html=True)
            col_got, col_review = st.columns(2)
            with col_got:
                st.markdown('<div class="btn-got-it">', unsafe_allow_html=True)
                if st.button("✓  Got it", use_container_width=True):
                    record_result(card['question'], card['answer'], correct=True)
                    st.session_state.got_it.append(card)
                    st.session_state.show_answer = False
                    if idx + 1 >= total: st.session_state.study_done = True
                    else: st.session_state.study_index += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_review:
                st.markdown('<div class="btn-need-review">', unsafe_allow_html=True)
                if st.button("↺  Need review", use_container_width=True):
                    record_result(card['question'], card['answer'], correct=False)
                    st.session_state.need_review.append(card)
                    st.session_state.show_answer = False
                    if idx + 1 >= total: st.session_state.study_done = True
                    else: st.session_state.study_index += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — QUIZ MODE
# ════════════════════════════════════════════════════════════════════
with tab_quiz:
    if not st.session_state.flashcards:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">✏️</div>
            <div style="font-family: Lora, serif; font-size: 1.15rem; font-weight: 500; color: #2C1F0E; margin-bottom:0.4rem;">No cards to quiz on</div>
            <div style="font-size: 0.9rem; color: #7A6248;">Generate flashcards first, then test yourself here.</div>
        </div>""", unsafe_allow_html=True)
    elif not st.session_state.quiz_questions:
        st.markdown("""
        <div style="padding: 2rem 0 1rem;">
            <div style="font-family: Lora, serif; font-size: 1.3rem; font-weight: 500; color: #2C1F0E; margin-bottom:0.4rem;">Ready to test yourself?</div>
            <div style="color: #7A6248; font-size: 0.95rem; margin-bottom: 1.5rem;">Each question has 4 options — one correct, three plausible wrong ones generated by AI.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Start quiz →", use_container_width=True):
            with st.spinner("Preparing your quiz..."):
                st.session_state.quiz_questions = generate_quiz(st.session_state.flashcards)
            reset_quiz(); st.rerun()
    elif st.session_state.quiz_done:
        total = len(st.session_state.quiz_questions)
        score = st.session_state.quiz_score
        pct = int((score / total) * 100)
        emoji = "🎉" if pct == 100 else "👍" if pct >= 70 else "📚"
        st.markdown(f"""
        <div class="score-card">
            <div style="font-size:2rem; margin-bottom:0.8rem;">{emoji}</div>
            <div class="score-number">{pct}%</div>
            <div class="score-label">{score} of {total} correct</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Retake quiz"): reset_quiz(); st.rerun()
        with col2:
            if st.button("New quiz"): st.session_state.quiz_questions = []; reset_quiz(); st.rerun()
    else:
        idx = st.session_state.quiz_index
        total = len(st.session_state.quiz_questions)
        q = st.session_state.quiz_questions[idx]
        st.progress(idx / total)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="study-card">
            <div class="study-label">Question {idx + 1} of {total}</div>
            <div class="study-question">{q['question']}</div>
        </div>""", unsafe_allow_html=True)
        if not st.session_state.quiz_answer_shown:
            for i, option in enumerate(q['options']):
                st.markdown('<div class="quiz-option">', unsafe_allow_html=True)
                if st.button(option, key=f"opt_{idx}_{i}", use_container_width=True):
                    st.session_state.quiz_selected = option
                    st.session_state.quiz_answer_shown = True
                    is_correct = (option == q['answer'])
                    record_result(q['question'], q['answer'], correct=is_correct)
                    if is_correct: st.session_state.quiz_score += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            selected = st.session_state.quiz_selected
            correct = q['answer']
            for option in q['options']:
                if option == correct:
                    st.markdown('<div class="quiz-correct">', unsafe_allow_html=True)
                    st.button(f"✓ {option}", key=f"res_{idx}_{option}", use_container_width=True, disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                elif option == selected:
                    st.markdown('<div class="quiz-wrong">', unsafe_allow_html=True)
                    st.button(f"✗ {option}", key=f"res_{idx}_{option}", use_container_width=True, disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="quiz-option">', unsafe_allow_html=True)
                    st.button(option, key=f"res_{idx}_{option}", use_container_width=True, disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if selected == correct: st.success("Correct!")
            else: st.error(f"The correct answer was: {correct}")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Next question →", use_container_width=True):
                st.session_state.quiz_answer_shown = False
                st.session_state.quiz_selected = None
                if idx + 1 >= total: st.session_state.quiz_done = True
                else: st.session_state.quiz_index += 1
                st.rerun()