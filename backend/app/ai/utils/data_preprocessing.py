"""
Data Preprocessing Utilities for Difficulty Classification
Handles data loading, cleaning, and feature extraction
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from transformers import DistilBertTokenizer
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


class DifficultyDataPreprocessor:
    """
    Preprocessor for difficulty classification dataset
    """
    
    # CEFR level mapping
    LABEL_MAP = {
        'A1': 0, 'A2': 1, 'B1': 2,
        'B2': 3, 'C1': 4, 'C2': 5
    }
    
    REVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}
    
    def __init__(
        self,
        tokenizer_name: str = 'distilbert-base-uncased',
        max_length: int = 512
    ):
        """
        Initialize preprocessor
        
        Args:
            tokenizer_name: HuggingFace tokenizer name
            max_length: Maximum sequence length
        """
        self.tokenizer = DistilBertTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length
        logger.info(f"Initialized preprocessor with tokenizer: {tokenizer_name}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might confuse model
        # But keep punctuation for context
        text = text.strip()
        
        return text
    
    def tokenize_text(
        self,
        text: str,
        padding: str = 'max_length',
        truncation: bool = True
    ) -> Dict[str, Any]:
        """
        Tokenize text for BERT
        
        Args:
            text: Input text
            padding: Padding strategy
            truncation: Whether to truncate
            
        Returns:
            Tokenized features
        """
        return self.tokenizer(
            text,
            padding=padding,
            truncation=truncation,
            max_length=self.max_length,
            return_tensors='pt'
        )
    
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load dataset from JSON file
        
        Args:
            file_path: Path to dataset file
            
        Returns:
            DataFrame with text and label columns
        """
        logger.info(f"Loading dataset from {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        if isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            raise ValueError("Unsupported data format")
        
        logger.info(f"Loaded {len(df)} samples")
        return df
    
    def prepare_dataset(
        self,
        texts: List[str],
        labels: List[str]
    ) -> Dict[str, List]:
        """
        Prepare dataset for training
        
        Args:
            texts: List of texts
            labels: List of CEFR labels (A1-C2)
            
        Returns:
            Dictionary with tokenized inputs and labels
        """
        # Clean texts
        cleaned_texts = [self.clean_text(text) for text in texts]
        
        # Tokenize
        encodings = self.tokenizer(
            cleaned_texts,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Convert labels to integers
        label_ids = [self.LABEL_MAP[label] for label in labels]
        
        return {
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': label_ids
        }
    
    def split_dataset(
        self,
        df: pd.DataFrame,
        test_size: float = 0.15,
        val_size: float = 0.15,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into train/val/test
        
        Args:
            df: Full dataset
            test_size: Test set proportion
            val_size: Validation set proportion
            random_state: Random seed
            
        Returns:
            train_df, val_df, test_df
        """
        # First split: train+val vs test
        train_val, test = train_test_split(
            df,
            test_size=test_size,
            stratify=df['label'],
            random_state=random_state
        )
        
        # Second split: train vs val
        val_proportion = val_size / (1 - test_size)
        train, val = train_test_split(
            train_val,
            test_size=val_proportion,
            stratify=train_val['label'],
            random_state=random_state
        )
        
        logger.info(f"Split dataset: Train={len(train)}, Val={len(val)}, Test={len(test)}")
        
        return train, val, test
    
    def save_split_datasets(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        output_dir: str
    ):
        """
        Save train/val/test datasets to JSON files
        
        Args:
            train_df: Training data
            val_df: Validation data
            test_df: Test data
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save each split
        for name, df in [('train', train_df), ('val', val_df), ('test', test_df)]:
            file_path = output_path / f'difficulty_{name}.json'
            
            data = {
                'data': df.to_dict('records'),
                'num_samples': len(df),
                'label_distribution': df['label'].value_counts().to_dict()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {name} dataset to {file_path}")
    
    def get_dataset_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get dataset statistics
        
        Args:
            df: Dataset DataFrame
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_samples': len(df),
            'label_distribution': df['label'].value_counts().to_dict(),
            'avg_text_length': df['text'].apply(len).mean(),
            'avg_word_count': df['text'].apply(lambda x: len(x.split())).mean(),
        }
        
        # Add label percentages
        total = len(df)
        stats['label_percentages'] = {
            label: count / total * 100
            for label, count in stats['label_distribution'].items()
        }
        
        return stats


def create_sample_dataset(num_samples_per_level: int = 100) -> List[Dict[str, str]]:
    """
    Create a small sample dataset for testing
    This is just for demonstration - real data should come from actual sources
    
    Args:
        num_samples_per_level: Number of samples per CEFR level
        
    Returns:
        List of sample data
    """
    samples = []
    
    # Sample texts for each level (simplified examples)
    sample_templates = {
        'A1': [
            "I have a cat. My cat is {color}. She is very {adjective}.",
            "Today is {day}. The weather is {weather}. I am {feeling}.",
            "This is my {item}. It is {color} and {adjective}."
        ],
        'A2': [
            "Last week, I went to the {place}. The weather was {weather}, so I decided to {activity}.",
            "My friend likes to {activity}. We often {activity} together on weekends.",
            "I am planning to {activity} next {time}. It will be very {adjective}."
        ],
        'B1': [
            "The recent changes in {topic} have affected many people's daily lives. While some welcome the improvements, others remain skeptical.",
            "Learning a new language requires dedication and consistent practice. It's important to immerse yourself in the culture.",
            "Environmental sustainability has become a crucial concern in modern society. Many organizations are implementing green initiatives."
        ],
        'B2': [
            "The implementation of new technologies has fundamentally transformed the way businesses operate in the contemporary marketplace.",
            "Research suggests that regular physical exercise contributes significantly to both mental and physical well-being.",
            "The economic implications of globalization continue to generate considerable debate among policymakers and academics."
        ],
        'C1': [
            "The paradigmatic shift in contemporary discourse surrounding environmental policy necessitates a comprehensive reevaluation of existing frameworks.",
            "Neuroscientific research has elucidated the intricate mechanisms underlying cognitive processes, challenging traditional assumptions.",
            "The proliferation of digital technologies has engendered unprecedented transformations in interpersonal communication dynamics."
        ],
        'C2': [
            "The epistemological implications of quantum mechanics fundamentally challenge deterministic paradigms that have historically underpinned classical physics.",
            "Contemporary hermeneutic approaches to literary criticism necessitate a nuanced understanding of intertextuality and authorial intentionality.",
            "The dialectical relationship between socioeconomic structures and ideological superstructures remains a contentious area of theoretical inquiry."
        ]
    }
    
    # Generate samples
    for level, templates in sample_templates.items():
        for i in range(num_samples_per_level):
            template = templates[i % len(templates)]
            
            # Simple template filling (would be more sophisticated in real data)
            text = template.format(
                color="blue",
                adjective="beautiful",
                day="Monday",
                weather="sunny",
                feeling="happy",
                item="book",
                place="park",
                activity="reading",
                time="month",
                topic="technology"
            )
            
            samples.append({
                'id': f'{level}_{i:04d}',
                'text': text,
                'label': level,
                'metadata': {
                    'source': 'generated',
                    'template_id': templates.index(template)
                }
            })
    
    logger.info(f"Generated {len(samples)} sample texts")
    return samples


if __name__ == '__main__':
    # Test preprocessing
    logging.basicConfig(level=logging.INFO)
    
    # Create sample dataset
    samples = create_sample_dataset(num_samples_per_level=20)
    
    # Save to file
    output_file = Path('app/ai/datasets/sample_dataset.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'data': samples}, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(samples)} samples to {output_file}")
    
    # Test preprocessor
    preprocessor = DifficultyDataPreprocessor()
    df = pd.DataFrame(samples)
    
    stats = preprocessor.get_dataset_statistics(df)
    print("\nDataset Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

