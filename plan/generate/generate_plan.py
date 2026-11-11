from openai import OpenAI


def generate_lesson_plan(api_key:str):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )