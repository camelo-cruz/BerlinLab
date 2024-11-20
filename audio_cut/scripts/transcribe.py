import os
import whisper
import json
import requests

# Use raw string to avoid unicode escape error
folder = r"C:\Users\camelo.cruz\Desktop\data"

# Load the Whisper model
model = whisper.load_model("large", device="cpu")

for filename in os.listdir(folder):
    if filename.endswith('.wav'):
        filepath = os.path.join(folder, filename)
        
        # Transcribe the audio file
        result = model.transcribe(filepath, language='de', word_timestamps=True)
        
        # Save the transcription to a JSON file
        output = filename.replace('.wav', '.json')
        output_path = os.path.join(folder, output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)