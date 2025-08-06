import os
import io
import gc
import tempfile
from typing import List, Dict, Any
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import pypdf
import google.generativeai as genai
from src.utils.memory_manager import MemoryManager, chunk_text, StreamingProcessor
from src.training.enhanced_model import EnhancedQueryProcessor

hackrx_unified_bp = Blueprint("hackrx_unified", __name__)

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("⚠️ Warning: GOOGLE_API_KEY environment variable not set")
else:
    genai.configure(api_key=api_key)

class EnhancedPDFProcessor:
    """Enhanced memory-efficient PDF processor with better text extraction"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
    
    @MemoryManager.cleanup_decorator
    def download_pdf(self, url: str) -> bytes:
        """Download PDF from URL with memory optimization"""
        try:
            # Set headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, stream=True, timeout=60, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                # Try anyway, some servers don't set correct content-type
                pass
            
            # Check content length to avoid downloading huge files
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
                raise ValueError("PDF file too large (>50MB)")
            
            # Read in chunks to manage memory
            pdf_data = io.BytesIO()
            total_size = 0
            max_size = 50 * 1024 * 1024  # 50MB limit
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    total_size += len(chunk)
                    if total_size > max_size:
                        pdf_data.close()
                        raise ValueError("PDF file too large (>50MB)")
                    
                    pdf_data.write(chunk)
                    
                    # Check memory usage periodically
                    if total_size % (1024 * 1024) == 0:  # Every MB
                        if not self.memory_manager.memory_limit_check(400):  # 400MB limit
                            pdf_data.close()
                            raise MemoryError("Memory limit exceeded during download")
            
            pdf_bytes = pdf_data.getvalue()
            pdf_data.close()
            
            return pdf_bytes
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing PDF download: {str(e)}")
    
    @MemoryManager.cleanup_decorator
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Enhanced text extraction from PDF bytes with better cleaning"""
        try:
            # Use BytesIO to avoid writing to disk
            pdf_stream = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(pdf_stream)
            
            # Check number of pages
            num_pages = len(reader.pages)
            if num_pages > 500:  # Limit pages to prevent memory issues
                print(f"Warning: PDF has {num_pages} pages, processing first 500 only")
                num_pages = 500
            
            text_parts = []
            for page_num in range(min(num_pages, len(reader.pages))):
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        # Enhanced text cleaning
                        cleaned_text = self._clean_extracted_text(page_text.strip())
                        if cleaned_text:
                            text_parts.append(cleaned_text)
                    
                    # Clear page from memory
                    del page
                    
                    # Garbage collect every 10 pages and check memory
                    if page_num % 10 == 0:
                        gc.collect()
                        if not self.memory_manager.memory_limit_check(400):
                            print(f"Memory limit reached at page {page_num}, stopping extraction")
                            break
                        
                except Exception as e:
                    print(f"Warning: Failed to extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            # Clean up
            pdf_stream.close()
            del reader
            gc.collect()
            
            if not text_parts:
                raise Exception("No text could be extracted from the PDF")
            
            # Join text parts efficiently with better formatting
            full_text = "\n\n".join(text_parts)
            del text_parts
            
            # Enhanced text post-processing
            full_text = self._post_process_text(full_text)
            
            # Limit text length to prevent memory issues (increased for better accuracy)
            max_text_length = 250000  # Increased from 200KB to 250KB
            if len(full_text) > max_text_length:
                full_text = full_text[:max_text_length] + "\n\n[Document truncated due to length]"
            
            return full_text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text from PDF"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts - using raw string for regex
        text = re.sub(r'[^\w\s.,:;!?-()[\]{}"\'/\\@#$%^&*+=<>~`|\\]', '', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # In some contexts
        
        return text.strip()
    
    def _post_process_text(self, text: str) -> str:
        """Post-process extracted text for better readability"""
        import re
        
        # Fix line breaks and spacing
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple line breaks to double
        text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)  # Sentence boundaries
        
        # Fix common formatting issues
        text = re.sub(r'\s+([.,:;!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', text)  # Add space after sentence end
        
        return text

# Initialize enhanced processor with training data
training_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "training_data", "raw_dataset.json")
enhanced_processor = None

try:
    if os.path.exists(training_data_path):
        enhanced_processor = EnhancedQueryProcessor(training_data_path)
        print("✅ Enhanced processor initialized with training data")
    else:
        enhanced_processor = EnhancedQueryProcessor()
        print("⚠️ Enhanced processor initialized without training data")
except Exception as e:
    print(f"⚠️ Error initializing enhanced processor: {str(e)}")
    enhanced_processor = EnhancedQueryProcessor()

@hackrx_unified_bp.route('/run', methods=['POST'])
@cross_origin()
def hackrx_unified_run():
    """Unified HackRX API endpoint with all improvements"""
    memory_manager = MemoryManager()
    
    try:
        # Log initial memory usage
        initial_memory = memory_manager.get_memory_usage()
        print(f"Initial memory usage: {initial_memory['rss_mb']:.2f}MB")
        
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        if 'documents' not in data:
            return jsonify({'error': 'documents field is required'}), 400
        
        if 'questions' not in data:
            return jsonify({'error': 'questions field is required'}), 400
        
        documents_url = data['documents']
        questions = data['questions']
        
        # Validate inputs
        if not isinstance(documents_url, str) or not documents_url.strip():
            return jsonify({'error': 'documents must be a valid URL string'}), 400
        
        if not isinstance(questions, list) or len(questions) == 0:
            return jsonify({'error': 'questions must be a non-empty list'}), 400
        
        if len(questions) > 25:  # Increased limit for enhanced model
            return jsonify({'error': 'Maximum 25 questions allowed'}), 400
        
        # Validate each question
        for i, question in enumerate(questions):
            if not isinstance(question, str) or not question.strip():
                return jsonify({'error': f'Question {i+1} must be a non-empty string'}), 400
            if len(question) > 1500:  # Increased limit
                return jsonify({'error': f'Question {i+1} too long (max 1500 characters)'}), 400
        
        # Process PDF with enhanced processor
        try:
            print("Starting enhanced PDF processing...")
            pdf_processor = EnhancedPDFProcessor()
            pdf_bytes = pdf_processor.download_pdf(documents_url)
            
            # Check memory after download
            memory_after_download = memory_manager.get_memory_usage()
            print(f"Memory after PDF download: {memory_after_download['rss_mb']:.2f}MB")
            
            document_text = pdf_processor.extract_text_from_pdf(pdf_bytes)
            
            # Clear PDF bytes from memory immediately
            del pdf_bytes
            gc.collect()
            
            print(f"Extracted text length: {len(document_text)} characters")
            
        except Exception as e:
            return jsonify({'error': f'PDF processing failed: {str(e)}'}), 400
        
        # Process queries with enhanced model
        try:
            print("Starting enhanced query processing...")
            
            if enhanced_processor:
                answers = enhanced_processor.batch_process_queries(document_text, questions)
            else:
                # Fallback to basic processing
                answers = []
                for question in questions:
                    answers.append("Enhanced processor not available")
            
            # Clear document text from memory
            del document_text
            gc.collect()
            
            print("Enhanced query processing completed")
            
        except Exception as e:
            return jsonify({'error': f'Query processing failed: {str(e)}'}), 500
        
        # Validate response
        if len(answers) != len(questions):
            return jsonify({'error': 'Mismatch between number of questions and answers'}), 500
        
        # Final memory check
        final_memory = memory_manager.get_memory_usage()
        print(f"Final memory usage: {final_memory['rss_mb']:.2f}MB")
        
        response = {
            'answers': answers,
            'model_info': {
                'model_name': 'gemini-1.5-pro-latest',
                'enhanced_features': [
                    'Document similarity matching',
                    'Enhanced prompt engineering',
                    'Post-processing optimization',
                    'Improved text extraction'
                ],
                'training_documents': len(enhanced_processor.training_data) if enhanced_processor else 0
            }
        }
        
        return jsonify(response), 200
        
    except MemoryError as e:
        memory_manager.force_garbage_collection()
        return jsonify({'error': f'Memory limit exceeded: {str(e)}'}), 507
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Unexpected error in hackrx_unified_run: {str(e)}")
        memory_manager.force_garbage_collection()
        return jsonify({'error': 'Internal server error'}), 500

@hackrx_unified_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check_unified():
    """Unified health check endpoint"""
    memory_manager = MemoryManager()
    memory_usage = memory_manager.get_memory_usage()
    
    return jsonify({
        'status': 'healthy',
        'service': 'HackRX Unified API',
        'version': '3.0.0',
        'model': 'gemini-1.5-pro-latest',
        'memory_usage_mb': round(memory_usage['rss_mb'], 2),
        'memory_percent': round(memory_usage['percent'], 2),
        'enhanced_features': [
            'Document similarity matching',
            'Enhanced prompt engineering',
            'Post-processing optimization',
            'Improved text extraction',
            'Training data integration'
        ],
        'training_documents': len(enhanced_processor.training_data) if enhanced_processor else 0
    }), 200