import logging
import time
from pathlib import Path
import os
from typing import Optional, Dict, Any

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Set up logging
_log = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processor using Docling for advanced document processing."""
    
    def __init__(self, image_resolution_scale: float = 2.0):
        """
        Initialize the PDF processor.
        
        Args:
            image_resolution_scale: Scale for image resolution (2.0 = high quality)
        """
        self.image_resolution_scale = image_resolution_scale
        self.doc_converter = self._setup_converter()
    
    def _setup_converter(self) -> DocumentConverter:
        """Set up the document converter with PDF pipeline options."""
        # Configure pipeline options for comprehensive document processing
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = self.image_resolution_scale
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True
        
        # Create document converter with PDF format options
        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        return doc_converter
    
    def process_pdf(self, input_pdf_path: str, output_base_dir: str = "output") -> Dict[str, Any]:
        """
        Process a PDF file and extract all content, images, tables, and figures.
        
        Args:
            input_pdf_path: Path to the input PDF file
            output_base_dir: Base directory for output files
            
        Returns:
            Dictionary containing processing results and metadata
        """
        try:
            input_path = Path(input_pdf_path)
            if not input_path.exists():
                raise FileNotFoundError(f"PDF file not found: {input_pdf_path}")
            
            # Create output directory based on PDF filename
            pdf_name = input_path.stem
            output_dir = Path(output_base_dir) / pdf_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            _log.info(f"Processing PDF: {input_pdf_path}")
            _log.info(f"Output directory: {output_dir}")
            
            start_time = time.time()
            
            # Convert the document
            conv_res = self.doc_converter.convert(input_path)
            
            # Initialize counters and results
            results = {
                "pdf_name": pdf_name,
                "output_dir": str(output_dir),
                "page_count": len(conv_res.document.pages),
                "table_count": 0,
                "picture_count": 0,
                "page_images": [],
                "table_images": [],
                "picture_images": [],
                "markdown_files": [],
                "html_files": [],
                "processing_time": 0
            }
            
            # Save page images
            for page_no, page in conv_res.document.pages.items():
                page_image_filename = output_dir / f"{pdf_name}-page-{page_no}.png"
                with page_image_filename.open("wb") as fp:
                    page.image.pil_image.save(fp, format="PNG")
                results["page_images"].append(str(page_image_filename))
                _log.info(f"Saved page image: {page_image_filename}")
            
            # Process and save images of figures and tables
            table_counter = 0
            picture_counter = 0
            
            for element, _level in conv_res.document.iterate_items():
                if isinstance(element, TableItem):
                    table_counter += 1
                    table_image_filename = output_dir / f"{pdf_name}-table-{table_counter}.png"
                    with table_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")
                    results["table_images"].append(str(table_image_filename))
                    _log.info(f"Saved table image: {table_image_filename}")
                
                if isinstance(element, PictureItem):
                    picture_counter += 1
                    picture_image_filename = output_dir / f"{pdf_name}-picture-{picture_counter}.png"
                    with picture_image_filename.open("wb") as fp:
                        element.get_image(conv_res.document).save(fp, "PNG")
                    results["picture_images"].append(str(picture_image_filename))
                    _log.info(f"Saved picture image: {picture_image_filename}")
            
            results["table_count"] = table_counter
            results["picture_count"] = picture_counter
            
            # Save markdown with embedded pictures
            md_embedded_filename = output_dir / f"{pdf_name}-with-images.md"
            conv_res.document.save_as_markdown(md_embedded_filename, image_mode=ImageRefMode.EMBEDDED)
            results["markdown_files"].append(str(md_embedded_filename))
            _log.info(f"Saved embedded markdown: {md_embedded_filename}")
            
            # Save markdown with externally referenced pictures
            md_refs_filename = output_dir / f"{pdf_name}-with-image-refs.md"
            conv_res.document.save_as_markdown(md_refs_filename, image_mode=ImageRefMode.REFERENCED)
            results["markdown_files"].append(str(md_refs_filename))
            _log.info(f"Saved referenced markdown: {md_refs_filename}")
            
            # Save HTML with externally referenced pictures
            html_filename = output_dir / f"{pdf_name}-with-image-refs.html"
            conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)
            results["html_files"].append(str(html_filename))
            _log.info(f"Saved HTML: {html_filename}")
            
            # Save plain text version
            txt_filename = output_dir / f"{pdf_name}-text.txt"
            with txt_filename.open("w", encoding="utf-8") as fp:
                fp.write(conv_res.document.export_to_text())
            results["text_file"] = str(txt_filename)
            _log.info(f"Saved text: {txt_filename}")
            
            end_time = time.time() - start_time
            results["processing_time"] = end_time
            
            _log.info(f"Document '{pdf_name}' processed successfully in {end_time:.2f} seconds.")
            _log.info(f"Extracted {results['page_count']} pages, {results['table_count']} tables, {results['picture_count']} pictures")
            
            return results
            
        except Exception as e:
            _log.error(f"Error processing PDF {input_pdf_path}: {str(e)}")
            raise
    
    def process_pdf_simple(self, input_pdf_path: str, output_base_dir: str = "output") -> str:
        """
        Simple PDF processing that returns just the text content.
        
        Args:
            input_pdf_path: Path to the input PDF file
            output_base_dir: Base directory for output files
            
        Returns:
            Extracted text content
        """
        try:
            input_path = Path(input_pdf_path)
            conv_res = self.doc_converter.convert(input_path)
            return conv_res.document.export_to_text()
        except Exception as e:
            _log.error(f"Error in simple PDF processing {input_pdf_path}: {str(e)}")
            raise


def main():
    """Example usage of the PDF processor."""
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    processor = PDFProcessor()
    
    # This would be used with an actual PDF file
    # results = processor.process_pdf("sample.pdf", "output")
    # print(f"Processing results: {results}")


if __name__ == "__main__":
    main()
