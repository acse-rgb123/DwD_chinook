import PyPDF2
import os

class PDFReader:
    def __init__(self, pdf_file_path):
        self.pdf_file_path = pdf_file_path

    def extract_text(self):
        with open(self.pdf_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()

        return text

    def extract_sections(self):
        """
        Split the text into sections (you can customize this based on how the PDF content is structured).
        """
        text = self.extract_text()
        paragraphs = text.split('\n\n')
        sections = {}

        current_section = None
        for paragraph in paragraphs:
            if 'Table' in paragraph or 'Schema' in paragraph:
                current_section = paragraph
                sections[current_section] = ""
            elif current_section:
                sections[current_section] += paragraph + "\n"
        
        return sections
