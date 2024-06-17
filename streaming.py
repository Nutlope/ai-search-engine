"""
get the user's question
Run the next two functions in parallel:
  Function 1 (query for the sources + query for the answer)
  Function 2 (query for similar questions)

Wait until sources + similar_questions are done, then respond with a stream. The stream will start off with sources and similar_questions, but will be pumping out chunks for the answer.

Example response:

Answer:
  Start streaming...

Sources:
  - source1
  - source2
  - source3

Similar Questions:
  - question1
"""

import asyncio


async def main():
    # Get the user's question
    question = "Some question"

    # Create a stream
    # return_stream

    response = await asyncio.gather(
        getSourcesAndAnswer(question), getSimilarQuestions(question)
    )

    # Next step:
    # Create a stream
    # Write "a" to it
    # Await asyncio.sleep(1)
    # Write "b" to it
    # Close it

    # response will have [{ sources: [], answer_stream: stream}, { similar_questions_promise: Promise<[]>}]

    # 1. Write to our stream with whatever answer_stream gives us
    # e.g. return_stream.write("Answer: ")
    # e.g. return_stream.write(answer_stream.read())

    # 2. Keep doing that until answer_stream closes

    # 3. Write the all the sources (because we have them, since we had to wait for them to load) to our return_stream
    # e.g. return_stream.write("Sources: ")
    # e.g. return_stream.write(sources.map)

    # 4. Await similar_questions_promise to finish
    # let similar_questions = await similar_questions_promise

    # 5. Write the similar_questions to our return_stream
    # e.g. return_stream.write("Similar questions:")
    # e.g. return_stream.write(similar_questions)

    # 6. Close the return_stream


async def getSourcesAndAnswer():
    print("Fetching sources")
    await asyncio.sleep(2)

    # Start fetching Answer with stream: true
    # Return { sources: [], answer: stream }


async def getSimilarQuestions():
    print("Fetching similar questions...")
    await asyncio.sleep(2)

    # Return { similar_questions_promise: Promise<[]> }


asyncio.run(main())
