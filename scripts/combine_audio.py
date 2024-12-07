import os
import argparse
from pydub import AudioSegment


def main():
    parser = argparse.ArgumentParser(
        description='combine audios. Input two folders with audio and the result will be their combination',
    )

    parser.add_argument('first_input', type=str)
    parser.add_argument('second_input', type=str)
    parser.add_argument('-o', '--output', default="../output")
    parser.add_argument('-s', '--silent', default=1, type=int)
    parser.add_argument('-f', '--fade', default=1, type=int)

    args = parser.parse_args()

    # Function to process a single audio file
    def process_file(file_path):
        audio = AudioSegment.from_wav(file_path)
        return audio.fade_out(args.fade)

    # Function to combine two audio files
    def combine_audio(audio1, audio2):
        return audio1 + AudioSegment.silent(args.silent) + audio2

    output_directory = args.output
    os.makedirs(output_directory, exist_ok=True)

    # Process first input
    if os.path.isdir(args.first_input):
        files_1 = [fname for fname in os.listdir(args.first_input) if fname.endswith('.wav')]
    else:
        files_1 = [args.first_input]

    # Process second input
    if os.path.isdir(args.second_input):
        files_2 = [fname for fname in os.listdir(args.second_input) if fname.endswith('.wav')]
    else:
        files_2 = [args.second_input]

    for file1 in files_1:
        for file2 in files_2:
            f1_path = os.path.join(args.first_input, file1) if os.path.isdir(args.first_input) else file1
            f2_path = os.path.join(args.second_input, file2) if os.path.isdir(args.second_input) else file2

            processed_audio1 = process_file(f1_path)
            processed_audio2 = process_file(f2_path)
            combined_audio = combine_audio(processed_audio1, processed_audio2)

            output_file_name = f"{os.path.splitext(os.path.basename(f1_path))[0]}_{os.path.splitext(os.path.basename(f2_path))[0]}.wav"
            output_path = os.path.join(output_directory, output_file_name)

            combined_audio.export(output_path, format="wav")
            print(f"Combined audio saved as {output_file_name}")


if __name__ == '__main__':
    main()
