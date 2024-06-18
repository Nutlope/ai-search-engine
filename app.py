import asyncio
import os
import requests
import json
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from together import Together
from bs4 import BeautifulSoup

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

class SourceType(BaseModel):
    title: str
    link: str

class SerperResponse(BaseModel):
    organic: List[SourceType]

async def fetch_and_parse(source):
    try:
        response = requests.get(source["url"], timeout=1)
        response.raise_for_status()
        doc = BeautifulSoup(response.text, "html.parser")
        parsed_content = doc.get_text(strip=True)
        cleaned_content = parsed_content[:20000]
        return {**source, "fullContent": cleaned_content}
    except Exception as e:
        return {**source, "fullContent": "not available"}


async def getSources(question: str):
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
        data=json.dumps({"q": question, "num": 6}),
    )

    response.raise_for_status()
    raw_json = response.json()
    data = SerperResponse.model_validate(raw_json)

    results = [{"name": result.title, "url": result.link} for result in data.organic]
    print("===== Sources ======")
    for i, result in enumerate(results):
        print(f"Source {i + 1}:", f"{result['name']} [{result['url']}]")
    return results


async def getAnswer(question: str, sources: list[SourceType]):
    final_results = await asyncio.gather(*map(fetch_and_parse, sources))
    main_answer_prompt = f"""
    Given a user question and some context, please write a clean, concise and accurate answer to the question based on the context. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context when crafting your answer.

    Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

    Here are the set of contexts:
    {"".join([f"[[citation:{index}]] {result['fullContent']} " for index, result in enumerate(final_results)])}

    Remember, don't blindly repeat the contexts verbatim and don't tell the user how you used the citations – just respond with the answer. It is very important for my career that you follow these instructions. Here is the user question:
    """

    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": main_answer_prompt},
            {"role": "user", "content": question},
        ],
    )
    print("===== Answer ======", "\n")
    print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()


async def getSimilarQuestions(question: str):
    prompt = """
    You are a helpful assistant that helps the user to ask related questions, based on user's original question. Please identify worthwhile topics that can be follow-ups, and write 3 questions no longer than 20 words each. Please make sure that specifics, like events, names, locations, are included in follow up questions so they can be asked standalone. For example, if the original question asks about "the Manhattan project", in the follow up question, do not just say "the project", but use the full name "the Manhattan project". Your related questions must be in the same language as the original question. Please provide these 3 related questions as a JSON array of 3 strings. Do NOT repeat the original question. ONLY return the JSON array, I will get fired if you don't return JSON. Here is the user's original question:
    """
    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
    )
    print("===== Similar Questions ======")
    print(response.choices[0].message.content)
    return response.choices[0].message.content


async def main():
    question = "What are some fun things to do in San Francisco?"
    sources = await getSources(question)
    await asyncio.gather(getAnswer(question, sources), getSimilarQuestions(question))

asyncio.run(main())