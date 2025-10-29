from openai import OpenAI
import pandas as pd
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()
# ✅ Initialize OpenRouter client

API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,  # 🔑 replace with your API key
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "CSV Query Chatbot"
    }
)

# ✅ Load dataset
data = pd.read_csv("cleaned.csv")

columns_to_keep = [
    "Title", "City + Locality", "BHK", "price", "Project Name",
    "Possession Status (Ready / Under Construction)", "amenities", "propertyImages"
]
data = data[columns_to_keep]

# ✅ Clean price column (extract numeric value)
def parse_price(price_str):
    try:
        s = str(price_str).strip().replace("₹", "").replace(",", "").upper()
        if "CR" in s:
            return float(re.findall(r"[\d\.]+", s)[0]) * 100  # Convert Cr → Lakh
        elif "L" in s:
            return float(re.findall(r"[\d\.]+", s)[0])
        else:
            return float(s)
    except:
        return None

data["numeric_price"] = data["price"].apply(parse_price)

# ✅ Extract filters
def extract_filters(query):
    filters = {}

    # 1️⃣ Property Type or BHK (supports Office, Villa, RK, etc.)
    property_types = ["BHK", "RK", "Office", "Office space", "House_Villa", "Villa"]
    filters["property_type"] = None

    bhk_match = re.search(r"(\d+\.?\d*)\s*(BHK|RK)", query, re.IGNORECASE)
    if bhk_match:
        filters["property_type"] = bhk_match.group(1).upper() + bhk_match.group(2).upper()
    else:
        for p in property_types:
            if p.lower() in query.lower():
                filters["property_type"] = p
                break

    # 2️⃣ Price range (e.g. under 1Cr, below 50L)
    price_match = re.search(r"under\s*(\d+\.?\d*)\s*(cr|crore|l|lakh)", query, re.IGNORECASE)
    if price_match:
        value = float(price_match.group(1))
        unit = price_match.group(2).lower()
        filters["max_price"] = value * 100 if "cr" in unit else value
    else:
        filters["max_price"] = None

    # 3️⃣ Possession status
    if "ready" in query.lower():
        filters["status"] = "READY"
    elif "under" in query.lower() or "construction" in query.lower():
        filters["status"] = "UNDER_CONSTRUCTION"

    # 4️⃣ City
    city_keywords = [
        "Pune", "Mumbai", "Hyderabad", "Bangalore", "Delhi", "Chennai",
        "Kolkata", "Ahmedabad", "Noida", "Gurgaon", "Vijayawada"
    ]
    for city in city_keywords:
        if city.lower() in query.lower():
            filters["city"] = city
            break

    return filters


# ✅ Main Function
def ask_llm_about_csv(query):
    # Greeting
    if re.match(r"^(hi|hello|hey|hola|hii|good\s*morning|good\s*evening|thank\s*you)$", query.strip(), re.IGNORECASE):
        return {"summary": "Hi there! 👋 How can I help you find properties today?", "results": []}

    filters = extract_filters(query)
    filtered = data.copy()

    # Filter by property type (BHK / Office / Villa etc.)
    if filters.get("property_type"):
        filtered = filtered[
            filtered["BHK"].astype(str).str.contains(filters["property_type"], case=False, na=False)
        ]

    # Filter by city
    if "city" in filters:
        filtered = filtered[
            filtered["City + Locality"].astype(str).str.contains(filters["city"], case=False, na=False)
        ]

    # Filter by possession status
    if "status" in filters:
        filtered = filtered[
            filtered["Possession Status (Ready / Under Construction)"]
            .astype(str)
            .str.contains(filters["status"], case=False, na=False)
        ]

    # Filter by price range
    if filters.get("max_price"):
        filtered = filtered[filtered["numeric_price"].notna()]
        filtered = filtered[filtered["numeric_price"] <= filters["max_price"]]

    filtered = filtered.head(10)

    # If no results found
    if filtered.empty:
        return {"summary": "I couldn’t find any matching properties.", "results": []}

    # ✅ Create instant JSON (no heavy LLM calls)
    results = []
    for _, row in filtered.iterrows():
        results.append({
            "Title": row.get("Title", "Unknown"),
            "City + Locality": row.get("City + Locality", "Unknown"),
            "BHK": row.get("BHK", "Unknown"),
            "Price": row.get("price", "Unknown"),
            "Project Name": row.get("Project Name", "Unknown"),
            "Possession Status": row.get("Possession Status (Ready / Under Construction)", "Unknown"),
            "Amenities": row.get("amenities", "Unknown"),
            "URL": str(row.get("propertyImages", "Unknown")).strip("[]'\"")
        })

    # ✅ Short summary via fast LLM (tiny prompt)
    sample_summary = (
        f"There are {len(results)} {filters.get('property_type', 'properties')} "
        f"in {filters.get('city', 'various locations')}"
    )
    if filters.get("max_price"):
        sample_summary += f" under ₹{filters['max_price']} Lakh."
    else:
        sample_summary += "."

    completion = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "Summarize property search results briefly."},
            {"role": "user", "content": sample_summary}
        ]
    )
    summary = completion.choices[0].message.content.strip()

    return {"summary": summary, "results": results}



