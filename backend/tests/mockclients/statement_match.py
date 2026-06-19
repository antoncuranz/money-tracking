from statement_match.adapter.llm_client import LlmProviderError
from statement_match.adapter.pdf_extractor import PdfExtractionError


class MockPdfExtractor:
    text = "Statement text"
    error = None
    contents = []

    @classmethod
    def reset(cls):
        cls.text = "Statement text"
        cls.error = None
        cls.contents = []

    def extract_text(self, content: bytes) -> str:
        type(self).contents.append(content)
        if type(self).error:
            raise type(self).error
        return type(self).text


class MockStatementMatchLlmClient:
    model = "mock-model"
    payload = {"results": []}
    error = None
    prompts = []

    @classmethod
    def reset(cls):
        cls.model = "mock-model"
        cls.payload = {"results": []}
        cls.error = None
        cls.prompts = []

    def match_statement(self, prompt: str):
        type(self).prompts.append(prompt)
        if type(self).error:
            raise type(self).error
        return type(self).payload
