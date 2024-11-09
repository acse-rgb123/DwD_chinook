import PyPDF2


class PDFReader:
    def __init__(self, pdf_file_path):
        self.pdf_file_path = pdf_file_path

    def extract_text(self):
        with open(self.pdf_file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += (
                    reader.pages[page_num].extract_text() + "\n"
                )  # Add newline for separation

        return text

    def extract_sections(self):
        """
        Forcefully splits text into sections every 1000 characters for chunking.
        """
        text = self.extract_text()

        # Split into fixed-size sections for chunking if no section headers
        sections = {}
        section_size = 1000  # Customize based on typical document size

        for i in range(0, len(text), section_size):
            section_key = f"section_{i // section_size}"
            sections[section_key] = text[i : i + section_size]

        print(f"Total sections created: {len(sections)}")
        return sections
