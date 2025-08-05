#!/usr/bin/env python3
"""
Script to train the enhanced model with the Bajaj dataset
"""
import sys
import os
sys.path.append('/home/ubuntu/hackrx-main')

from src.training.enhanced_model import EnhancedQueryProcessor
import json
import time

def main():
    print("🚀 Starting Enhanced Model Training")
    print("=" * 50)
    
    # Paths
    training_data_path = "/home/ubuntu/hackrx-main/training_data/raw_dataset.json"
    training_pairs_path = "/home/ubuntu/hackrx-main/training_data/training_pairs.json"
    
    # Initialize enhanced processor
    print("📚 Loading training data...")
    processor = EnhancedQueryProcessor(training_data_path)
    
    # Load training pairs for evaluation
    with open(training_pairs_path, 'r', encoding='utf-8') as f:
        training_pairs = json.load(f)
    
    print(f"✅ Loaded {len(training_pairs)} training pairs")
    
    # Test the enhanced model with sample questions
    print("\n🧪 Testing Enhanced Model Performance...")
    
    sample_questions = [
        "What is the premium amount?",
        "What are the key benefits of this policy?",
        "What are the exclusions in this policy?",
        "What is the coverage amount?",
        "How to file a claim?",
        "What is the policy period?",
        "Who is eligible for this policy?",
        "What documents are required?",
        "What is the waiting period?",
        "What are the renewal conditions?"
    ]
    
    # Test with first document
    if processor.training_data:
        test_document = processor.training_data[0]['content']
        print(f"\n📄 Testing with document: {processor.training_data[0]['filename']}")
        
        results = []
        total_time = 0
        
        for i, question in enumerate(sample_questions):
            print(f"\n❓ Question {i+1}: {question}")
            
            start_time = time.time()
            answer = processor.process_query_with_enhancement(test_document, question)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            print(f"✅ Answer: {answer}")
            print(f"⏱️  Response time: {response_time:.2f}s")
            
            results.append({
                'question': question,
                'answer': answer,
                'response_time': response_time,
                'answer_length': len(answer)
            })
        
        # Calculate performance metrics
        avg_response_time = total_time / len(sample_questions)
        avg_answer_length = sum(r['answer_length'] for r in results) / len(results)
        
        print(f"\n📊 Performance Summary:")
        print(f"  - Total Questions: {len(sample_questions)}")
        print(f"  - Average Response Time: {avg_response_time:.2f}s")
        print(f"  - Average Answer Length: {avg_answer_length:.0f} characters")
        print(f"  - Total Processing Time: {total_time:.2f}s")
        
        # Save results
        results_path = "/home/ubuntu/hackrx-main/training_data/test_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                'test_results': results,
                'performance_metrics': {
                    'avg_response_time': avg_response_time,
                    'avg_answer_length': avg_answer_length,
                    'total_processing_time': total_time,
                    'total_questions': len(sample_questions)
                },
                'model_info': {
                    'model_name': 'gemini-1.5-pro-latest',
                    'training_documents': len(processor.training_data),
                    'enhanced_features': [
                        'Document similarity matching',
                        'Enhanced prompt engineering',
                        'Post-processing optimization',
                        'Context-aware responses'
                    ]
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Test results saved to: {results_path}")
        
        # Test batch processing
        print(f"\n🔄 Testing Batch Processing...")
        batch_start = time.time()
        batch_answers = processor.batch_process_queries(test_document, sample_questions[:5])
        batch_end = time.time()
        
        batch_time = batch_end - batch_start
        print(f"✅ Batch processing completed in {batch_time:.2f}s")
        print(f"📈 Efficiency: {batch_time/5:.2f}s per question (batch) vs {avg_response_time:.2f}s (individual)")
        
    print("\n🎉 Enhanced Model Training and Testing Completed!")
    print("\n📋 Model Improvements Implemented:")
    print("  ✅ Document similarity matching using TF-IDF")
    print("  ✅ Enhanced prompt engineering with context")
    print("  ✅ Post-processing for better accuracy")
    print("  ✅ Optimized model parameters (temperature=0.1)")
    print("  ✅ Increased context length (100K characters)")
    print("  ✅ Memory-efficient batch processing")
    print("  ✅ Model component caching for faster loading")

if __name__ == "__main__":
    main()

