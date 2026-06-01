# features.py — Tool implementations for the Backyard Bird ReAct Agent
# Each function here is a real, callable tool the agent can use during its reasoning loop
# Analogy: if config.py is the menu, this is the kitchen — the place where the actual work gets done

import math          # provides mathematical functions like sqrt, floor, etc.
# import wikipedia     # Python library for fetching Wikipedia summaries
import requests      # for making HTTP calls to the Open-Meteo weather API
import config        # imports our central settings (API URLs, etc.)

# ── Calculator ─────────────────────────────────────────────────────────────────

def calculator(expression: str) -> str:
    """
    Evaluates a math expression and returns the result as a string.

    Plain explanation: takes a string like '77 * 0.14' and computes the answer.
    Analogy: a pocket calculator that accepts typed expressions instead of button presses.
    """
    try:
        # eval() executes the expression string as Python code
        # we pass math as a safe namespace so the LLM can use functions like math.sqrt()
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return f"{result}"                           # returns the result as a plain string
    except Exception as e:                           # catches any invalid expression errors
        return f"Calculator error: {str(e)}"         # returns a readable error instead of crashing

# ── Wikipedia ──────────────────────────────────────────────────────────────────

def wikipedia_search(query: str) -> str:
    """
    Fetches a Wikipedia summary for a bird species or ornithology topic.

    Plain explanation: calls Wikipedia's API directly and returns the first
    few sentences of the article.
    Analogy: sending an intern to the library to look up a topic and come back
    with a short summary — not the whole book, just the key facts.
    """
    try:
        response = requests.get(                             # calls Wikipedia's REST API directly
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_"),
            headers={"User-Agent": "BirdAgent/1.0"},         # required by Wikipedia's API terms
            timeout=10                                        # gives up after 10 seconds
        )
        if response.status_code != 200:                      # checks if the request succeeded
            return f"No Wikipedia article found for '{query}'."
        data = response.json()                               # parses the JSON response
        extract = data.get("extract", "")                    # gets the article summary text
        if not extract:                                      # checks if summary is empty
            return f"No Wikipedia summary available for '{query}'."
        sentences = extract.split(". ")                      # splits into sentences
        summary = ". ".join(sentences[:4])                   # takes the first 4 sentences
        if not summaryd.endswith("."):                        # adds a period if missing
            summary += "."
        return summary                                        # returns the cleaned summary
    except Exception as e:                                   # catches any network or parsing errors
        return f"Wikipedia error: {str(e)}"

# ── Weather ────────────────────────────────────────────────────────────────────
def get_weather(city: str) -> str:
    """
    Returns current weather conditions for a given city using the Open-Meteo API.

    Plain explanation: converts the city name to coordinates, then fetches
    live temperature, wind speed, and weather condition.
    Analogy: looking out the window for someone in another city — you first
    find where their city is on a map, then check what the sky looks like there.
    """
    try:
        # Step 1: convert city name to coordinates using Nominatim (OpenStreetMap)
        geo_response = requests.get(                         # calls Nominatim geocoding API
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},  # q accepts any city name or address
            headers={"User-Agent": "BirdAgent/1.0"},         # required by Nominatim's terms of use
            timeout=10                                        # gives up after 10 seconds
        )
        geo_data = geo_response.json()                       # parses the JSON response into a list

        if not geo_data:                                     # checks if any location was found
            return f"Could not find location: '{city}'"

        lat = float(geo_data[0]["lat"])                      # extracts latitude as a float
        lon = float(geo_data[0]["lon"])                      # extracts longitude as a float
        location_name = geo_data[0]["display_name"]          # extracts the full resolved place name                   # extracts the resolved city name

        # Step 2: fetch current weather using coordinates
        weather_response = requests.get(                     # makes a GET request to the weather API
            config.WEATHER_API_URL,
            params={
                "latitude": lat,                             # latitude from step 1
                "longitude": lon,                            # longitude from step 1
                "current_weather": True,                     # requests current conditions (not forecast)
                "temperature_unit": "fahrenheit",            # returns temp in °F
                "wind_speed_unit": "mph",                    # returns wind in mph
            },
            timeout=10                                       # gives up after 10 seconds
        )
        weather_data = weather_response.json()               # parses the JSON response

        current = weather_data["current_weather"]            # extracts the current weather block
        temp = current["temperature"]                        # current temperature in °F
        wind = current["windspeed"]                          # current wind speed in mph
        code = current["weathercode"]                        # WMO weather code (number representing conditions)

        # WMO weather code mapping — converts numeric codes to human-readable descriptions
        # full code list: https://open-meteo.com/en/docs
        weather_descriptions = {
            0: "clear sky",
            1: "mainly clear", 2: "partly cloudy", 3: "overcast",
            45: "fog", 48: "icy fog",
            51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
            61: "slight rain", 63: "moderate rain", 65: "heavy rain",
            71: "slight snow", 73: "moderate snow", 75: "heavy snow",
            80: "slight showers", 81: "moderate showers", 82: "violent showers",
            95: "thunderstorm",
        }
        description = weather_descriptions.get(code, f"weather code {code}")  # looks up description or falls back to code number

        # bird watching quality assessment based on conditions
        good_watching = temp > 35 and wind < 20 and code in [0, 1, 2, 3]  # True if conditions are reasonable
        watching_note = "Good conditions for bird watching." if good_watching else "Challenging conditions for bird watching."

        return (
            f"Current weather in {location_name}: {temp}°F, {description}, "
            f"wind {wind} mph. {watching_note}"
        )

    except Exception as e:                                   # catches any network or parsing errors
        return f"Weather error: {str(e)}"

# ── Dictionary ─────────────────────────────────────────────────────────────────

# Built-in ornithology glossary — covers common technical terms the agent might be asked about
# Analogy: a pocket field guide glossary — not every word in the English language,
# just the specialized vocabulary a birder is likely to encounter
ORNITHOLOGY_GLOSSARY = {
    "precocial": "Describes birds whose chicks hatch in an advanced state of development — eyes open, covered in down, and able to move around shortly after hatching. Examples: ducks, geese, shorebirds.",
    "altricial": "Describes birds whose chicks hatch helpless — eyes closed, little or no feathers, entirely dependent on parents for warmth and food. Examples: robins, sparrows, most songbirds.",
    "passerine": "The largest order of birds, also called perching birds or songbirds. Characterized by three toes pointing forward and one pointing back, allowing them to grip branches. Examples: warblers, finches, sparrows.",
    "raptor": "A bird of prey — characterized by sharp talons, a hooked beak, and keen eyesight. Examples: hawks, eagles, falcons, owls.",
    "molt": "The process by which birds shed old feathers and grow new ones. Most birds molt at least once a year, often after breeding season.",
    "brood parasite": "A bird that lays its eggs in another species' nest, leaving the host parents to raise its young. The Brown-headed Cowbird is the most common brood parasite in North America.",
    "migration": "The seasonal movement of birds between breeding and wintering grounds, typically triggered by changes in day length and temperature.",
    "fledgling": "A young bird that has grown its first true feathers and is learning to fly, but is still dependent on its parents for food.",
    "clutch": "The complete set of eggs laid by a bird in a single nesting attempt.",
    "dimorphic": "Having two distinct forms. Sexual dimorphism in birds refers to visible differences between males and females of the same species, such as the bright red male vs. brown female Northern Cardinal.",
    "irruption": "An irregular mass movement of birds into areas where they are not normally found, usually driven by food shortages in their usual range. Example: snowy owls moving south in winter.",
    "corvid": "A member of the crow family (Corvidae), known for high intelligence. Examples: crows, ravens, jays, magpies.",
    "riparian": "Relating to or living on the banks of rivers or streams. Many bird species prefer riparian habitats for nesting and foraging.",
    "crepuscular": "Active primarily at dawn and dusk. Some birds, like the American Woodcock, are crepuscular.",
    "diurnal": "Active primarily during the day. Most songbirds are diurnal.",
    "nocturnal": "Active primarily at night. Examples: owls, nightjars, whip-poor-wills.",
}

def dictionary_lookup(term: str) -> str:
    """
    Looks up an ornithology or bird-related term and returns its definition.

    Plain explanation: checks a built-in glossary of bird and ornithology vocabulary
    and returns the definition if found.
    Analogy: a specialized field guide glossary — it only covers bird-related terms,
    but covers them well.
    """
    normalized = term.lower().strip()                        # converts to lowercase and removes whitespace for matching
    if normalized in ORNITHOLOGY_GLOSSARY:                   # checks if the term exists in the glossary
        return f"{term}: {ORNITHOLOGY_GLOSSARY[normalized]}" # returns the term and its definition
    else:
        return f"'{term}' was not found in the ornithology glossary. Try terms like: precocial, altricial, passerine, raptor, molt, migration, fledgling, clutch, dimorphic, irruption, corvid."

# ── Tool registry ──────────────────────────────────────────────────────────────
# Maps tool names (strings) to their actual Python functions
# The agent loop in predict.py uses this dict to call the right function
# Analogy: a switchboard operator — when a call comes in for 'weather',
# the switchboard routes it to the get_weather function

TOOL_REGISTRY = {
    "calculator": calculator,         # maps the string "calculator" to the calculator function
    "wikipedia": wikipedia_search,    # maps "wikipedia" to the wikipedia_search function
    "weather": get_weather,           # maps "weather" to the get_weather function
    "dictionary": dictionary_lookup,  # maps "dictionary" to the dictionary_lookup function
}