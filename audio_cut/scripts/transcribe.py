folder = 

for filename in os.listdir(folder):
  if filename.endswith('.wav'):
    !whisper '{filename}' --model large --language German --word_timestamps True
    output = filename.replace('.wav', '.json')
    files.download(output)