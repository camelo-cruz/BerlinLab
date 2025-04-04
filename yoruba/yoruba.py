import os
import pandas as pd
import docx
import re

column_index = 'recording'

def extract_base_block_name(name):
    match = re.search(r'(blockNr_\d+_taskNr_\d+_trialNr_\d+)', name)
    return match.group(1) if match else name

def process_yoruba(base_folder):
    # Ensure the folder exists
    if not os.path.exists(base_folder):
        print(f"Folder not found: {base_folder}")
        return

    # Iterate through all subdirectories (sessions)
    for root, dirs, files in os.walk(base_folder):
        if any(file.endswith(".xlsx") for file in files) and any(file.endswith(".docx") for file in files):
            print(f"Processing session folder: {root}")
            process_session(root)

def process_session(folder_path):
    # Define the Excel file path (assumes only one .xlsx per folder)
    excel_file_path = None
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xlsx"):
            excel_file_path = os.path.join(folder_path, file_name)
            break

    if not excel_file_path:
        print(f"No .xlsx file found in {folder_path}")
        return

    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_file_path)

    # Ensure all necessary columns exist; add them if missing
    columns_to_fix = ['latin_transcription_everything', 'translation_everything', 
                      'latin_transcription_utterance_used', 'glossing_utterance_used', 
                      'translation_utterance_used']
    for col in columns_to_fix:
        if col not in df.columns:
            df[col] = ""
    df[columns_to_fix] = df[columns_to_fix].fillna("").astype(str)

    # Regular expression to match text inside various types of quotes (single or double)
    quote_pattern = re.compile(r"([‘’“”'\"].*?[‘’“”'\"])")

    # Process each .docx file in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".docx"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing: {file_name}")

            try:
                doc = docx.Document(file_path)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                continue

            # Build full text preserving indentation (for tabs)
            full_text = []
            for para in doc.paragraphs:
                if para.paragraph_format.left_indent:
                    full_text.append("\t" + para.text)
                else:
                    full_text.append(para.text)
            text = "\n".join(full_text)

            # Split the text into individual lines
            lines = text.strip().split("\n")

            # Variables to hold data for the current block
            current_block = None
            latin_transcription = []
            translation = []
            dot_lines = []
            collecting_dots = False

            # Process the text line by line
            for i, line in enumerate(lines):
                line = line.rstrip()

                # If a new block starts (line begins with "blockNr"), process the previous block first
                if line.startswith("blockNr"):
                    if current_block:
                        base_block = extract_base_block_name(current_block)
                        row_index = df[df[column_index].fillna('').str.strip().str.contains(re.escape(base_block))].index
                        if not row_index.empty:
                            index = row_index[0]
                            df.at[index, 'latin_transcription_everything'] = "\n".join(latin_transcription).strip()
                            df.at[index, 'translation_everything'] = "\n".join(translation).strip()
                            
                            if dot_lines:
                                # Determine group size: expect groups of either 3 or 4 dot lines.
                                if len(dot_lines) % 3 == 0:
                                    group_size = 3
                                elif len(dot_lines) % 4 == 0:
                                    group_size = 4
                                else:
                                    print(f"Unexpected number of dot_lines ({len(dot_lines)}) in block '{current_block}'.")
                                    group_size = None

                                if group_size:
                                    groups = [dot_lines[i:i+group_size] for i in range(0, len(dot_lines), group_size)]
                                    latin_trans_utterance = "\n".join(group[0] for group in groups)
                                    if group_size == 3:
                                        glossing_utterance = "\n".join(group[1] for group in groups)
                                        translation_utterance = "\n".join(group[2] for group in groups)
                                    else:  # group_size == 4
                                        glossing_utterance = "\n".join(f"{group[1]}\n{group[2]}" for group in groups)
                                        translation_utterance = "\n".join(group[3] for group in groups)
                                    
                                    df.at[index, 'latin_transcription_utterance_used'] = latin_trans_utterance
                                    df.at[index, 'glossing_utterance_used'] = glossing_utterance
                                    df.at[index, 'translation_utterance_used'] = translation_utterance
                        else:
                            print(f"Block name '{current_block}' not found in the Excel file.")

                    # Reset for new block
                    current_block = line
                    latin_transcription, translation, dot_lines = [], [], []
                    collecting_dots = False
                    continue

                # Process dotted lines (utterance lines)
                if line.startswith("."):
                    dot_lines.append(line.lstrip('.').strip())
                    collecting_dots = True
                    continue

                collecting_dots = False

                # Remove punctuation and extract quoted text for translation
                punctuation_to_remove = re.compile(r"[.,:…\t]")
                matches = quote_pattern.findall(line)
                if matches:
                    for match in matches:
                        translation.append(match.strip())
                    modified_line = re.sub(quote_pattern, '\n', line)
                    before_text = punctuation_to_remove.sub('', modified_line).strip()
                    if before_text:
                        latin_transcription.append(before_text)

            # Process the last block after loop ends
            if current_block:
                base_block = extract_base_block_name(current_block)
                row_index = df[df[column_index].fillna('').str.strip().str.contains(re.escape(base_block))].index
                if not row_index.empty:
                    index = row_index[0]
                    df.at[index, 'latin_transcription_everything'] = "\n".join(latin_transcription).strip()
                    df.at[index, 'translation_everything'] = "\n".join(translation).strip()
                    
                    if dot_lines:
                        if len(dot_lines) % 3 == 0:
                            group_size = 3
                        elif len(dot_lines) % 4 == 0:
                            group_size = 4
                        else:
                            print(f"Unexpected number of dot_lines ({len(dot_lines)}) in block '{current_block}'.")
                            group_size = None

                        if group_size:
                            groups = [dot_lines[i:i+group_size] for i in range(0, len(dot_lines), group_size)]
                            latin_trans_utterance = "\n".join(group[0] for group in groups)
                            if group_size == 3:
                                glossing_utterance = "\n".join(group[1] for group in groups)
                                translation_utterance = "\n".join(group[2] for group in groups)
                            else:  # group_size == 4
                                glossing_utterance = "\n".join(f"{group[1]}\n{group[2]}" for group in groups)
                                translation_utterance = "\n".join(group[3] for group in groups)
                            
                            df.at[index, 'latin_transcription_utterance_used'] = latin_trans_utterance
                            df.at[index, 'glossing_utterance_used'] = glossing_utterance
                            df.at[index, 'translation_utterance_used'] = translation_utterance
                else:
                    print(f"Block name '{current_block}' not found in the Excel file.")

    # Save the updated DataFrame to a new Excel file
    output_file = os.path.join(folder_path, "trials_and_sessions_annotated.xlsx")
    try:
        df.to_excel(output_file, index=False)
        print(f"File updated successfully: {output_file}")
    except Exception as e:
        print(f"Error saving Excel file: {e}")

# Example usage
process_yoruba('/Users/alejandra/Desktop/Session_1014449 Kopie')