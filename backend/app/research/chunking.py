from __future__ import annotations

import re
from dataclasses import dataclass

from app.research.retrieval import ResearchDocument


@dataclass(frozen=True)
class ResearchChunk:
    chunk_id: str
    document_id: str
    title: str
    source: str
    published_date: str | None
    section: str
    chunk_index: int
    content: str


class FinancialDocumentChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 75) -> None:
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive.")
        if overlap < 0:
            raise ValueError("overlap cannot be negative.")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: ResearchDocument) -> list[ResearchChunk]:
        if not document.content.strip():
            raise ValueError("Document content cannot be empty.")

        sections = self._split_sections(document.content)
        chunks: list[ResearchChunk] = []
        chunk_index = 0

        for section, content in sections:
            words = content.split()
            if not words:
                continue

            step = self.chunk_size - self.overlap

            for start in range(0, len(words), step):
                chunk_words = words[start:start + self.chunk_size]
                if not chunk_words:
                    continue

                chunks.append(
                    ResearchChunk(
                        chunk_id=f"{document.document_id}-{chunk_index}",
                        document_id=document.document_id,
                        title=document.title,
                        source=document.source,
                        published_date=document.published_date,
                        section=section,
                        chunk_index=chunk_index,
                        content=" ".join(chunk_words),
                    )
                )
                chunk_index += 1

                if start + self.chunk_size >= len(words):
                    break

        return chunks

    @staticmethod
    def _split_sections(content: str) -> list[tuple[str, str]]:
        lines = [line.strip() for line in content.splitlines()]
        sections: list[tuple[str, list[str]]] = []
        current_section = "General"
        current_content: list[str] = []

        for line in lines:
            if not line:
                continue

            normalized = re.sub(r"\s+", " ", line)

            if FinancialDocumentChunker._is_heading(normalized):
                if current_content:
                    sections.append(
                        (current_section, current_content)
                    )
                    current_content = []

                current_section = normalized[:200]
            else:
                current_content.append(normalized)

        if current_content:
            sections.append((current_section, current_content))

        return [
            (section, " ".join(content))
            for section, content in sections
            if content
        ]

    @staticmethod
    def _is_heading(line: str) -> bool:
        if len(line) > 250:
            return False

        upper = line.upper()

        known_sections = (
            "RISK FACTORS",
            "BUSINESS",
            "PROPERTIES",
            "LEGAL PROCEEDINGS",
            "MARKET FOR REGISTRANT",
            "SELECTED FINANCIAL DATA",
            "MANAGEMENT'S DISCUSSION",
            "QUANTITATIVE AND QUALITATIVE DISCLOSURES",
            "FINANCIAL STATEMENTS",
            "NOTES TO FINANCIAL STATEMENTS",
            "CONTROLS AND PROCEDURES",
            "EXECUTIVE COMPENSATION",
            "SECURITY OWNERSHIP",
            "DIRECTORS",
            "MARKET RISK",
            "LIQUIDITY",
        )

        if any(section in upper for section in known_sections):
            return True

        return bool(
            re.match(
                r"^(ITEM\s+\d+[A-Z]?(?:\.|:)?\s+.+|PART\s+[IVX]+(?:\.|:)?\s+.+)$",
                upper,
            )
        )
