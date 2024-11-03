import json
import logging
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
print("Environment variables loaded. script")

# Directly retrieve API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Select API client based on available keys
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    model = "mixtral-8x7b-32768"
    print("Using GROQ API client. script")
elif OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = "gpt-4"
    print("Using OpenAI API client.")
else:
    raise ValueError("No valid API key found for either OpenAI or Groq.")

def generate_script(topic):
    """Generates a concise, engaging YouTube Shorts script based on the given topic."""
    print(f"Generating script for topic: {topic}")

    prompt = (
        # f"""You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
        # Each video lasts less than 50 seconds (approximately 140 words). Your content is concise, original, 
        # and captivating. Please create an engaging script for the requested type of 'facts'.

        # For example:
        # Topic: Weird Facts
        # Script:
        # - Bananas are berries, but strawberries aren't.
        # - A single cloud can weigh over a million pounds.
        # - There's a species of jellyfish that is biologically immortal.

        # Requested topic: {topic}
        # Please format the output as a JSON object like this: 
        # {{ "script": "Here is the script..." }}
        # """
        
        
        
        f"""You are a seasoned content writer for a YouTube channel that produces in-depth facts videos. 
    Each video is a longer-format presentation, approximately 500 words in length, and goes beyond surface-level facts 
    to provide context and engaging details. Your content is original, captivating, and designed to keep the viewer interested 
    through a series of fascinating facts that are both educational and entertaining.

    For example:
    Topic: Unusual Animal Facts
    Script:
    - Did you know octopuses have three hearts? Two pump blood to the gills, while the third pumps it to the rest of the body. 
      This unique structure supports their high level of intelligence and adaptability in the ocean.
    - Dolphins have been observed giving themselves names. Scientists found that each dolphin has a distinct whistle that 
      other dolphins use to call it, similar to a human name.
    - Sloths can hold their breath longer than dolphins! By slowing their metabolism, they can remain underwater 
      for up to 40 minutes.

    Requested topic: {topic}
    Please write at least 500 words of script, structuring it with a clear introduction, detailed facts, and a conclusion.
    Format the output as a JSON object like this:
    {{ "script": "Here is the full script..." }}
    """
    )

    try:
        print("Sending request to API for script generation...")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": topic}]
        )
        print("Response received from API.")

        content = response.choices[0].message.content
        print("Parsing response content...")

        script = json.loads(content).get("script", "")
        if not script:
            raise ValueError("Script content missing in JSON.")
        
        print("Script generated successfully.")
        return script

    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        print("Error parsing JSON response.")
        return "Script could not be generated due to a parsing error."
    except Exception as e:
        logging.error(f"An error occurred while generating script: {e}")
        print("Script generation failed.")
        return "Script generation failed."
