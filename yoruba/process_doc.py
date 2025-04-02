from docx import Document
import re

def process_word_file(input_path, output_path):
    # Load the Word document
    doc = Document(input_path)

    # Define simple replacements
    simple_replacements = {
        "Block": "block",
        "_trial_": "_trialNr"
    }

    # Process each paragraph
    for para in doc.paragraphs:
        text = para.text

        # Remove all tabs
        text = text.replace("\t", " ")

        # If the line contains `-`, add `.` at the start
        if "-" in text:
            text = "." + text  # Add `.` at the beginning

        # Perform simple replacements
        for old, new in simple_replacements.items():
            text = text.replace(old, new)

        # Replace `_rec` only if it appears at the **end of a sentence**
        text = re.sub(r"_rec$", "_recoding.mp3", text)

        # Update the paragraph text
        para.text = text

    # Save the modified document
    doc.save(output_path)
    print(f"Processed file saved as: {output_path}")

# Example usage
input_file = '/Users/alejandra/Library/CloudStorage/OneDrive-FreigegebeneBibliotheken–Leibniz-ZAS/Leibniz Dream Data - Studies/F_Negative_Concepts/F01a-Cum-Sine-Patterns/F01a_raw_files_yor/F01a_yor_for_Johnson/Session_1122050/Session_1122050.docx'
output_file = '/Users/alejandra/Library/CloudStorage/OneDrive-FreigegebeneBibliotheken–Leibniz-ZAS/Leibniz Dream Data - Studies/F_Negative_Concepts/F01a-Cum-Sine-Patterns/F01a_raw_files_yor/F01a_yor_for_Johnson/Session_1122050/Session_1122050.docx'
process_word_file(input_file, output_file)
