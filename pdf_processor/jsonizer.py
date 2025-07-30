"""
JSON processing module for converting markdown files to structured JSON.

This module provides functionality to convert processed PDF markdown files
into three different JSON formats:
1. Text and tables only (no images, references, or bibliography)
2. Full content with images
3. Metadata and references only
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator
from datetime import datetime

# Set up logging
_log = logging.getLogger(__name__)


class Reference(BaseModel):
    """Pydantic model for academic references with standardized structure."""
    
    title: Optional[str] = Field(None, description="Title of the referenced work")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: Optional[str] = Field(None, description="Journal or publication name")
    year: Optional[int] = Field(None, description="Publication year")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    isbn: Optional[str] = Field(None, description="ISBN for books")
    url: Optional[str] = Field(None, description="URL or web link")
    publisher: Optional[str] = Field(None, description="Publisher name")
    raw_text: str = Field(..., description="Original reference text")
    reference_type: str = Field(default="unknown", description="Type of reference (journal, book, website, etc.)")
    
    @validator('year')
    def validate_year(cls, v):
        if v is not None and (v < 1800 or v > datetime.now().year + 1):
            raise ValueError(f"Year must be between 1800 and {datetime.now().year + 1}")
        return v
    
    @validator('doi')
    def validate_doi(cls, v):
        if v is not None and not re.match(r'^10\.\d+/.+', v):
            # If it doesn't match standard DOI format, keep it but note it
            _log.warning(f"DOI may not be in standard format: {v}")
        return v


class DocumentMetadata(BaseModel):
    """Pydantic model for document metadata."""
    
    title: Optional[str] = Field(None, description="Document title")
    authors: List[str] = Field(default_factory=list, description="Document authors")
    abstract: Optional[str] = Field(None, description="Document abstract")
    keywords: List[str] = Field(default_factory=list, description="Document keywords")
    publication_date: Optional[str] = Field(None, description="Publication date")
    journal: Optional[str] = Field(None, description="Journal name")
    doi: Optional[str] = Field(None, description="Document DOI")
    page_count: Optional[int] = Field(None, description="Number of pages")
    language: str = Field(default="en", description="Document language")
    document_type: str = Field(default="academic_paper", description="Type of document")
    processed_date: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Processing timestamp")


@dataclass
class ProcessingStats:
    """Statistics from the JSON processing."""
    total_sections: int = 0
    total_tables: int = 0
    total_images: int = 0
    total_references: int = 0
    processing_time: float = 0.0


class MarkdownToJSONProcessor:
    """Main processor class for converting markdown to structured JSON."""
    
    def __init__(self):
        self.stats = ProcessingStats()
    
    def process_markdown_file(self, md_file_path: Union[str, Path], output_dir: Union[str, Path]) -> Dict[str, str]:
        """
        Process a markdown file and generate three JSON outputs.
        
        Args:
            md_file_path: Path to the markdown file with images
            output_dir: Directory to save the JSON files
            
        Returns:
            Dictionary with paths to the generated JSON files
        """
        start_time = datetime.now()
        
        md_path = Path(md_file_path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Read the markdown file
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        _log.info(f"Processing markdown file: {md_path}")
        
        # Parse the markdown content
        parsed_content = self._parse_markdown(markdown_content)
        
        # Generate the three JSON files
        base_name = md_path.stem
        
        # 1. Text and tables only (no images, references, bibliography)
        text_tables_json = self._create_text_tables_json(parsed_content)
        text_tables_path = output_path / f"{base_name}_text_tables.json"
        with open(text_tables_path, 'w', encoding='utf-8') as f:
            json.dump(text_tables_json, f, indent=2, ensure_ascii=False)
        
        # 2. Full content with images
        full_content_json = self._create_full_content_json(parsed_content)
        full_content_path = output_path / f"{base_name}_full_content.json"
        with open(full_content_path, 'w', encoding='utf-8') as f:
            json.dump(full_content_json, f, indent=2, ensure_ascii=False)
        
        # 3. Metadata and references only
        metadata_refs_json = self._create_metadata_references_json(parsed_content)
        metadata_refs_path = output_path / f"{base_name}_metadata_references.json"
        with open(metadata_refs_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_refs_json, f, indent=2, ensure_ascii=False)
        
        # Update processing stats
        end_time = datetime.now()
        self.stats.processing_time = (end_time - start_time).total_seconds()
        
        _log.info(f"Generated 3 JSON files in {self.stats.processing_time:.2f} seconds")
        
        return {
            "text_tables": str(text_tables_path),
            "full_content": str(full_content_path),
            "metadata_references": str(metadata_refs_path)
        }
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """Parse markdown content into structured data."""
        parsed = {
            "metadata": {},
            "sections": [],
            "tables": [],
            "images": [],
            "references": [],
            "raw_content": content
        }
        
        lines = content.split('\n')
        current_section = None
        in_table = False
        table_content = []
        in_references = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for headings
            if line.startswith('#'):
                # Save current section if exists
                if current_section:
                    parsed["sections"].append(current_section)
                
                # Determine heading level
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                # Check if this is a references section
                if any(ref_word in title.lower() for ref_word in ['reference', 'bibliography', 'citation']):
                    in_references = True
                else:
                    in_references = False
                
                current_section = {
                    "level": level,
                    "title": title,
                    "content": [],
                    "subsections": [],
                    "tables": [],
                    "images": []
                }
                continue
            
            # Check for images
            img_match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if img_match:
                alt_text, img_path = img_match.groups()
                image_data = {
                    "alt_text": alt_text,
                    "path": img_path,
                    "caption": alt_text,
                    "line_number": i + 1
                }
                parsed["images"].append(image_data)
                if current_section:
                    current_section["images"].append(image_data)
                continue
            
            # Check for table headers (markdown tables)
            if '|' in line and (i + 1 < len(lines) and '|' in lines[i + 1] and '-' in lines[i + 1]):
                in_table = True
                table_content = [line]
                continue
            
            # Continue collecting table content
            if in_table and '|' in line:
                table_content.append(line)
                continue
            elif in_table:
                # End of table
                table_data = self._parse_table(table_content)
                parsed["tables"].append(table_data)
                if current_section:
                    current_section["tables"].append(table_data)
                in_table = False
                table_content = []
                self.stats.total_tables += 1
            
            # Check for references
            if in_references and (line.startswith('- ') or line.startswith('1. ') or re.match(r'^\d+\.', line)):
                ref_text = re.sub(r'^[-\d.]\s*', '', line)
                reference = self._parse_reference(ref_text)
                parsed["references"].append(reference.dict())
                continue
            
            # Regular content
            if current_section:
                current_section["content"].append(line)
        
        # Add the last section
        if current_section:
            parsed["sections"].append(current_section)
        
        # Extract metadata from first section or content
        parsed["metadata"] = self._extract_metadata(parsed)
        
        # Update stats
        self.stats.total_sections = len(parsed["sections"])
        self.stats.total_images = len(parsed["images"])
        self.stats.total_references = len(parsed["references"])
        
        return parsed
    
    def _parse_table(self, table_lines: List[str]) -> Dict[str, Any]:
        """Parse markdown table into structured format."""
        if len(table_lines) < 2:
            return {"headers": [], "rows": [], "raw_content": '\n'.join(table_lines)}
        
        # Extract headers
        header_line = table_lines[0]
        headers = [cell.strip() for cell in header_line.split('|') if cell.strip()]
        
        # Extract rows (skip the separator line)
        rows = []
        for line in table_lines[2:]:
            if '|' in line:
                row = [cell.strip() for cell in line.split('|') if cell.strip()]
                if row:  # Only add non-empty rows
                    rows.append(row)
        
        return {
            "headers": headers,
            "rows": rows,
            "num_columns": len(headers),
            "num_rows": len(rows),
            "raw_content": '\n'.join(table_lines)
        }
    
    def _parse_reference(self, ref_text: str) -> Reference:
        """Parse a reference string into structured Reference object."""
        # Basic parsing patterns
        title_match = re.search(r'"([^"]+)"', ref_text)
        title = title_match.group(1) if title_match else None
        
        # Extract DOI
        doi_match = re.search(r'doi:?\s*([10]\.\d+/[^\s]+)', ref_text, re.IGNORECASE)
        doi = doi_match.group(1) if doi_match else None
        
        # Extract PMID
        pmid_match = re.search(r'pmid:?\s*(\d+)', ref_text, re.IGNORECASE)
        pmid = pmid_match.group(1) if pmid_match else None
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
        year = int(year_match.group()) if year_match else None
        
        # Extract authors (basic pattern - names before year or title)
        authors = []
        if title:
            author_part = ref_text.split(title)[0]
        elif year:
            author_part = ref_text.split(str(year))[0]
        else:
            author_part = ref_text[:100]  # First 100 chars as fallback
        
        # Simple author extraction (split by commas and 'and')
        if author_part:
            author_candidates = re.split(r',|\band\b', author_part)
            for author in author_candidates:
                author = author.strip().rstrip('.')
                if author and len(author) > 1 and not author.isdigit():
                    authors.append(author)
        
        # Determine reference type
        ref_type = "unknown"
        if "journal" in ref_text.lower() or doi:
            ref_type = "journal_article"
        elif "book" in ref_text.lower() or "isbn" in ref_text.lower():
            ref_type = "book"
        elif "http" in ref_text.lower() or "www" in ref_text.lower():
            ref_type = "website"
        elif "conference" in ref_text.lower() or "proceedings" in ref_text.lower():
            ref_type = "conference_paper"
        
        return Reference(
            title=title,
            authors=authors[:5],  # Limit to first 5 authors
            year=year,
            doi=doi,
            pmid=pmid,
            raw_text=ref_text,
            reference_type=ref_type
        )
    
    def _extract_metadata(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document metadata from parsed content."""
        metadata = DocumentMetadata()
        
        # Try to find title from first heading
        if parsed_content["sections"]:
            first_section = parsed_content["sections"][0]
            if first_section["level"] == 1:
                metadata.title = first_section["title"]
        
        # Count pages (rough estimate based on content length)
        content_length = len(parsed_content["raw_content"])
        metadata.page_count = max(1, content_length // 3000)  # Rough estimate
        
        # Look for abstract in early sections
        for section in parsed_content["sections"][:3]:
            if "abstract" in section["title"].lower():
                metadata.abstract = ' '.join(section["content"])
                break
        
        return metadata.dict()
    
    def _create_text_tables_json(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON with text and tables only (no images, references, bibliography)."""
        filtered_sections = []
        
        for section in parsed_content["sections"]:
            # Skip reference/bibliography sections
            if any(ref_word in section["title"].lower() for ref_word in ['reference', 'bibliography', 'citation']):
                continue
            
            # Create clean section without images
            clean_section = {
                "level": section["level"],
                "title": section["title"],
                "content": section["content"],
                "tables": section["tables"],
                "subsections": section.get("subsections", [])
            }
            filtered_sections.append(clean_section)
        
        return {
            "document_type": "text_and_tables_only",
            "metadata": parsed_content["metadata"],
            "sections": filtered_sections,
            "tables": parsed_content["tables"],
            "statistics": {
                "total_sections": len(filtered_sections),
                "total_tables": len(parsed_content["tables"]),
                "processing_date": datetime.now().isoformat()
            }
        }
    
    def _create_full_content_json(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON with full content including images."""
        return {
            "document_type": "full_content_with_images",
            "metadata": parsed_content["metadata"],
            "sections": parsed_content["sections"],
            "tables": parsed_content["tables"],
            "images": parsed_content["images"],
            "references": parsed_content["references"],
            "statistics": {
                "total_sections": len(parsed_content["sections"]),
                "total_tables": len(parsed_content["tables"]),
                "total_images": len(parsed_content["images"]),
                "total_references": len(parsed_content["references"]),
                "processing_date": datetime.now().isoformat()
            }
        }
    
    def _create_metadata_references_json(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON with metadata and references only."""
        return {
            "document_type": "metadata_and_references_only",
            "metadata": parsed_content["metadata"],
            "references": parsed_content["references"],
            "reference_statistics": {
                "total_references": len(parsed_content["references"]),
                "reference_types": self._get_reference_type_counts(parsed_content["references"]),
                "references_with_doi": len([r for r in parsed_content["references"] if r.get("doi")]),
                "references_with_pmid": len([r for r in parsed_content["references"] if r.get("pmid")])
            },
            "processing_info": {
                "processing_date": datetime.now().isoformat(),
                "total_processing_time_seconds": self.stats.processing_time
            }
        }
    
    def _get_reference_type_counts(self, references: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count references by type."""
        type_counts = {}
        for ref in references:
            ref_type = ref.get("reference_type", "unknown")
            type_counts[ref_type] = type_counts.get(ref_type, 0) + 1
        return type_counts


def process_pdf_markdown_to_json(markdown_file_path: Union[str, Path], output_dir: Union[str, Path]) -> Dict[str, str]:
    """
    Convenience function to process a markdown file and generate JSON outputs.
    
    Args:
        markdown_file_path: Path to the markdown file (should be the one with images)
        output_dir: Directory to save the JSON files
        
    Returns:
        Dictionary with paths to the generated JSON files
    """
    processor = MarkdownToJSONProcessor()
    return processor.process_markdown_file(markdown_file_path, output_dir)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python jsonizer.py <markdown_file> <output_directory>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        result = process_pdf_markdown_to_json(md_file, output_dir)
        print("Generated JSON files:")
        for file_type, file_path in result.items():
            print(f"  {file_type}: {file_path}")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
