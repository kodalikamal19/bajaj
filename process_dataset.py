#!/usr/bin/env python3
"""
Script to process the Bajaj dataset and create training data
"""
import sys
import os
sys.path.append('/home/ubuntu/hackrx-main')

from src.training.dataset_processor import DatasetProcessor
import json

def main():
    print("🚀 Starting Bajaj Dataset Processing")
    print("=" * 50)
    
    # Dataset path
    dataset_path = "/home/ubuntu/bajaj_dataset/bajaj"
    output_dir = "/home/ubuntu/hackrx-main/training_data"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize processor
    processor = DatasetProcessor(dataset_path)
    
    # Process all PDFs
    print("📄 Processing PDF documents...")
    dataset = processor.process_all_pdfs()
    
    if not dataset:
        print("❌ No documents processed successfully")
        return
    
    print(f"✅ Successfully processed {len(dataset)} documents")
    
    # Save raw dataset
    raw_dataset_path = os.path.join(output_dir, "raw_dataset.json")
    processor.save_dataset(dataset, raw_dataset_path)
    
    # Generate training questions
    print("🤔 Generating training questions...")
    training_pairs = processor.generate_training_questions(dataset)
    
    print(f"✅ Generated {len(training_pairs)} training question-answer pairs")
    
    # Save training pairs
    training_pairs_path = os.path.join(output_dir, "training_pairs.json")
    processor.save_dataset(training_pairs, training_pairs_path)
    
    # Create summary
    summary = {
        "total_documents": len(dataset),
        "total_training_pairs": len(training_pairs),
        "document_types": {},
        "total_characters": sum(doc['length'] for doc in dataset),
        "files_processed": [doc['filename'] for doc in dataset]
    }
    
    # Count document types
    for doc in dataset:
        doc_type = doc['document_type']
        summary['document_types'][doc_type] = summary['document_types'].get(doc_type, 0) + 1
    
    # Save summary
    summary_path = os.path.join(output_dir, "dataset_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n📊 Dataset Summary:")
    print(f"  - Total Documents: {summary['total_documents']}")
    print(f"  - Total Training Pairs: {summary['total_training_pairs']}")
    print(f"  - Total Characters: {summary['total_characters']:,}")
    print(f"  - Document Types: {summary['document_types']}")
    
    print(f"\n💾 Files saved to: {output_dir}")
    print("  - raw_dataset.json: Raw extracted text from PDFs")
    print("  - training_pairs.json: Generated question-answer pairs")
    print("  - dataset_summary.json: Processing summary")
    
    print("\n🎉 Dataset processing completed successfully!")

if __name__ == "__main__":
    main()

