# HackRX Enhanced API - Ultra-Optimized Document Processing

## 🚀 Overview

The HackRX Enhanced API is a highly optimized, AI-powered document processing system that extracts information from PDF documents and answers questions with exceptional accuracy and performance. This version includes advanced training capabilities, multiple optimization levels, and comprehensive performance monitoring.

## 🎯 Key Features

### ✅ **Multiple API Endpoints**
- **Standard API** (`/api/v1/hackrx/run`) - Basic functionality
- **Enhanced API** (`/api/enhanced/v1/hackrx/run`) - With training data integration
- **Ultra API** (`/api/ultra/v1/hackrx/run`) - Maximum performance and accuracy

### ✅ **Advanced AI Model**
- **Model**: `gemini-1.5-pro-latest` (Google's most advanced model)
- **Training**: Trained on 7 insurance documents (1M+ characters)
- **Accuracy**: Enhanced with document similarity matching
- **Context**: Up to 300KB document processing capability
- **Summarized Answers**: Provides concise, 1-3 sentence answers

### ✅ **Performance Optimizations**
- **Parallel Processing**: Up to 4 concurrent query workers
- **Memory Management**: Smart 450MB limit with automatic cleanup
- **Caching**: Response caching with hit rate tracking
- **Text Processing**: Advanced PDF extraction and cleaning
- **Batch Processing**: Optimized for multiple questions

### ✅ **Training Features**
- **Dataset**: 7 Bajaj insurance documents processed
- **Document Types**: Insurance policies, health insurance, life insurance
- **Training Pairs**: 105+ question-answer combinations
- **Similarity Matching**: TF-IDF based document similarity
- **Context Enhancement**: Relevant document context injection

## 📊 Performance Metrics

### **Processing Capabilities**
- **Max Questions**: 30 per request (Ultra), 25 (Enhanced), 20 (Standard)
- **Max Question Length**: 2000 characters (Ultra), 1500 (Enhanced), 1000 (Standard)
- **Max PDF Size**: 50MB
- **Max Pages**: 600 pages (Ultra), 500 (Enhanced/Standard)
- **Text Limit**: 300KB (Ultra), 250KB (Enhanced), 200KB (Standard)

### **Performance Benchmarks**
- **Average Response Time**: ~2-5 seconds per question
- **Memory Usage**: <450MB peak
- **Parallel Efficiency**: 60-80% improvement for 5+ questions
- **Cache Hit Rate**: Varies based on usage patterns

## 🛠️ API Endpoints

### 1. Ultra-Optimized Endpoint (Recommended)
```
POST /api/ultra/v1/hackrx/run
```

**Features:**
- Maximum performance and accuracy
- Parallel query processing
- Advanced text optimization
- Performance metrics in response
- Response compression

### 2. Enhanced Endpoint
```
POST /api/enhanced/v1/hackrx/run
```

**Features:**
- Training data integration
- Document similarity matching
- Enhanced prompt engineering
- Improved text extraction

### 3. Standard Endpoint
```
POST /api/v1/hackrx/run
```

**Features:**
- Basic functionality
- Memory optimized
- Standard Gemini processing

### Health Check Endpoints
```
GET /api/health          # Standard health check
GET /api/enhanced/health # Enhanced health check
GET /api/ultra/health    # Ultra health check with performance stats
GET /api/ultra/stats     # Detailed performance statistics
```

## 📝 Request Format

```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the premium amount?",
    "What are the key benefits?",
    "What are the exclusions?",
    "How to file a claim?"
  ]
}
```

## 📋 Response Format

### Ultra API Response
```json
{
  "answers": [
    "The premium amount is ₹12,000 annually...",
    "Key benefits include coverage for...",
    "Exclusions include pre-existing conditions...",
    "To file a claim, contact customer service..."
  ],
  "performance_metrics": {
    "total_processing_time": 8.45,
    "avg_time_per_question": 2.11,
    "memory_usage_mb": 234.5,
    "questions_processed": 4,
    "text_length_processed": 125000
  },
  "model_info": {
    "model_name": "gemini-1.5-pro-latest",
    "version": "ultra-optimized-v2.0",
    "enhanced_features": [
      "Ultra-fast PDF processing",
      "Parallel query processing",
      "Advanced text optimization",
      "Smart memory management",
      "Document similarity matching",
      "Enhanced prompt engineering",
      "Response compression",
      "Performance caching"
    ],
    "training_documents": 7
  }
}
```

## 🔧 Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
PORT=5001
FLASK_ENV=production
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository>
cd hackrx-main
pip install -r requirements.txt
```

### 2. Set Environment Variable
```bash
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

### 3. Run the Application
```bash
python src/main.py
```

### 4. Test the API
```bash
curl -X POST http://localhost:5001/api/ultra/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/sample.pdf",
    "questions": ["What is this document about?"]
  }'
```

## 📈 Training and Dataset

### Dataset Information
- **Documents**: 7 Bajaj insurance PDFs
- **Total Characters**: 1,024,094
- **Document Types**: Insurance policies, health insurance, life insurance
- **Training Pairs**: 105 question-answer combinations

### Training Process
```bash
# Process the dataset
python process_dataset.py

# Train the enhanced model
python train_model.py
```

### Training Files Generated
- `training_data/raw_dataset.json` - Extracted text from PDFs
- `training_data/training_pairs.json` - Generated Q&A pairs
- `training_data/dataset_summary.json` - Processing summary
- `training_data/test_results.json` - Model performance results
- `model_components/` - Cached model components

## 🎯 Model Improvements Implemented

### ✅ **Accuracy Enhancements**
1. **Document Similarity Matching** - TF-IDF based context retrieval
2. **Enhanced Prompt Engineering** - Context-aware prompts with similar document examples
3. **Post-Processing Optimization** - Answer refinement and formatting
4. **Training Data Integration** - 7 insurance documents for domain expertise
5. **Advanced Text Extraction** - Improved PDF parsing and cleaning

### ✅ **Performance Optimizations**
1. **Parallel Query Processing** - Up to 4 concurrent workers
2. **Memory Management** - Smart limits and automatic cleanup
3. **Response Caching** - Intelligent caching with hit rate tracking
4. **Batch Processing** - Optimized multi-question handling
5. **Text Optimization** - Advanced cleaning and preprocessing

### ✅ **Runtime Improvements**
1. **Ultra-Fast PDF Processing** - 16KB chunks, batch processing
2. **Optimized Model Parameters** - Temperature=0.1 for accuracy
3. **Smart Memory Limits** - 450MB with automatic management
4. **Performance Monitoring** - Real-time metrics and statistics
5. **Response Compression** - Bandwidth optimization

## 🔍 Model Specifications

### **Gemini Model Configuration**
```python
model = genai.GenerativeModel("gemini-1.5-pro-latest")
generation_config = {
    "temperature": 0.1,      # Low for accuracy
    "top_p": 0.8,           # Focused sampling
    "top_k": 40,            # Controlled diversity
    "max_output_tokens": 200  # Reduced for summarized answers
}
```

### **TF-IDF Vectorizer Settings**
```python
vectorizer = TfidfVectorizer(
    max_features=5000,       # Feature limit
    stop_words='english',    # Remove common words
    ngram_range=(1, 3),     # 1-3 word phrases
    max_df=0.8,             # Remove too common terms
    min_df=2                # Require minimum frequency
)
```

## 📊 Performance Monitoring

### Available Metrics
- **Response Times** - Per question and total processing time
- **Memory Usage** - Peak and average memory consumption
- **Cache Performance** - Hit rates and cache efficiency
- **Throughput** - Questions processed per second
- **Error Rates** - Success/failure statistics

### Monitoring Endpoints
```bash
# Get performance statistics
GET /api/ultra/stats

# Health check with performance data
GET /api/ultra/health
```

## 🚀 Deployment

### Render Deployment
1. **Connect Repository** to Render
2. **Set Environment Variables**:
   - `GOOGLE_API_KEY`: Your Gemini API key
3. **Deploy** using provided `render.yaml` configuration

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "src/main.py"]
```

## 🔧 Configuration Options

### Memory Limits
- **Standard**: 400MB
- **Enhanced**: 400MB
- **Ultra**: 450MB

### Processing Limits
- **Questions**: 20-30 per request
- **PDF Size**: 50MB maximum
- **Pages**: 500-600 pages
- **Text**: 200KB-300KB

### Performance Tuning
- **Parallel Workers**: 3-4 (configurable)
- **Batch Size**: 20 pages
- **Cache Size**: 100 entries
- **Timeout**: 45-60 seconds

## 🎯 Use Cases

### **Insurance Document Analysis**
- Policy terms and conditions
- Premium calculations
- Coverage details
- Claim procedures
- Exclusions and limitations

### **Financial Document Processing**
- Investment policies
- Banking documents
- Loan agreements
- Insurance claims
- Regulatory filings

### **Legal Document Review**
- Contract analysis
- Compliance checking
- Risk assessment
- Due diligence
- Document summarization

## 🔒 Security Features

- **Input Validation** - Comprehensive request validation
- **Memory Protection** - Automatic memory limit enforcement
- **Error Handling** - Secure error messages
- **CORS Support** - Configurable cross-origin requests
- **Rate Limiting** - Built-in request limits

## 📞 Support

For technical support or questions:
- Check the health endpoints for system status
- Review performance statistics for optimization
- Monitor memory usage for capacity planning
- Use the training data for domain-specific improvements

## 🎉 Version History

- **v2.0-ultra** - Ultra-optimized with parallel processing and advanced caching
- **v2.0-enhanced** - Training data integration and similarity matching
- **v1.0** - Basic Gemini-powered document processing

---

**Built with ❤️ using Google Gemini 1.5 Pro Latest**

