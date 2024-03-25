import os 
import pandas as pd
from deep_translator import GoogleTranslator
import argparse

def translate(file, target_lang):
    df = pd.read_excel(file)
    
    #read the excel sheet and either add a new column 'automatic_translation'
    #or transform add to the existing column the translations
    for i in range(len(df)):
        try:
            if 'automatic_translation' in df.columns:
                df.loc[i,'automatic_translation'] = GoogleTranslator(source='auto', target='en').translate(df['transcription'][i]) 
            else:
                df.insert(df.columns.get_loc('transcription_comments'), 'automatic_translation', 'n')
                df.loc[i,'automatic_translation'] = GoogleTranslator(source='auto', target='en').translate(df['transcription'][i]) 
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
        
    return df


def main():
    """
    Main function to translate a manually prepaired transcription
    
    arguments:
    file
    target language
    """
    
    parser = argparse.ArgumentParser(description="automatic transcription")
    parser.add_argument("input_file")
    parser.add_argument("target_language", default="en")
    args = parser.parse_args()
    
    df = translate(args.input_file, args.target_language)
    
    df.to_excel(args.input_file)


if __name__ == "__main__":
    main()