import os
from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


from intake.schemas.lesson_info_response import LessonInfoResponse
from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")


test_path = Path(__file__).parent / 'test_teacher.pdf'
extracted_text = extract_files([test_path])
chunks = []
for text in extracted_text:
    chunks.append(get_text_chunks(text))

materials_text = "\n\n--- фрагмент материала ---\n\n".join(
    chunk for file_chunks in chunks for chunk in file_chunks
)

#TODO: отбирать top-N чанков по релевантности

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",
)

messages: list[ChatCompletionMessageParam] = [
    {"role": "system", "content":
    """
        You are an assistant that prepares a structured lesson brief for an English teacher.
        
        You receive:
        1) teacher_description — free-text request
        2) materials — extracted text chunks from attached files
        
        Your job:
        - Understand what lesson the teacher wants
        - Use materials only as evidence
        - Do NOT write a full lesson plan with timed activities
        - Do NOT invent worksheet content that is not supported by materials
        - If information is missing, put null and ask clarifying questions
        - If a material has little/no usable text, mention that in warnings/missing_info
        
        
        Return ONLY valid JSON with these keys:
        {
          "goal": string,
          "topic": string | null,
          "cefr_level": "A1"|"A2"|"B1"|"B2"|"C1"|"C2"|null,
          "duration_minutes": number | null,
          "skills": string[],
          "lesson_type": "grammar"|"skills"|"exam_prep"|"revision"|"mixed"|"unclear",
          "language_focus": string[],
          "based_on_materials": string[],
          "assumptions": string[],
          "missing_info": string[],
          "clarifying_questions": string[],
          "readiness": "ready"|"needs_clarification"|"insufficient_input",
          "confidence": number
        }
        
    """},
    {"role": "user", "content":
    f"""
        teacher_description: 'Сделай бриф урока A1–A2 на 40–45 минут по was/were для Elementary.
                            Есть готовый worksheet: gap-fill, choose was/were, rewrite am/is/are → was/were.
                            Нужны цель урока, фокус грамматики и чего не хватает для полного плана.
                            Класс: дети 10–12 лет, 10 учеников.'
        pinned_material_chunks:
        {materials_text}
    """},
]

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=messages
)
lesson = LessonInfoResponse.model_validate_json(response.choices[0].message.content)
print(lesson)