import io
from typing import List, Dict, Any, Tuple
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

class FileProcessor:
    """Handles parsing and reconstructing .docx and .txt files while preserving styling and tables."""

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
                    "is_table_cell": False,
                    "style": "Normal"
                })
        return text, paragraphs

    @staticmethod
    def extract_from_docx(content_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """Extracts text, paragraph structure, and non-empty table cells from a .docx file."""
        doc = Document(io.BytesIO(content_bytes))
        full_text_parts = []
        paragraphs_meta = []
        item_counter = 0

        # 1. Extract regular paragraphs
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
                "id": item_counter,
                "para_idx": idx,
                "text": p_text,
                "is_heading": is_heading,
                "is_bullet": is_bullet,
                "is_table_cell": False,
                "style": style_name,
                "runs": runs_info
            })
            item_counter += 1

        # 2. Extract non-empty prose table cells (e.g. comparison tables, research gap tables)
        seen_cells = set()
        for t_idx, table in enumerate(doc.tables):
            for r_idx, row in enumerate(table.rows):
                for c_idx, cell in enumerate(row.cells):
                    c_text = cell.text.strip()
                    if c_text and c_text not in seen_cells and len(c_text.split()) > 3:
                        seen_cells.add(c_text)
                        full_text_parts.append(c_text)
                        paragraphs_meta.append({
                            "id": item_counter,
                            "is_table_cell": True,
                            "table_idx": t_idx,
                            "row_idx": r_idx,
                            "col_idx": c_idx,
                            "text": c_text,
                            "is_heading": False,
                            "is_bullet": False,
                            "style": "Table Cell"
                        })
                        item_counter += 1

        return "\n\n".join(full_text_parts), paragraphs_meta

    @staticmethod
    def reconstruct_txt(paragraphs: List[Dict[str, Any]]) -> bytes:
        """Reconstructs text into .txt byte stream."""
        lines = [p.get("text", "") for p in paragraphs if not p.get("is_table_cell")]
        output_str = "\n\n".join(lines)
        return output_str.encode("utf-8")

    @staticmethod
    def reconstruct_docx(original_bytes: bytes, replacement_paragraphs: List[Dict[str, Any]]) -> bytes:
        """
        Reconstructs a .docx document replacing existing paragraph contents with new text
        while maintaining paragraph styles, heading tags, formatting attributes, and table structures.
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

        for p_info in replacement_paragraphs:
            new_text = p_info.get("text", "")
            if p_info.get("is_table_cell"):
                t_idx = p_info.get("table_idx")
                r_idx = p_info.get("row_idx")
                c_idx = p_info.get("col_idx")
                if t_idx is not None and t_idx < len(doc.tables):
                    table = doc.tables[t_idx]
                    if r_idx < len(table.rows) and c_idx < len(table.rows[r_idx].cells):
                        table.rows[r_idx].cells[c_idx].text = new_text
            else:
                p_idx = p_info.get("para_idx")
                if p_idx is not None and p_idx < len(doc.paragraphs):
                    target_p = doc.paragraphs[p_idx]
                elif p_info.get("id", 0) < len(non_empty_doc_paras):
                    target_p = non_empty_doc_paras[p_info.get("id", 0)]
                else:
                    target_p = None

                if target_p is not None:
                    first_run_font_name = None
                    first_run_font_size = None
                    if target_p.runs:
                        first_run = target_p.runs[0]
                        first_run_font_name = first_run.font.name
                        first_run_font_size = first_run.font.size

                    p_elem = target_p._element
                    for r_elem in list(target_p.runs):
                        p_elem.remove(r_elem._r)

                    new_run = target_p.add_run(new_text)
                    if first_run_font_name:
                        new_run.font.name = first_run_font_name
                    if first_run_font_size:
                        new_run.font.size = first_run_font_size

        output_io = io.BytesIO()
        doc.save(output_io)
        output_io.seek(0)
        return output_io.getvalue()
