import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def search_web(query):
    """Fetch top 3 snippets from SerpAPI"""
    api_key = os.getenv("SERPAPI_KEY")
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": api_key, "num": 3}
    res = requests.get(url, params=params)
    sources = []
    if res.status_code == 200:
        data = res.json()
        for result in data.get("organic_results", [])[:3]:
            sources.append({
                "title": result.get("title", "No title"),
                "link": result.get("link", "#"),
                "snippet": result.get("snippet", "No info")
            })
    return sources


def execute(tasks, user_input):
    """Runs Gemini check and returns (verdict, evidence, probability %)"""
    evidence = search_web(user_input)
    evidence_text = " | ".join([e['snippet'] for e in evidence]) if evidence else "No live sources found."

    verdict = call_gemini(
        f"""
        Claim: {user_input}
        Evidence: {evidence_text}
        Task: {tasks}

        Give:
        1) Short reasoning
        2) Final verdict (TRUE / FALSE / UNVERIFIED)
        3) Confidence level (Low, Medium, High)
        4) Probability that the claim is true (0-100%)
        """
    )

    # Try extracting probability
    probability = None
    match = re.search(r"(\d{1,3})\s*%", verdict)
    if match:
        probability = min(100, max(0, int(match.group(1))))

    return verdict, evidence, probability


def get_trending_news():
    """Fetch trending headlines from NewsAPI"""
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return []

    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={api_key}"
        res = requests.get(url)
        if res.status_code == 200:
            articles = res.json().get("articles", [])
            return [
                {
                    "title": art["title"],
                    "description": art.get("description", ""),
                    "url": art["url"],
                    "source": art["source"]["name"]
                }
                for art in articles
            ]
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []
    return []