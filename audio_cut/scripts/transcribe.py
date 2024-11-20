import os
import subprocess

folder = "C:\Users\camelo.cruz\Desktop\data"

for filename in os.listdir(folder):
    if filename.endswith('.wav'):
        filepath = os.path.join(folder, filename)
        subprocess.run(['whisper', filepath, '--model', 'large', '--language', 'German', '--word_timestamps', 'True'])
        output = filename.replace('.wav', '.json')
        output_path = os.path.join(folder, output)