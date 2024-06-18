"""
1. Call getSources to get sources
2. Call getAnswer & getSimilarQuestions in parallel
"""

import asyncio
import os
import requests
import json
from pydantic import BaseModel, ValidationError
from typing import List
from dotenv import load_dotenv
from together import Together
from bs4 import BeautifulSoup
from dotenv import load_dotenv

client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


# Define the schema using Pydantic
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
        cleaned_content = (
            parsed_content.strip()
            .replace("\n" * 4, "\n\n\n")
            .replace("\n\n", " ")
            .replace(" " * 3, "  ")
            .replace("\t", "")
            .replace("\n\n\n", "\n")[:20000]
        )
        print("parsed:", source["url"])

        return {**source, "fullContent": cleaned_content}
    except Exception as e:
        print(f"Error parsing {source['name']}, error: {e}")
        return {**source, "fullContent": "not available"}


async def getSources(question: str):
    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY is required")

    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
        data=json.dumps({"q": question, "num": 6}),
    )

    response.raise_for_status()
    raw_json = response.json()

    try:
        data = SerperResponse.model_validate(raw_json)
    except ValidationError as e:
        print("JSON validation error:", e.json())
        raise

    results = [{"name": result.title, "url": result.link} for result in data.organic]
    print("===== Sources ======")
    for i, result in enumerate(results):
        print(f"Source {i + 1}:", f"{result['name']} [{result['url']}]")
    return results


async def getAnswer(question: str, sources: list[SourceType]):
    print("===== Answer ======")
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

    return response.choices[0].message.content.strip()


async def getSimilarQuestions(question: str):
    print("===== Similar Questions ======")
    print("Some similar qs here")


async def main():
    question = "fun things to do in NYC"
    sources = await getSources(question)
    answer = await getAnswer(question, sources)
    print("\n")
    print(answer)
    # await asyncio.gather(getAnswer(question, sources), getSimilarQuestions(question))


asyncio.run(main())
