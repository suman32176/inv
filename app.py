import os
import logging
import asyncio
from dotenv import load_dotenv
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import get_video_search_queries_timed, merge_empty_intervals
import argparse

# Load environment variables
load_dotenv()
print("Environment variables loaded. app")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main(topic):
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"
    print(f"Starting the process for topic: {topic}")

    try:
        # Generate the script
        # response = generate_script(topic)
        print("Please enter the video script:")
        script = input()
        logging.info("Script generated successfully. app")
        print("Script generated successfully.app")
    except Exception as e:
        logging.error(f"Error generating script: {e}")
        print("Error generating script.")
        return

    logging.info(f"Script: {response}")
    print(f"Generated Script: {response}")

    try:
        # Generate audio from the script
        await generate_audio(response, SAMPLE_FILE_NAME)
        logging.info("Audio generated successfully.")
        print("Audio generated successfully.app")
    except Exception as e:
        logging.error(f"Error generating audio: {e}")
        print("Error generating audio.app")
        return

    try:
        # Generate timed captions
        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        logging.info("Timed captions generated successfully.")
        print("Timed captions generated successfully. app")
    except Exception as e:
        logging.error(f"Error generating timed captions: {e}")
        print("Error generating timed captions.")
        return

    logging.info(f"Timed Captions: {timed_captions}")
    print(f"Generated Timed Captions: {timed_captions}")

    try:
        # Generate search queries for videos
        search_terms = get_video_search_queries_timed(response, timed_captions)
        if search_terms:
            logging.info("Search terms generated successfully.")
            print("Search terms generated successfully.")
        else:
            logging.warning("No search terms generated.")
            print("Warning: No search terms generated.")
    except Exception as e:
        logging.error(f"Error generating search terms: {e}")
        print("Error generating search terms.")
        return

    logging.info(f"Search Terms: {search_terms}")
    print(f"Generated Search Terms: {search_terms}")

    try:
        # Generate background video URLs
        background_video_urls = await generate_video_url(search_terms, VIDEO_SERVER) if search_terms else None
        if background_video_urls:
            logging.info("Background video URLs generated successfully.")
            print("Background video URLs generated successfully.")
        else:
            logging.warning("No background video URLs generated.")
            print("Warning: No background video URLs generated.")
    except Exception as e:
        logging.error(f"Error generating background video URLs: {e}")
        print("Error generating background video URLs.")
        return

    background_video_urls = merge_empty_intervals(background_video_urls)

    if background_video_urls:
        try:
            # Get the output media
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
            logging.info("Video generated successfully.")
            print("Video generated successfully.")
            print(video)
        except Exception as e:
            logging.error(f"Error generating video: {e}")
            print("Error generating video.")
    else:
        logging.warning("No background video available for merging.")
        print("Warning: No background video available for merging.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")

    args = parser.parse_args()
    asyncio.run(main(args.topic))