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

load_dotenv()


async def getSources(question: str):
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY is required")

    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
        data=json.dumps({"q": question, "num": 6}),
    )

    response.raise_for_status()
    raw_json = response.json()

    # Define the schema using Pydantic
    class Result(BaseModel):
        title: str
        link: str

    class SerperResponse(BaseModel):
        organic: List[Result]

    # Validate the response
    try:
        data = SerperResponse.model_validate(raw_json)
    except ValidationError as e:
        print("JSON validation error:", e.json())
        raise

    results = [{"name": result.title, "url": result.link} for result in data.organic]
    print("===== Sources ======")
    for i, result in enumerate(results):
        print(f"Source {i + 1}:", f"{result['name']} [{result['url']}]")


async def getAnswer(question: str):
    print("===== Answer ======")
    print("Some answer here")


async def getSimilarQuestions(question: str):
    print("===== Similar Questions ======")
    print("Some similar qs here")


async def main():
    question = "fun things to do in NYC"
    await getSources(question)
    await asyncio.gather(getAnswer(question), getSimilarQuestions(question))


asyncio.run(main())
