# Supported file format: PDF, DOCX, DOC
# This program will parse all resume presented in source_dir and
# parse out the following information:
# - Name
# - Graduate Year
# - School & Major (Latest Education)
# - Highest Level of Education (Two Options: 本碩/博士)
# We will then rename the file to the following format and save it in output_dir:
# <本碩/博士>-<Name>-<School>-<Major>-<Graduate Year>
# If target_list is provided, we will save the resume with addtioanl prefix "Matched-" if the school is in the list

from options import parse_args
from utils import extract_text_from_file, parse_content, generate_filename
import os
import shutil

def process_file(file, args):

    print(f'Processing file: {file}...')

    text_content = extract_text_from_file(file)
    print('Waiting for response from OpenAI...')
    parsed_info = parse_content(text_content)

    # Get the original file extension
    file_extension = os.path.splitext(file)[1]

    filename = f"{generate_filename(parsed_info, args)}{file_extension}"
    print(f"New filename: {filename}. Press any key to save the file.")
    input()

    # Copy the file to the output directory with the new name
    shutil.copyfile(file, os.path.join(args.output_dir, filename))

def main():
    args = parse_args()
    # Check if args are valid
    if not os.path.exists(args.source_dir):
        print(f"Error: Source directory {args.source_dir} does not exist.")
        return
    if not os.path.exists(args.output_dir):
        print(f"Error: Output directory {args.output_dir} does not exist.")
        return
    if args.target_list and not os.path.exists(args.target_list):
        print(f"Error: Target list file {args.target_list} does not exist.")
        return
    # Get all files with the following extensions: PDF, DOCX, DOC
    files = os.listdir(args.source_dir)
    files = [file for file in files if file.endswith((".pdf", ".docx", ".doc"))]
    # Process each file
    for file in files:
        file_path = os.path.join(args.source_dir, file)
        process_file(file_path, args)
    print("All files processed.")
    

if __name__ == "__main__":
    main()