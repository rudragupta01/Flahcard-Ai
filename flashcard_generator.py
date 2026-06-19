import os
import re
from dotenv import load_dotenv
from groq import Groq
from rag_pipeline import (
    chunk_text, store_in_chromadb, retrieve_relevant_chunks,
    chunk_multiple_sources, store_tagged_chunks, retrieve_relevant_chunks_with_sources
)
from document_loader import load_pdf, load_text, load_multiple_pdfs

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_flashcards(context_chunks, num_cards=5, topic="general", difficulty_hint=""):
    context = "\n\n".join(context_chunks)
    difficulty_instruction = f"\nDifficulty guidance: {difficulty_hint}" if difficulty_hint else ""

    prompt = f"""You are a smart study assistant. Based ONLY on the text provided below, generate EXACTLY {num_cards} flashcards.

Each flashcard must follow this EXACT format with no deviation:
Q: [question here]
A: [answer here]

Rules:
- Generate EXACTLY {num_cards} flashcards, numbered internally is fine but always start lines with Q: and A:
- Every Q: must be immediately followed by its A: on the next line
- Answers must be single line only — no line breaks inside an answer
- Only use information from the provided text
- Cover different concepts — absolutely no repeated or similar questions
- Focus on topic: {topic}{difficulty_instruction}

Text:
{context}

Generate EXACTLY {num_cards} flashcards now:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def generate_quiz(flashcards):
    """Take existing flashcards and generate MCQ options for each."""
    quiz = []
    for card in flashcards:
        prompt = f"""You are a quiz generator. Given a question and its correct answer, generate 3 plausible but incorrect options.

Question: {card['question']}
Correct Answer: {card['answer']}

Generate exactly 3 wrong options that are plausible but clearly incorrect.
Format your response as exactly 3 lines, one wrong option per line, nothing else. No numbering, no labels.
Wrong options:"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = response.choices[0].message.content.strip()
        wrong_options = [line.strip() for line in raw.split('\n') if line.strip()][:3]

        while len(wrong_options) < 3:
            wrong_options.append("None of the above")

        import random
        options = wrong_options + [card['answer']]
        random.shuffle(options)

        quiz.append({
            'question': card['question'],
            'answer': card['answer'],
            'options': options
        })
    return quiz


def parse_flashcards(raw_text):
    flashcards = []
    lines = raw_text.strip().split('\n')
    current_q = None
    current_a_lines = []

    for line in lines:
        line = line.strip()
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        line = re.sub(r'^Q\d+:', 'Q:', line)
        line = re.sub(r'^A\d+:', 'A:', line)

        if line.startswith('Q:'):
            if current_q and current_a_lines:
                flashcards.append({
                    'question': current_q,
                    'answer': ' '.join(current_a_lines).strip()
                })
            current_q = line[2:].strip()
            current_a_lines = []

        elif line.startswith('A:'):
            current_a_lines = [line[2:].strip()]

        elif current_a_lines and line:
            current_a_lines.append(line)

    if current_q and current_a_lines:
        flashcards.append({
            'question': current_q,
            'answer': ' '.join(current_a_lines).strip()
        })

    return flashcards


def run_full_pipeline(input_text=None, pdf_path=None, topic="general", num_cards=5, difficulty_hint=""):
    if pdf_path:
        text = load_pdf(pdf_path)
    else:
        text = load_text(input_text)

    chunks = chunk_text(text, chunk_size=200, overlap=20)
    store_in_chromadb(chunks)

    n_chunks = min(num_cards + 4, 20)
    relevant_chunks = retrieve_relevant_chunks(topic, n_results=n_chunks)

    flashcards = []
    for attempt in range(5):
        raw_flashcards = generate_flashcards(relevant_chunks, num_cards, topic, difficulty_hint)
        flashcards = parse_flashcards(raw_flashcards)

        if len(flashcards) >= num_cards:
            return flashcards[:num_cards]

        print(f"[Attempt {attempt + 1}] Only got {len(flashcards)} cards, retrying...")

    if len(flashcards) < num_cards:
        shortfall = num_cards - len(flashcards)
        existing_questions = "\n".join(f"- {c['question']}" for c in flashcards)
        topup_prompt_chunks = relevant_chunks

        extra_raw = generate_flashcards(
            topup_prompt_chunks,
            num_cards=shortfall,
            topic=topic,
            difficulty_hint=difficulty_hint + f"\nDo NOT repeat these existing questions:\n{existing_questions}"
        )
        extra_cards = parse_flashcards(extra_raw)
        flashcards.extend(extra_cards)

    return flashcards[:num_cards]


# ════════════════════════════════════════════════════════════════════
# MULTI-PDF SUPPORT
# ════════════════════════════════════════════════════════════════════

def generate_flashcards_with_sources(context_items, num_cards=5, topic="general", difficulty_hint=""):
    """
    context_items: list of dicts [{"chunk": ..., "source": ...}, ...]
    Generates flashcards AND tags each one with its likely source filename.
    """
    context_text = "\n\n".join(
        f"[Source: {item['source']}]\n{item['chunk']}" for item in context_items
    )
    difficulty_instruction = f"\nDifficulty guidance: {difficulty_hint}" if difficulty_hint else ""

    prompt = f"""You are a smart study assistant. Based ONLY on the text provided below, generate EXACTLY {num_cards} flashcards.

Each flashcard must follow this EXACT format with no deviation:
Q: [question here]
A: [answer here]
SOURCE: [the filename from the [Source: ...] tag the answer came from]

Rules:
- Generate EXACTLY {num_cards} flashcards
- Every Q: must be followed by A: then SOURCE: on the next lines
- Answers must be single line only
- Only use information from the provided text
- Cover different concepts and different source documents where possible
- Focus on topic: {topic}{difficulty_instruction}

Text:
{context_text}

Generate EXACTLY {num_cards} flashcards now:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def parse_flashcards_with_sources(raw_text):
    flashcards = []
    lines = raw_text.strip().split('\n')
    current_q = None
    current_a_lines = []
    current_source = "unknown"

    for line in lines:
        line = line.strip()
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        line = re.sub(r'^Q\d+:', 'Q:', line)
        line = re.sub(r'^A\d+:', 'A:', line)

        if line.startswith('Q:'):
            if current_q and current_a_lines:
                flashcards.append({
                    'question': current_q,
                    'answer': ' '.join(current_a_lines).strip(),
                    'source': current_source
                })
            current_q = line[2:].strip()
            current_a_lines = []
            current_source = "unknown"

        elif line.startswith('A:'):
            current_a_lines = [line[2:].strip()]

        elif line.startswith('SOURCE:'):
            current_source = line[7:].strip()

        elif current_a_lines and line and not line.startswith('SOURCE'):
            current_a_lines.append(line)

    if current_q and current_a_lines:
        flashcards.append({
            'question': current_q,
            'answer': ' '.join(current_a_lines).strip(),
            'source': current_source
        })

    return flashcards


def run_multi_pdf_pipeline(file_paths_with_names, topic="general", num_cards=5, difficulty_hint=""):
    """
    file_paths_with_names: list of tuples (temp_file_path, original_filename)
    """
    sources = load_multiple_pdfs(file_paths_with_names)
    if not sources:
        return []

    tagged_chunks = chunk_multiple_sources(sources, chunk_size=200, overlap=20)
    store_tagged_chunks(tagged_chunks)

    n_chunks = min(num_cards + 4, 20)
    relevant_items = retrieve_relevant_chunks_with_sources(topic, n_results=n_chunks)

    flashcards = []
    for attempt in range(5):
        raw = generate_flashcards_with_sources(relevant_items, num_cards, topic, difficulty_hint)
        flashcards = parse_flashcards_with_sources(raw)

        if len(flashcards) >= num_cards:
            return flashcards[:num_cards]

        print(f"[Attempt {attempt + 1}] Only got {len(flashcards)} cards, retrying...")

    if len(flashcards) < num_cards:
        shortfall = num_cards - len(flashcards)
        existing_questions = "\n".join(f"- {c['question']}" for c in flashcards)
        extra_raw = generate_flashcards_with_sources(
            relevant_items,
            num_cards=shortfall,
            topic=topic,
            difficulty_hint=difficulty_hint + f"\nDo NOT repeat these existing questions:\n{existing_questions}"
        )
        extra_cards = parse_flashcards_with_sources(extra_raw)
        flashcards.extend(extra_cards)

    return flashcards[:num_cards]