
"""
Metadata extraction script for journal articles using OpenRouter AI agent.
This script processes the first page of a PDF (as an image) and extracts
structured metadata using vision-language models.
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from PIL import Image
import requests

# Load environment variables
load_dotenv()

# Configuration
MODEL = "google/gemini-2.5-flash-lite"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Set up logging
logging.basicConfig(level=logging.INFO)
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
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v is not None and (v < 1800 or v > datetime.now().year + 1):
            raise ValueError(f"Year must be between 1800 and {datetime.now().year + 1}")
        return v


class ArticleMetadata(BaseModel):
    """Pydantic model for journal article metadata."""
    
    title: Optional[str] = Field(None, description="Article title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: Optional[str] = Field(None, description="Journal name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range")
    year: Optional[int] = Field(None, description="Publication year")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    issn: Optional[str] = Field(None, description="ISSN")
    abstract: Optional[str] = Field(None, description="Article abstract")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    article_type: Optional[str] = Field("research_article", description="Type of article")
    publisher: Optional[str] = Field(None, description="Publisher name")
    url: Optional[str] = Field(None, description="Article URL")
    citation_info: Optional[str] = Field(None, description="Full citation information")
    extracted_date: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Extraction timestamp")
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v is not None and (v < 1800 or v > datetime.now().year + 1):
            raise ValueError(f"Year must be between 1800 and {datetime.now().year + 1}")
        return v


class MetadataExtractor:
    """Class for extracting metadata from journal article images using AI."""
    
    def __init__(self, model_name: str = MODEL):
        """Initialize the metadata extractor with OpenRouter AI."""
        self.model_name = model_name
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            _log.error(f"Error encoding image {image_path}: {e}")
            raise
    
    def extract_metadata_from_image(self, image_path: str) -> ArticleMetadata:
        """
        Extract article metadata from the first page image using AI vision.
        
        Args:
            image_path: Path to the first page image of the article
            
        Returns:
            ArticleMetadata object with extracted information
        """
        _log.info(f"Extracting metadata from image: {image_path}")
        
        # Encode image to base64
        base64_image = self.encode_image_to_base64(image_path)
        
        # Determine image type from file extension
        image_ext = Path(image_path).suffix.lower()
        if image_ext in ['.jpg', '.jpeg']:
            data_url = f"data:image/jpeg;base64,{base64_image}"
        elif image_ext == '.png':
            data_url = f"data:image/png;base64,{base64_image}"
        else:
            data_url = f"data:image/png;base64,{base64_image}"  # Default to PNG
        
        # Create the system prompt for metadata extraction
        system_prompt = """You are an expert academic librarian and metadata extraction specialist. 
        Your task is to analyze the first page of a journal article and extract comprehensive metadata.
        
        Please extract the following information from the article image:
        1. Article title (complete and accurate)
        2. All authors (in order, full names if available)
        3. Journal name
        4. Volume number
        5. Issue number
        6. Page range
        7. Publication year
        8. DOI (Digital Object Identifier)
        9. PubMed ID (if visible)
        10. ISSN (if visible)
        11. Abstract text (if visible on this page)
        12. Keywords (if listed on this page)
        13. Article type (research article, review, case study, etc.)
        14. Publisher name
        15. Any URLs visible
        
        Return the information in a structured JSON format that matches this schema:
        {
            "title": "string",
            "authors": ["string"],
            "journal": "string",
            "volume": "string",
            "issue": "string", 
            "pages": "string",
            "year": integer,
            "doi": "string",
            "pmid": "string",
            "issn": "string",
            "abstract": "string",
            "keywords": ["string"],
            "article_type": "string",
            "publisher": "string",
            "url": "string",
            "citation_info": "string"
        }
        
        Guidelines:
        - Be precise and accurate
        - If information is not visible or unclear, use null
        - Extract text exactly as it appears
        - For authors, maintain the order and format shown
        - For DOI, include the full identifier
        - For citation_info, provide a complete citation string if possible
        """
        
        # Create the user message with image
        user_prompt = """Please analyze this journal article first page image and extract all available metadata. 
        Look carefully at all visible text in the image including title, authors, journal name, dates, DOI, and any other bibliographic information.
        Extract only information that you can clearly see and read in the image. Return only valid JSON without any additional text or explanation."""
        
        try:
            # Set up headers for OpenRouter API
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Create messages for OpenRouter API
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ]
            
            # Create payload for OpenRouter API
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.1,  # Low temperature for consistent extraction
                "max_tokens": 4000
            }
            
            # Send request to OpenRouter AI
            _log.info("Sending request to OpenRouter AI...")
            response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API request failed with status {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Extract content from response
            if 'choices' not in response_data or not response_data['choices']:
                raise ValueError("No choices in API response")
            
            response_content = response_data['choices'][0]['message']['content'].strip()
            _log.info(f"AI Response received: {len(response_content)} characters")
            
            # Log the actual response for debugging
            _log.info(f"Raw AI response: {response_content}")
            
            # Try to extract JSON from the response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = response_content[json_start:json_end]
            _log.info(f"Extracted JSON: {json_str}")
            metadata_dict = json.loads(json_str)
            
            # Handle null values for required fields
            if metadata_dict.get('title') is None:
                metadata_dict['title'] = "Title not extracted"
            if metadata_dict.get('article_type') is None:
                metadata_dict['article_type'] = "research_article"
            
            # Create and validate the ArticleMetadata object
            metadata = ArticleMetadata(**metadata_dict)
            _log.info("Successfully extracted and validated metadata")
            
            return metadata
            
        except json.JSONDecodeError as e:
            _log.error(f"Failed to parse JSON from AI response: {e}")
            _log.error(f"Response content: {response_content}")
            raise
        except Exception as e:
            _log.error(f"Error during metadata extraction: {e}")
            raise
    
    def save_metadata_to_json(self, metadata: ArticleMetadata, output_path: str) -> str:
        """
        Save metadata to JSON file.
        
        Args:
            metadata: ArticleMetadata object
            output_path: Path to save the JSON file
            
        Returns:
            Path to the saved JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and save
        metadata_dict = metadata.model_dump()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        
        _log.info(f"Metadata saved to: {output_file}")
        return str(output_file)
    
    def process_pdf_first_page(self, image_path: str, output_dir: str = "./metadata_output") -> Dict[str, Any]:
        """
        Complete workflow to extract metadata from PDF first page image.
        
        Args:
            image_path: Path to the first page image
            output_dir: Directory to save the output JSON
            
        Returns:
            Dictionary with processing results
        """
        try:
            start_time = datetime.now()
            
            # Extract metadata
            metadata = self.extract_metadata_from_image(image_path)
            
            # Prepare output filename
            image_name = Path(image_path).stem
            json_filename = f"{image_name}_metadata.json"
            json_path = Path(output_dir) / json_filename
            
            # Save to JSON
            saved_path = self.save_metadata_to_json(metadata, str(json_path))
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            results = {
                "success": True,
                "metadata": metadata.model_dump(),
                "json_file_path": saved_path,
                "processing_time_seconds": processing_time,
                "extracted_fields": len([v for v in metadata.model_dump().values() if v is not None and v != [] and v != ""]),
                "extraction_timestamp": end_time.isoformat()
            }
            
            _log.info(f"Processing completed in {processing_time:.2f} seconds")
            return results
            
        except Exception as e:
            _log.error(f"Error in processing workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "extraction_timestamp": datetime.now().isoformat()
            }


def extract_metadata_from_pdf_page(image_path: str, output_dir: str = "./metadata_output") -> Dict[str, Any]:
    """
    Convenience function to extract metadata from a PDF first page image.
    
    Args:
        image_path: Path to the first page image
        output_dir: Directory to save the output JSON
        
    Returns:
        Dictionary with processing results
    """
    extractor = MetadataExtractor()
    return extractor.process_pdf_first_page(image_path, output_dir)


# Test functionality
if __name__ == "__main__":
    """Test the metadata extraction functionality with actual PDF page image."""
    
    # Test configuration using the actual PDF page from output directory
    test_image_path = "./output/tmpawoe9zoo/tmpawoe9zoo-page-1.png"
    test_output_dir = "./test_metadata_output"
    
    print("🧪 Testing Metadata Extraction System with Real PDF Page")
    print(f"Model: {MODEL}")
    print(f"Test image: {test_image_path}")
    print("-" * 70)
    
    # Check if test image exists
    if not Path(test_image_path).exists():
        print(f"❌ Test image not found: {test_image_path}")
        print("Available images in output directory:")
        
        # List available images
        output_dir = Path("./output")
        if output_dir.exists():
            for subdir in output_dir.iterdir():
                if subdir.is_dir():
                    print(f"\n📁 {subdir.name}:")
                    for file in subdir.glob("*page-1*"):
                        print(f"  📄 {file.name}")
        
        print("\n💡 Tip: Update 'test_image_path' with an available image path")
        
    else:
        try:
            print("🚀 Starting metadata extraction test...")
            
            # Check if API key is available
            if not OPENROUTER_API_KEY:
                print("❌ OPENROUTER_API_KEY environment variable not set!")
                print("💡 Please set your OpenRouter API key in the .env file")
                print("Example: OPENROUTER_API_KEY=your_api_key_here")
                exit(1)
            
            # Run the extraction
            print("🔍 Initializing MetadataExtractor...")
            extractor = MetadataExtractor()
            
            print("📸 Processing image with AI vision...")
            results = extractor.process_pdf_first_page(test_image_path, test_output_dir)
            
            if results["success"]:
                print("✅ Metadata extraction successful!")
                print(f"📊 Extracted {results['extracted_fields']} fields")
                print(f"⏱️ Processing time: {results['processing_time_seconds']:.2f} seconds")
                print(f"💾 JSON saved to: {results['json_file_path']}")
                
                # Display key extracted information
                metadata = results["metadata"]
                print("\n" + "="*50)
                print("📄 EXTRACTED METADATA:")
                print("="*50)
                print(f"📌 Title: {metadata.get('title', 'N/A')}")
                print(f"👥 Authors: {', '.join(metadata.get('authors', []))}")
                print(f"📚 Journal: {metadata.get('journal', 'N/A')}")
                print(f"📅 Year: {metadata.get('year', 'N/A')}")
                print(f"🔗 DOI: {metadata.get('doi', 'N/A')}")
                print(f"📖 Volume: {metadata.get('volume', 'N/A')}")
                print(f"📄 Pages: {metadata.get('pages', 'N/A')}")
                print(f"🏢 Publisher: {metadata.get('publisher', 'N/A')}")
                print(f"🏷️ Article Type: {metadata.get('article_type', 'N/A')}")
                
                if metadata.get('abstract'):
                    print(f"📝 Abstract: {metadata.get('abstract', 'N/A')[:200]}...")
                
                if metadata.get('keywords'):
                    print(f"🔑 Keywords: {', '.join(metadata.get('keywords', []))}")
                
                # Test JSON file integrity
                print("\n🔍 Testing JSON file integrity...")
                with open(results['json_file_path'], 'r', encoding='utf-8') as f:
                    loaded_metadata = json.load(f)
                    validated_metadata = ArticleMetadata(**loaded_metadata)
                    print("✅ JSON file is valid and can be loaded back into ArticleMetadata model")
                
                # Show JSON file location
                print(f"\n📁 Full JSON output available at: {Path(results['json_file_path']).absolute()}")
                
            else:
                print(f"❌ Metadata extraction failed: {results['error']}")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("🏁 Test completed!")
    
    # Usage instructions
    print("\n📖 USAGE INSTRUCTIONS:")
    print("-" * 30)
    print("1. Ensure OPENROUTER_API_KEY is set in your .env file")
    print("2. Place journal article first page images in the test directory")
    print("3. Update 'test_image_path' variable with your image filename")
    print("4. Run: python metadata.py")
    print("5. Check the output JSON file for extracted metadata")
    
    print("\n🔧 ENVIRONMENT REQUIREMENTS:")
    print("-" * 35)
    print("✓ OPENROUTER_API_KEY environment variable set")
    print("✓ Internet connection for API calls")
    print("✓ PIL (Pillow) for image processing")
    print("✓ requests library for API communication")
    print("✓ pydantic for data validation")
    
    print("\n🎯 SUPPORTED IMAGE FORMATS:")
    print("-" * 30)
    print("✓ PNG (.png)")
    print("✓ JPEG (.jpg, .jpeg)")
    
    print("\n💡 TIP: The AI model works best with:")
    print("- High-resolution, clear images")
    print("- Complete first page of journal articles")
    print("- Images with visible text (title, authors, journal info)")
    print("- PDF pages that include abstracts and metadata")
    