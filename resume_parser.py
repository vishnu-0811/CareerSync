# import fitz  # PyMuPDF
# import re

# # Load skill list from a file (if you've saved one)
# def load_skill_list(file_path):
#     with open(file_path, 'r') as f:
#         return [line.strip().lower() for line in f.readlines() if line.strip()]

# # Extract text from PDF using PyMuPDF
# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     text = ''
#     for page in doc:
#         text += page.get_text()
#     doc.close()
#     return text.lower()

# # Extract skills by matching with predefined list
# def extract_skills(text, skill_list):
#     found_skills = set()
#     for skill in skill_list:
#         pattern = r'\b' + re.escape(skill) + r'\b'
#         if re.search(pattern, text):
#             found_skills.add(skill)
#     return ', '.join(sorted(found_skills))

# # Full pipeline
# def parse_pdf_for_skills(pdf_path, skill_list_file="unique_skills.txt"):
#     skill_list = load_skill_list(skill_list_file)
#     text = extract_text_from_pdf(pdf_path)
#     return extract_skills(text, skill_list)

# # Example usage
# if __name__ == "__main__":
#     pdf_file = "path/to/your/resume.pdf"
#     skills = parse_pdf_for_skills(pdf_file)
#     print("Extracted Skills:", skills)
import fitz  # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Load skill list from a file
def load_skill_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# Extract text from PDF using fitz
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.lower()

# Extract skills using spaCy PhraseMatcher
def extract_skills_spacy(text, skill_list):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skill_list]
    matcher.add("SKILLS", patterns)

    doc = nlp(text)
    matches = matcher(doc)
    found_skills = {doc[start:end].text for _, start, end in matches}
    return ', '.join(sorted(found_skills))

# Full pipeline
def parse_pdf_for_skills(pdf_path, skill_list_file="unique_skills.txt"):
    skill_list = load_skill_list(skill_list_file)
    text = extract_text_from_pdf(pdf_path)
    return extract_skills_spacy(text, skill_list)

# Example usage
if __name__ == "__main__":
    pdf_file = "path/to/your/resume.pdf"
    skills = parse_pdf_for_skills(pdf_file)
    print("Extracted Skills:", skills)
