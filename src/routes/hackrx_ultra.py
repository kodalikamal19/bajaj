import os
import io
import gc
import time
from typing import List, Dict, Any
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import pypdf
import google.generativeai as genai
from src.utils.memory_manager import MemoryManager, chunk_text, StreamingProcessor
from src.training.enhanced_model import EnhancedQueryProcessor
from src.optimization.performance_optimizer import PerformanceOptimizer, ResponseCompressor

hackrx_ultra_bp = Blueprint("hackrx_ultra", __name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize global components
performance_optimizer = PerformanceOptimizer()
response_compressor = ResponseCompressor()

class UltraOptimizedPDFProcessor:
    """Ultra-optimized PDF processor with maximum efficiency"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.optimizer = performance_optimizer
    
    @MemoryManager.cleanup_decorator
    @performance_optimizer.time_function
    def download_pdf(self, url: str) -> bytes:
        """Ultra-optimized PDF download"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # Optimized request with shorter timeout for faster failure
            response = requests.get(url, stream=True, timeout=45, headers=headers)
            response.raise_for_status()
            
            # Quick content validation
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                print("Warning: Content type may not be PDF, proceeding anyway")
            
            # Optimized size check
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 50 * 1024 * 1024:
                raise ValueError("PDF file too large (>50MB)")
            
            # Ultra-efficient chunked reading
            pdf_data = io.BytesIO()
            total_size = 0
            max_size = 50 * 1024 * 1024
            chunk_size = 16384  # Increased chunk size for better performance
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    total_size += len(chunk)
                    if total_size > max_size:
                        pdf_data.close()
                        raise ValueError("PDF file too large (>50MB)")
                    
                    pdf_data.write(chunk)
                    
                    # Less frequent memory checks for better performance
                    if total_size % (2 * 1024 * 1024) == 0:  # Every 2MB
                        if not self.memory_manager.memory_limit_check(450):
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
    @performance_optimizer.time_function
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Ultra-optimized text extraction with advanced cleaning"""
        try:
            pdf_stream = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(pdf_stream)
            
            num_pages = len(reader.pages)
            if num_pages > 600:  # Increased page limit
                print(f"Warning: PDF has {num_pages} pages, processing first 600 only")
                num_pages = 600
            
            text_parts = []
            batch_size = 20  # Process pages in batches for better memory management
            
            for batch_start in range(0, min(num_pages, len(reader.pages)), batch_size):
                batch_end = min(batch_start + batch_size, num_pages)
                batch_texts = []
                
                for page_num in range(batch_start, batch_end):
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if page_text and page_text.strip():
                            # Ultra-fast text cleaning
                            cleaned_text = self.optimizer.optimize_text_processing(page_text.strip())
                            if cleaned_text and len(cleaned_text) > 20:  # Skip very short extracts
                                batch_texts.append(cleaned_text)
                        
                        del page
                        
                    except Exception as e:
                        print(f"Warning: Failed to extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                if batch_texts:
                    text_parts.extend(batch_texts)
                
                # Batch memory management
                gc.collect()
                if not self.memory_manager.memory_limit_check(450):
                    print(f"Memory limit reached at batch {batch_start//batch_size + 1}, stopping extraction")
                    break
            
            pdf_stream.close()
            del reader
            gc.collect()
            
            if not text_parts:
                raise Exception("No text could be extracted from the PDF")
            
            # Ultra-efficient text joining
            full_text = "\n\n".join(text_parts)
            del text_parts
            
            # Advanced text post-processing
            full_text = self._ultra_optimize_text(full_text)
            
            # Increased text length limit for better accuracy
            max_text_length = 300000  # 300KB
            if len(full_text) > max_text_length:
                # Smart truncation at sentence boundaries
                truncation_point = full_text.rfind('. ', 0, max_text_length)
                if truncation_point > max_text_length * 0.8:
                    full_text = full_text[:truncation_point + 1] + "\n\n[Document truncated at sentence boundary]"
                else:
                    full_text = full_text[:max_text_length] + "\n\n[Document truncated due to length]"
            
            return full_text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _ultra_optimize_text(self, text: str) -> str:
        """Ultra-advanced text optimization"""
        import re
        
        # Multi-step optimization
        # 1. Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add spaces between camelCase
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Add spaces between numbers and letters
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)  # Add spaces between letters and numbers
        
        # 2. Fix line breaks and paragraphs
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple line breaks to double
        text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)  # Sentence boundaries
        
        # 3. Insurance-specific optimizations
        text = self.optimizer._optimize_insurance_text(text)
        
        # 4. Remove excessive whitespace
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\t+', ' ', text)  # Tabs to spaces
        
        return text.strip()

# Initialize ultra-optimized processor
training_data_path = "/home/ubuntu/hackrx-main/training_data/raw_dataset.json"
ultra_processor = None

try:
    if os.path.exists(training_data_path):
        ultra_processor = EnhancedQueryProcessor(training_data_path)
        print("✅ Ultra processor initialized with training data")
    else:
        ultra_processor = EnhancedQueryProcessor()
        print("⚠️ Ultra processor initialized without training data")
except Exception as e:
    print(f"⚠️ Error initializing ultra processor: {str(e)}")
    ultra_processor = EnhancedQueryProcessor()

@hackrx_ultra_bp.route('/v1/hackrx/run', methods=['POST'])
@cross_origin()
@performance_optimizer.time_function
def hackrx_ultra_run():
    """Ultra-optimized HackRX API endpoint with maximum performance and accuracy"""
    memory_manager = MemoryManager()
    
    try:
        # Ultra-fast request validation
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Quick validation with detailed error messages
        if 'documents' not in data:
            return jsonify({'error': 'documents field is required'}), 400
        if 'questions' not in data:
            return jsonify({'error': 'questions field is required'}), 400
        
        documents_url = data['documents']
        questions = data['questions']
        
        # Enhanced input validation
        if not isinstance(documents_url, str) or not documents_url.strip():
            return jsonify({'error': 'documents must be a valid URL string'}), 400
        if not isinstance(questions, list) or len(questions) == 0:
            return jsonify({'error': 'questions must be a non-empty list'}), 400
        if len(questions) > 30:  # Increased limit for ultra version
            return jsonify({'error': 'Maximum 30 questions allowed'}), 400
        
        # Validate questions with better error reporting
        for i, question in enumerate(questions):
            if not isinstance(question, str) or not question.strip():
                return jsonify({'error': f'Question {i+1} must be a non-empty string'}), 400
            if len(question) > 2000:  # Increased limit
                return jsonify({'error': f'Question {i+1} too long (max 2000 characters)'}), 400
        
        # Ultra-optimized PDF processing
        try:
            print("Starting ultra-optimized PDF processing...")
            pdf_processor = UltraOptimizedPDFProcessor()
            pdf_bytes = pdf_processor.download_pdf(documents_url)
            
            memory_after_download = memory_manager.get_memory_usage()
            print(f"Memory after PDF download: {memory_after_download['rss_mb']:.2f}MB")
            
            document_text = pdf_processor.extract_text_from_pdf(pdf_bytes)
            
            del pdf_bytes
            gc.collect()
            
            print(f"Extracted text length: {len(document_text)} characters")
            
        except Exception as e:
            return jsonify({'error': f'PDF processing failed: {str(e)}'}), 400
        
        # Ultra-optimized query processing with parallel execution
        try:
            print("Starting ultra-optimized query processing...")
            
            if ultra_processor:
                # Use parallel processing for better performance
                if len(questions) > 5:
                    answers = performance_optimizer.parallel_process_queries(
                        ultra_processor, document_text, questions, max_workers=4
                    )
                else:
                    answers = ultra_processor.batch_process_queries(document_text, questions)
            else:
                answers = ["Ultra processor not available" for _ in questions]
            
            del document_text
            gc.collect()
            
            print("Ultra-optimized query processing completed")
            
        except Exception as e:
            return jsonify({'error': f'Query processing failed: {str(e)}'}), 500
        
        # Validate and optimize response
        if len(answers) != len(questions):
            return jsonify({'error': 'Mismatch between number of questions and answers'}), 500
        
        # Final optimizations
        performance_optimizer.batch_optimize_memory()
        
        # Create ultra-optimized response
        response = {
            'answers': answers
        }
        
        return jsonify(response), 200
        
    except MemoryError as e:
        memory_manager.force_garbage_collection()
        return jsonify({'error': f'Memory limit exceeded: {str(e)}'}), 507
        
    except Exception as e:
        print(f"Unexpected error in hackrx_ultra_run: {str(e)}")
        memory_manager.force_garbage_collection()
        return jsonify({'error': 'Internal server error'}), 500

@hackrx_ultra_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check_ultra():
    """Ultra-optimized health check with performance stats"""
    memory_manager = MemoryManager()
    memory_usage = memory_manager.get_memory_usage()
    perf_stats = performance_optimizer.get_performance_stats()
    
    return jsonify({
        'status': 'healthy',
        'service': 'HackRX Ultra API',
        'version': '2.0.0-ultra',
        'model': 'gemini-1.5-pro-latest',
        'memory_usage_mb': round(memory_usage['rss_mb'], 2),
        'memory_percent': round(memory_usage['percent'], 2),
        'performance_stats': perf_stats,
        'ultra_features': [
            'Ultra-fast PDF processing (16KB chunks)',
            'Parallel query processing (up to 4 workers)',
            'Advanced text optimization',
            'Smart memory management (450MB limit)',
            'Performance caching with hit rate tracking',
            'Response compression',
            'Batch processing optimization',
            'Enhanced error handling',
            'Real-time performance monitoring'
        ],
        'training_documents': len(ultra_processor.training_data) if ultra_processor else 0,
        'max_questions': 30,
        'max_question_length': 2000,
        'max_pdf_size_mb': 50
    }), 200

@hackrx_ultra_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_performance_stats():
    """Get detailed performance statistics"""
    return jsonify(performance_optimizer.get_performance_stats()), 200

