from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)

# Configure Gemini
# print("Loaded Key:", os.getenv("GEMINI_API_KEY"))  # TEMP DEBUG
genai.configure(api_key="AIzaSyBTPJHcdxrXlWAfj-SReuLO4IuZx8scYTk")

model = genai.GenerativeModel("gemini-1.5-flash")


# STEP 1: Gemini creates optimized shopping search query
def generate_search_query(user_input):
    prompt = f"""
    Convert this user request into a shopping search query:
    "{user_input}"
    Make it suitable for finding best online deals in India.
    """

    response = model.generate_content(prompt)
    return response.text.strip()


# STEP 2: Free search using DuckDuckGo
def duckduckgo_search(query):
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query}

    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for result in soup.find_all("a", class_="result__a", limit=8):
        title = result.get_text()
        link = result.get("href")

        results.append({
            "title": title,
            "link": link
        })

    return results


# STEP 3: Gemini ranks and selects best deals
def rank_deals(user_input, results):
    prompt = f"""
    User wants: {user_input}

    Here are online search results:
    {results}

    Select the best 5 deals.
    Return clean formatted output with:
    - Product Name
    - Why it's a good deal
    - Link
    """

    response = model.generate_content(prompt)
    return response.text


@app.route("/", methods=["GET", "POST"])
def home():
    final_result = ""

    if request.method == "POST":
        user_input = request.form.get("query")

        if user_input:
            optimized_query = generate_search_query(user_input)
            search_results = duckduckgo_search(optimized_query)
            final_result = rank_deals(user_input, search_results)

    return render_template("index.html", result=final_result)


if __name__ == "__main__":
    app.run(debug=False)
