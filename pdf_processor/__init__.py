"""
PDF processing package using Docling for advanced document analysis.

This package provides comprehensive PDF processing capabilities including:
- Text extraction
- Image and figure extraction
- Table detection and extraction
- Multiple output formats (Markdown, HTML, Text)
- High-quality OCR and layout analysis
"""

from .main_pdf_processor import PDFProcessor

__all__ = ["PDFProcessor"]
