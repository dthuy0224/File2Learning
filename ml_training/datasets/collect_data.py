"""
Data Collection Script for Difficulty Classification

Downloads and prepares datasets from various sources:
1. OneStopEnglish Corpus (GitHub)
2. Sample generated data
3. User-uploaded documents (future)

Usage:
    python -m app.ai.datasets.collect_data
"""

import requests
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    """Collect training data from various sources"""
    
    def __init__(self, output_dir: str = "app/ai/datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
    
    def download_onestop_corpus(self) -> List[Dict[str, Any]]:
        """
        Download OneStopEnglish corpus from GitHub
        
        This dataset contains news articles rewritten at 3 levels:
        - Elementary (A2-B1)
        - Intermediate (B1-B2)
        - Advanced (B2-C1)
        
        Returns:
            List of text samples with labels
        """
        logger.info("Downloading OneStopEnglish corpus...")
        
        # GitHub repo URLs
        base_url = "https://raw.githubusercontent.com/nishkalavallabhi/OneStopEnglishCorpus/master/Texts-SeparatedByReadingLevel"
        
        levels = {
            'Ele-Txt': 'A2',  # Elementary → A2
            'Int-Txt': 'B1',  # Intermediate → B1
            'Adv-Txt': 'C1',  # Advanced → C1
        }
        
        samples = []
        
        try:
            for folder, label in levels.items():
                # Note: This is a simplified example
                # In practice, you need to download actual files from the repo
                logger.info(f"Processing {folder} (Level: {label})")
                
                # For now, create placeholder
                # TODO: Replace with actual download logic
                samples.append({
                    'id': f'onestop_{folder}_placeholder',
                    'text': f'This is a placeholder for {folder} level text. Please download manually from GitHub.',
                    'label': label,
                    'metadata': {
                        'source': 'onestop',
                        'folder': folder
                    }
                })
        
        except Exception as e:
            logger.error(f"Error downloading OneStopEnglish: {e}")
            logger.warning("Using placeholder data. Please download manually from:")
            logger.warning("https://github.com/nishkalavallabhi/OneStopEnglishCorpus")
        
        return samples
    
    def create_synthetic_dataset(
        self, 
        num_samples_per_level: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Create synthetic training data
        Uses templates and variations to generate diverse examples
        
        Args:
            num_samples_per_level: Number of samples to generate per level
            
        Returns:
            List of generated samples
        """
        logger.info(f"Generating synthetic dataset ({num_samples_per_level} per level)...")
        
        samples = []
        
        # Vocabulary for each level
        level_vocabulary = {
            'A1': {
                'nouns': ['cat', 'dog', 'book', 'car', 'house', 'tree', 'water', 'food'],
                'verbs': ['go', 'see', 'have', 'like', 'want', 'eat', 'drink', 'play'],
                'adjectives': ['big', 'small', 'good', 'bad', 'happy', 'sad', 'red', 'blue'],
            },
            'A2': {
                'nouns': ['friend', 'family', 'school', 'work', 'hobby', 'vacation', 'restaurant'],
                'verbs': ['travel', 'enjoy', 'prefer', 'visit', 'plan', 'decide', 'remember'],
                'adjectives': ['interesting', 'boring', 'exciting', 'difficult', 'easy', 'beautiful'],
            },
            'B1': {
                'topics': ['environment', 'technology', 'education', 'health', 'culture', 'society'],
                'concepts': ['improvement', 'development', 'challenge', 'opportunity', 'benefit'],
            },
            'B2': {
                'topics': ['globalization', 'innovation', 'sustainability', 'diversity', 'integration'],
                'concepts': ['implementation', 'transformation', 'comprehensive', 'significant'],
            },
            'C1': {
                'topics': ['paradigm shift', 'contemporary discourse', 'theoretical framework'],
                'concepts': ['necessitate', 'elucidate', 'proliferation', 'unprecedented'],
            },
            'C2': {
                'topics': ['epistemological implications', 'hermeneutic approaches', 'dialectical relationship'],
                'concepts': ['fundamentally challenge', 'nuanced understanding', 'contentious area'],
            },
        }
        
        # Templates for each level
        templates = {
            'A1': [
                "I have a {noun}. It is {adj}. I {verb} it every day.",
                "My {noun} is {adj}. I like to {verb} with it.",
                "This is a {noun}. It is very {adj}."
            ],
            'A2': [
                "Last week, I went to the {noun}. It was very {adj}. I decided to {verb} there.",
                "My {noun} and I like to {verb}. We usually {verb} on weekends because it is {adj}.",
                "I'm planning to {verb} next month. It will be very {adj} and {adj}."
            ],
            'B1': [
                "The recent developments in {topic} have shown {concept}. Many experts believe this trend will continue.",
                "Understanding {topic} requires careful consideration of various factors including {concept}.",
                "The {concept} of {topic} has become increasingly important in modern society."
            ],
            'B2': [
                "The {concept} of new approaches to {topic} has fundamentally transformed contemporary understanding.",
                "Recent research demonstrates that {topic} significantly contributes to {concept} in various contexts.",
                "The {concept} nature of {topic} continues to generate substantial debate among experts."
            ],
            'C1': [
                "The {concept} in contemporary {topic} necessitates a comprehensive reevaluation of existing frameworks.",
                "Scholarly discourse has {concept} the intricate mechanisms underlying {topic}, challenging traditional assumptions.",
                "The {concept} of {topic} has engendered unprecedented transformations in theoretical perspectives."
            ],
            'C2': [
                "The {concept} of {topic} fundamentally challenge deterministic paradigms that have historically underpinned classical understanding.",
                "Contemporary {topic} necessitate a nuanced understanding of the {concept} within broader theoretical contexts.",
                "The {concept} between {topic} remains a contentious area of rigorous theoretical inquiry and empirical investigation."
            ],
        }
        
        # Generate samples
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            for i in range(num_samples_per_level):
                template = templates[level][i % len(templates[level])]
                
                # Fill template with appropriate vocabulary
                if level in ['A1', 'A2']:
                    text = template.format(
                        noun=level_vocabulary[level]['nouns'][i % len(level_vocabulary[level]['nouns'])],
                        verb=level_vocabulary[level]['verbs'][i % len(level_vocabulary[level]['verbs'])],
                        adj=level_vocabulary[level]['adjectives'][i % len(level_vocabulary[level]['adjectives'])]
                    )
                else:
                    text = template.format(
                        topic=level_vocabulary[level]['topics'][i % len(level_vocabulary[level]['topics'])],
                        concept=level_vocabulary[level]['concepts'][i % len(level_vocabulary[level]['concepts'])]
                    )
                
                samples.append({
                    'id': f'{level}_synth_{i:04d}',
                    'text': text,
                    'label': level,
                    'metadata': {
                        'source': 'synthetic',
                        'template_id': i % len(templates[level])
                    }
                })
        
        logger.info(f"Generated {len(samples)} synthetic samples")
        return samples
    
    def collect_all_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from all sources
        
        Returns:
            Combined dataset
        """
        all_samples = []
        
        # 1. Synthetic data (always available)
        logger.info("=" * 50)
        synthetic_data = self.create_synthetic_dataset(num_samples_per_level=200)
        all_samples.extend(synthetic_data)
        
        # 2. OneStopEnglish (if available)
        logger.info("=" * 50)
        try:
            onestop_data = self.download_onestop_corpus()
            all_samples.extend(onestop_data)
        except Exception as e:
            logger.warning(f"Could not download OneStopEnglish: {e}")
        
        logger.info("=" * 50)
        logger.info(f"Total samples collected: {len(all_samples)}")
        
        # Show distribution
        df = pd.DataFrame(all_samples)
        logger.info("\nLabel distribution:")
        print(df['label'].value_counts().sort_index())
        
        return all_samples
    
    def save_dataset(self, samples: List[Dict[str, Any]], filename: str = "raw_dataset.json"):
        """
        Save collected dataset to file
        
        Args:
            samples: List of samples
            filename: Output filename
        """
        output_file = self.output_dir / filename
        
        data = {
            'data': samples,
            'num_samples': len(samples),
            'label_distribution': pd.DataFrame(samples)['label'].value_counts().to_dict(),
            'metadata': {
                'version': '1.0',
                'created_by': 'DataCollector',
                'description': 'Training dataset for difficulty classification'
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset saved to: {output_file}")
        logger.info(f"Total samples: {len(samples)}")


def main():
    """Main function to collect and save data"""
    print("=" * 70)
    print("File2Learning - Data Collection for Difficulty Classification")
    print("=" * 70)
    
    collector = DataCollector()
    
    # Collect all data
    samples = collector.collect_all_data()
    
    # Save raw dataset
    collector.save_dataset(samples, filename="raw_dataset.json")
    
    print("\n" + "=" * 70)
    print("SUCCESS: Data collection complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the dataset: app/ai/datasets/raw_dataset.json")
    print("2. Run preprocessing: python -m app.ai.utils.data_preprocessing")
    print("3. Start training: python -m app.ai.training.train_difficulty")
    print("\nNote: For better results, please download OneStopEnglish corpus manually:")
    print("https://github.com/nishkalavallabhi/OneStopEnglishCorpus")


if __name__ == '__main__':
    main()

