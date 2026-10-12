import io
from typing import List, Dict, Any, Tuple
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class FileProcessor:
    """Handles parsing and reconstructing .docx and .txt files while preserving styling."""

    @staticmethod
    def extract_from_txt(content_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """Extracts text and paragraph breakdown from .txt content with encoding fallbacks."""
        text = ""
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text = content_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        paragraphs = []
        raw_lines = text.splitlines()
        for idx, line in enumerate(raw_lines):
            stripped = line.strip()
            if stripped:
                paragraphs.append({
                    "id": idx,
                    "text": line,
                    "is_heading": False,
                    "is_bullet": stripped.startswith(("-", "*", "•")),
                    "style": "Normal"
                })
        return text, paragraphs

    @staticmethod
    def extract_from_docx(content_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """Extracts text and paragraph structure from a .docx file."""
        doc = Document(io.BytesIO(content_bytes))
        full_text_parts = []
        paragraphs_meta = []

        for idx, p in enumerate(doc.paragraphs):
            p_text = p.text
            stripped = p_text.strip()
            if not stripped:
                continue

            full_text_parts.append(p_text)
            style_name = p.style.name if p.style else "Normal"
            is_heading = "heading" in style_name.lower() or "title" in style_name.lower()
            is_bullet = "list" in style_name.lower() or stripped.startswith(("-", "*", "•"))

            # Capture run-level styling hints
            runs_info = []
            for r in p.runs:
                runs_info.append({
                    "text": r.text,
                    "bold": bool(r.bold),
                    "italic": bool(r.italic),
                    "underline": bool(r.underline)
                })

            paragraphs_meta.append({
                "id": idx,
                "text": p_text,
                "is_heading": is_heading,
                "is_bullet": is_bullet,
                "style": style_name,
                "runs": runs_info
            })

        return "\n\n".join(full_text_parts), paragraphs_meta

    @staticmethod
    def reconstruct_txt(paragraphs: List[Dict[str, Any]]) -> bytes:
        """Reconstructs text into .txt byte stream."""
        lines = [p.get("text", "") for p in paragraphs]
        output_str = "\n\n".join(lines)
        return output_str.encode("utf-8")

    @staticmethod
    def reconstruct_docx(original_bytes: bytes, replacement_paragraphs: List[Dict[str, Any]]) -> bytes:
        """
        Reconstructs a .docx document replacing existing paragraph contents with new text
        while maintaining paragraph styles, heading tags, and formatting attributes.
        """
        if not original_bytes:
            # Create a brand new formatted docx
            doc = Document()
            for p_info in replacement_paragraphs:
                text = p_info.get("text", "").strip()
                if not text:
                    continue
                if p_info.get("is_heading"):
                    style = p_info.get("style", "Heading 1")
                    try:
                        doc.add_paragraph(text, style=style)
                    except Exception:
                        doc.add_heading(text, level=1)
                elif p_info.get("is_bullet"):
                    doc.add_paragraph(text, style="List Bullet")
                else:
                    doc.add_paragraph(text, style="Normal")
            output_io = io.BytesIO()
            doc.save(output_io)
            output_io.seek(0)
            return output_io.getvalue()

        # Update the original document in-place to preserve margins, headers, styles
        doc = Document(io.BytesIO(original_bytes))
        non_empty_doc_paras = [p for p in doc.paragraphs if p.text.strip()]

        for i, new_p_info in enumerate(replacement_paragraphs):
            new_text = new_p_info.get("text", "")
            if i < len(non_empty_doc_paras):
                target_p = non_empty_doc_paras[i]
                # Keep font/color from first run if available
                first_run_font_name = None
                first_run_font_size = None
                if target_p.runs:
                    first_run = target_p.runs[0]
                    first_run_font_name = first_run.font.name
                    first_run_font_size = first_run.font.size

                # Clear existing runs
                p_elem = target_p._element
                for r_elem in list(target_p.runs):
                    p_elem.remove(r_elem._r)

                # Add new text run
                new_run = target_p.add_run(new_text)
                if first_run_font_name:
                    new_run.font.name = first_run_font_name
                if first_run_font_size:
                    new_run.font.size = first_run_font_size
            else:
                # Append new paragraph if replacement has more entries
                style = new_p_info.get("style", "Normal")
                try:
                    doc.add_paragraph(new_text, style=style)
                except Exception:
                    doc.add_paragraph(new_text)

        output_io = io.BytesIO()
        doc.save(output_io)
        output_io.seek(0)
        return output_io.getvalue()
