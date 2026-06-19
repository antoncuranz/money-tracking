from io import BytesIO

from pypdf import PdfReader


class PdfExtractionError(Exception):
    pass


class PdfExtractor:
    def extract_text(self, content: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(content))
        except Exception as exc:
            raise PdfExtractionError("Unable to read PDF.") from exc

        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                pages.append(page_text.strip())

        text = "\n\n".join(page for page in pages if page)
        if not text.strip():
            raise PdfExtractionError("PDF does not contain extractable text.")

        return text
