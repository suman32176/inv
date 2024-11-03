import edge_tts

async def generate_audio(text, outputFilename):
    print("Starting audio generation...")
    try:
        communicate = edge_tts.Communicate(text, "en-AU-WilliamNeural")
        print("Text-to-speech conversion initialized.")
        await communicate.save(outputFilename)
        print(f"Audio successfully saved to {outputFilename}.")
    except Exception as e:
        print(f"Error during audio generation: {e}")
