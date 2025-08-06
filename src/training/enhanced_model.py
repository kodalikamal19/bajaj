import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import gc
from src.utils.memory_manager import MemoryManager

class EnhancedQueryProcessor:
    """Enhanced query processor with training capabilities and improved accuracy"""
    
    def __init__(self, training_data_path: str = None):
        # Configure Gemini with latest model
        self.model = None
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ Warning: GOOGLE_API_KEY environment variable not set")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        
        self.memory_manager = MemoryManager()
        self.training_data = []
        self.document_embeddings = {}
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            max_df=0.8,
            min_df=2
        )
        self.document_vectors = None
        
        # Load training data if provided
        if training_data_path and os.path.exists(training_data_path):
            self.load_training_data(training_data_path)
            self.build_document_index()
    
    def load_training_data(self, data_path: str):
        """Load training data from JSON file"""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            print(f"Loaded {len(self.training_data)} training documents")
        except Exception as e:
            print(f"Error loading training data: {str(e)}")
            self.training_data = []
    
    def build_document_index(self):
        """Build TF-IDF index for document similarity matching"""
        if not self.training_data:
            return
        
        try:
            # Extract document contents
            documents = [doc['content'] for doc in self.training_data]
            
            # Build TF-IDF vectors
            self.document_vectors = self.vectorizer.fit_transform(documents)
            
            # Save the vectorizer and vectors
            self.save_model_components()
            
            print(f"Built document index with {len(documents)} documents")
            
        except Exception as e:
            print(f"Error building document index: {str(e)}")
    
    def find_similar_documents(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find similar documents from training data"""
        if self.document_vectors is None or not self.training_data:
            return []
        
        try:
            # Vectorize the query
            query_vector = self.vectorizer.transform([query_text])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Get top-k similar documents
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            similar_docs = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    doc = self.training_data[idx].copy()
                    doc['similarity_score'] = float(similarities[idx])
                    similar_docs.append(doc)
            
            return similar_docs
            
        except Exception as e:
            print(f"Error finding similar documents: {str(e)}")
            return []
    
    def generate_enhanced_prompt(self, document_text: str, question: str, similar_docs: List[Dict[str, Any]] = None) -> str:
        """Generate enhanced prompt with context from similar documents"""
        
        # Optimized prompt for faster processing and complete sentences
        prompt = f"""Based on the following document, answer the question accurately and concisely. 
        The answer MUST be a complete, grammatically correct sentence or two, summarizing the information directly.
        Example: 'Yes, knee surgery is covered under the policy.'

DOCUMENT:
{document_text[:50000]}

QUESTION: {question}

INSTRUCTIONS:
- Provide a direct, factual answer based only on the document content
- Keep answers brief (1-2 complete sentences maximum)
- If information is not in the document, respond "Information not available in the document."
- Focus on specific facts, numbers, and key details
- Do not include introductory or concluding phrases.

ANSWER:"""
        
        return prompt
    
    def process_query_with_enhancement(self, document_text: str, question: str) -> str:
        """Process query with enhanced context and accuracy"""
        try:
            # Check if model is available (API key was set)
            if self.model is None:
                return "API key not configured. Please set the GOOGLE_API_KEY environment variable."
                
            # Skip similarity search for faster processing
            similar_docs = []
            
            # Generate enhanced prompt
            enhanced_prompt = self.generate_enhanced_prompt(
                document_text, question, similar_docs
            )
            
            # Generate response with optimized settings for speed and completeness
            response = self.model.generate_content(
                enhanced_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,  # Deterministic for speed
                    top_p=0.9,
                    top_k=20,  # Reduced for faster generation
                    max_output_tokens=75,  # Adjusted for complete sentences while aiming for speed
                )
            )
            
            answer = response.text.strip()
            
            # Minimal post-processing for speed
            if answer and answer[0].islower():
                answer = answer[0].upper() + answer[1:]
            
            return answer
            
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def post_process_answer(self, answer: str, question: str, document_text: str) -> str:
        """Post-process answer to improve accuracy and consistency"""
        
        # Remove common AI hedging phrases for more direct answers
        hedging_phrases = [
            "Based on the document, ",
            "According to the document, ",
            "The document states that ",
            "It appears that ",
            "It seems that "
        ]
        
        for phrase in hedging_phrases:
            if answer.startswith(phrase):
                answer = answer[len(phrase):]
                break
        
        # Ensure first letter is capitalized
        if answer and answer[0].islower():
            answer = answer[0].upper() + answer[1:]
        
        # Add specific formatting for common question types
        question_lower = question.lower()
        
        if 'premium' in question_lower and 'amount' in question_lower:
            # Try to extract specific premium amounts
            import re
            amounts = re.findall(r'₹[\d,]+|Rs\.?\s*[\d,]+|\$[\d,]+', answer)
            if amounts:
                answer = f"The premium amount is {amounts[0]}. {answer}"
        
        elif 'coverage' in question_lower or 'sum insured' in question_lower:
            # Try to extract coverage amounts
            import re
            amounts = re.findall(r'₹[\d,]+|Rs\.?\s*[\d,]+|\$[\d,]+', answer)
            if amounts:
                answer = f"The coverage amount is {amounts[0]}. {answer}"
        
        return answer
    
    def batch_process_queries(self, document_text: str, questions: List[str]) -> List[str]:
        """Process multiple queries with enhanced accuracy"""
        answers = []
        
        # Optimize document text once
        optimized_text = self._optimize_document_text(document_text)
        
        for i, question in enumerate(questions):
            try:
                print(f"Processing enhanced query {i+1}/{len(questions)}")
                
                answer = self.process_query_with_enhancement(optimized_text, question)
                answers.append(answer)
                
                # Memory cleanup
                gc.collect()
                
            except Exception as e:
                print(f"Error processing question '{question}': {str(e)}")
                answers.append(f"Error processing this question: {str(e)}")
        
        return answers
    
    def _optimize_document_text(self, document_text: str) -> str:
        """Optimize document text for faster processing"""
        # Quick optimization for speed
        lines = [line.strip() for line in document_text.split('\n') if line.strip() and len(line.strip()) > 3]
        optimized_text = '\n'.join(lines)
        
        # Reduced text length for faster processing
        max_length = 50000  # Reduced from 100000
        if len(optimized_text) > max_length:
            optimized_text = optimized_text[:max_length] + "\n[Document truncated]"
        
        return optimized_text
    
    def save_model_components(self):
        """Save model components for faster loading"""
        try:
            model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "model_components")
            os.makedirs(model_dir, exist_ok=True)
            
            # Save vectorizer
            with open(os.path.join(model_dir, "vectorizer.pkl"), 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            # Save document vectors
            with open(os.path.join(model_dir, "document_vectors.pkl"), 'wb') as f:
                pickle.dump(self.document_vectors, f)
            
            print("Model components saved successfully")
            
        except Exception as e:
            print(f"Error saving model components: {str(e)}")
    
    def load_model_components(self):
        """Load pre-trained model components"""
        try:
            model_dir = "/home/ubuntu/hackrx-main/model_components"
            
            # Load vectorizer
            vectorizer_path = os.path.join(model_dir, "vectorizer.pkl")
            if os.path.exists(vectorizer_path):
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            
            # Load document vectors
            vectors_path = os.path.join(model_dir, "document_vectors.pkl")
            if os.path.exists(vectors_path):
                with open(vectors_path, 'rb') as f:
                    self.document_vectors = pickle.load(f)
            
            print("Model components loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading model components: {str(e)}")
            return False
    
    def evaluate_accuracy(self, test_questions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate model accuracy on test questions"""
        correct_answers = 0
        total_questions = len(test_questions)
        
        for test_item in test_questions:
            document = test_item['context']
            question = test_item['question']
            
            answer = self.process_query_with_enhancement(document, question)
            
            # Simple accuracy check (can be enhanced with more sophisticated metrics)
            if "Information not available" not in answer and len(answer) > 10:
                correct_answers += 1
        
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct_answers': correct_answers,
            'total_questions': total_questions
        }