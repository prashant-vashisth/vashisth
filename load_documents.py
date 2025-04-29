import os
from pypdf import PdfReader

def load_all_pdfs_from_folder(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
    return all_text

if __name__ == "__main__":
    folder = "source_pdfs"
    combined_text = load_all_pdfs_from_folder(folder)
    print(f"First 1000 characters:\n{combined_text[:1000]}")
