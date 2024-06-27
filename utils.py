import os
import json
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()


def _build_system_message():
    pass

def extract_text_from_file(file):
    # Determine the file extension
    file_extension = os.path.splitext(file)[1]

    # Initialize the text content
    text_content = ""
    # Read the file content based on the file type
    if file_extension == ".pdf":
        with open(file, "rb") as fileobj:
            reader = PdfReader(fileobj)
            for page in reader.pages:
                text_content += page.extract_text()

        # if the text_content is small, that means we need to use OCR
        if len(text_content) < 20:
            images = convert_from_path(file)
            for image in images:
                text_content += pytesseract.image_to_string(image)
    
    elif file_extension == ".docx":
        # Use python-docx library to read the content
        pass

    return text_content

def parse_content(text_content):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    completion = client.chat.completions.create(
        model="gpt-4o",
          messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "You are a professional grade resume parser and will be provided with text content extracted from a resume file. Your task is to return nothing else but clean, accurate JSON formatted data with: # - Name\n# - Graduate Year (Latest Education, make sure the output is a number parsed or inferred))\n# - School & Major (Latest Education)\n# - PhD (true for Candidate or degree holder).\nThe keys should be: 'phd', 'name', 'school', 'major', 'grad_year'.\nPlease help translate school and major into Simplified Chinese in the returned JSON if applicable. Check your response to make sure all Chinese characters are in Simplified Chinese."
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": text_content,
                }
            ]
            }
        ],
        response_format= { "type":"json_object" }
    )

    return json.loads(completion.choices[0].message.content)

def generate_filename(parsed_info, args):
    # If the school is in the target list, prepend "Matched-" to the filename

    education_level = "本硕" if not parsed_info['phd'] else "博士"

    filename = f'{education_level}-{parsed_info['name']}-{parsed_info['school']}-{parsed_info['major']}-{parsed_info['grad_year']}'

    # If the graduate year is after 2024, mark as "实习"; otherwise mark as "全职"
    if parsed_info['grad_year'] and int(parsed_info['grad_year']) > 2024:
        filename = f'实习-{filename}'
    else:
        filename = f'全职-{filename}'

    if args.target_list:
        # read schools from target list, each line contains a school name
        with open(args.target_list, 'r', encoding='utf-8') as f:
            school_list = f.readlines()
            school_list = [x.strip() for x in school_list]
            if parsed_info['school'] in school_list:
                filename = f'Matched-{filename}'
            
    return filename
