# AI search engine in 150 LOC

> An open source AI engine in 150 lines of Python. Rewrite of [TurboSeek](https://github.com/Nutlope/turboseek) (full-stack Next.js site).

## Running locally

1. Create an account at [Together AI](https://dub.sh/together-ai) for the LLM
2. Create an account at [SERP API](https://serper.dev/) for the search API
3. Clone the repo, rename `.example.env` to `.env`, and replace the API keys
4. Run `pip install -r requirements.txt` to install dependencies
5. Run `python app.py` to run the search engine

## How it works

1. Take in a user's question
2. Make a request to the Serper API to look up the top 6 results on Google
3. Scrape text from the 6 links bing sent back with BeautifulSoup
4. Make a request to Mixtral-8x7B with the user's question + scraped text from the links
5. Make another request to the LLM to come up with 3 related questions the user can follow up with

## Future tasks

- [ ] Add streaming to the example
- [ ] Put it in a web server like fastAPI
