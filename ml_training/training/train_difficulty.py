"""
Training Script for Difficulty Classifier
Optimized for RTX 3050 4GB VRAM

Usage:
    python -m app.ai.training.train_difficulty
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizer,
    AdamW,
    get_linear_schedule_with_warmup
)
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from tqdm import tqdm
import json
import logging
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns

# Import custom modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from app.ai.models.difficulty_classifier import DifficultyClassifier
from app.ai.utils.data_preprocessing import DifficultyDataPreprocessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DifficultyDataset(Dataset):
    """PyTorch Dataset for difficulty classification"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class DifficultyTrainer:
    """Trainer for Difficulty Classifier"""
    
    def __init__(
        self,
        model: DifficultyClassifier,
        train_dataloader: DataLoader,
        val_dataloader: DataLoader,
        device: str = 'cuda',
        learning_rate: float = 2e-5,
        num_epochs: int = 3,
        warmup_steps: int = 500,
        output_dir: str = 'models/difficulty_classifier'
    ):
        self.model = model.to(device)
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.device = device
        self.num_epochs = num_epochs
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Optimizer
        self.optimizer = AdamW(
            model.parameters(),
            lr=learning_rate,
            eps=1e-8
        )
        
        # Learning rate scheduler
        total_steps = len(train_dataloader) * num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        # Track metrics
        self.train_losses = []
        self.val_losses = []
        self.val_accuracies = []
        self.val_f1_scores = []
        
        logger.info(f"Trainer initialized. Device: {device}")
        logger.info(f"Total training steps: {total_steps}")
    
    def train_epoch(self) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        progress_bar = tqdm(self.train_dataloader, desc="Training")
        
        for batch in progress_bar:
            # Move batch to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs['loss']
            total_loss += loss.item()
            
            # Backward pass
            loss.backward()
            
            # Clip gradients
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            # Update weights
            self.optimizer.step()
            self.scheduler.step()
            
            # Update progress bar
            progress_bar.set_postfix({'loss': loss.item()})
        
        avg_loss = total_loss / len(self.train_dataloader)
        return avg_loss
    
    def evaluate(self) -> Dict[str, float]:
        """Evaluate on validation set"""
        self.model.eval()
        total_loss = 0
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(self.val_dataloader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                total_loss += outputs['loss'].item()
                
                predictions = outputs['predictions'].cpu().numpy()
                all_predictions.extend(predictions)
                all_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        avg_loss = total_loss / len(self.val_dataloader)
        accuracy = accuracy_score(all_labels, all_predictions)
        f1_macro = f1_score(all_labels, all_predictions, average='macro')
        f1_weighted = f1_score(all_labels, all_predictions, average='weighted')
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted,
            'predictions': all_predictions,
            'labels': all_labels
        }
    
    def train(self):
        """Full training loop"""
        logger.info("Starting training...")
        logger.info(f"Training for {self.num_epochs} epochs")
        
        best_f1 = 0.0
        
        for epoch in range(self.num_epochs):
            logger.info(f"\n{'='*60}")
            logger.info(f"Epoch {epoch + 1}/{self.num_epochs}")
            logger.info(f"{'='*60}")
            
            # Train
            train_loss = self.train_epoch()
            self.train_losses.append(train_loss)
            logger.info(f"Average training loss: {train_loss:.4f}")
            
            # Evaluate
            val_metrics = self.evaluate()
            self.val_losses.append(val_metrics['loss'])
            self.val_accuracies.append(val_metrics['accuracy'])
            self.val_f1_scores.append(val_metrics['f1_weighted'])
            
            logger.info(f"Validation loss: {val_metrics['loss']:.4f}")
            logger.info(f"Validation accuracy: {val_metrics['accuracy']:.4f}")
            logger.info(f"Validation F1 (macro): {val_metrics['f1_macro']:.4f}")
            logger.info(f"Validation F1 (weighted): {val_metrics['f1_weighted']:.4f}")
            
            # Save best model
            if val_metrics['f1_weighted'] > best_f1:
                best_f1 = val_metrics['f1_weighted']
                self.save_model('best_model.pt')
                logger.info(f"✅ New best model saved! F1: {best_f1:.4f}")
            
            # Save checkpoint
            self.save_checkpoint(epoch, val_metrics)
        
        logger.info("\n" + "="*60)
        logger.info("Training complete!")
        logger.info(f"Best validation F1: {best_f1:.4f}")
        logger.info("="*60)
        
        # Plot training curves
        self.plot_training_curves()
    
    def save_model(self, filename: str):
        """Save model weights"""
        save_path = self.output_dir / filename
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'num_labels': self.model.num_labels,
            'label_map': self.model.LABEL_MAP
        }, save_path)
        logger.info(f"Model saved to {save_path}")
    
    def save_checkpoint(self, epoch: int, metrics: Dict[str, float]):
        """Save training checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'metrics': metrics,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'val_accuracies': self.val_accuracies,
            'val_f1_scores': self.val_f1_scores
        }
        
        checkpoint_path = self.output_dir / f'checkpoint_epoch_{epoch+1}.pt'
        torch.save(checkpoint, checkpoint_path)
    
    def plot_training_curves(self):
        """Plot training curves"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Loss curve
        axes[0].plot(self.train_losses, label='Train Loss')
        axes[0].plot(self.val_losses, label='Val Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Training and Validation Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        # Accuracy curve
        axes[1].plot(self.val_accuracies, label='Validation Accuracy', color='green')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title('Validation Accuracy')
        axes[1].legend()
        axes[1].grid(True)
        
        # F1 Score curve
        axes[2].plot(self.val_f1_scores, label='Validation F1 (weighted)', color='orange')
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('F1 Score')
        axes[2].set_title('Validation F1 Score')
        axes[2].legend()
        axes[2].grid(True)
        
        plt.tight_layout()
        
        plot_path = self.output_dir / 'training_curves.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"Training curves saved to {plot_path}")
        plt.close()


def plot_confusion_matrix(y_true, y_pred, labels, save_path):
    """Plot confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=labels,
        yticklabels=labels
    )
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Confusion matrix saved to {save_path}")


def main():
    """Main training function"""
    print("=" * 70)
    print("🚀 Training Difficulty Classifier")
    print("=" * 70)
    
    # Configuration
    config = {
        'batch_size': 8,  # Optimized for RTX 3050 4GB
        'num_epochs': 3,
        'learning_rate': 2e-5,
        'max_length': 512,
        'warmup_steps': 500,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu'
    }
    
    logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    logger.info(f"Using device: {config['device']}")
    
    if config['device'] == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    # Load data
    logger.info("\nLoading dataset...")
    preprocessor = DifficultyDataPreprocessor()
    
    dataset_path = Path('app/ai/datasets/raw_dataset.json')
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.info("Please run: python -m app.ai.datasets.collect_data")
        return
    
    df = preprocessor.load_dataset(str(dataset_path))
    
    # Split dataset
    train_df, val_df, test_df = preprocessor.split_dataset(df)
    
    # Save splits
    preprocessor.save_split_datasets(
        train_df, val_df, test_df,
        output_dir='app/ai/datasets'
    )
    
    # Create datasets
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    
    train_dataset = DifficultyDataset(
        train_df['text'].tolist(),
        [preprocessor.LABEL_MAP[label] for label in train_df['label']],
        tokenizer,
        max_length=config['max_length']
    )
    
    val_dataset = DifficultyDataset(
        val_df['text'].tolist(),
        [preprocessor.LABEL_MAP[label] for label in val_df['label']],
        tokenizer,
        max_length=config['max_length']
    )
    
    # Create dataloaders
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=0  # Windows compatibility
    )
    
    val_dataloader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'] * 2,  # Larger batch for eval
        shuffle=False,
        num_workers=0
    )
    
    logger.info(f"Train batches: {len(train_dataloader)}")
    logger.info(f"Val batches: {len(val_dataloader)}")
    
    # Initialize model
    logger.info("\nInitializing model...")
    model = DifficultyClassifier(num_labels=6, dropout=0.3)
    
    model_info = model.get_model_info()
    logger.info(f"Model parameters: {model_info['total_parameters']:,}")
    
    # Initialize trainer
    trainer = DifficultyTrainer(
        model=model,
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader,
        device=config['device'],
        learning_rate=config['learning_rate'],
        num_epochs=config['num_epochs'],
        warmup_steps=config['warmup_steps']
    )
    
    # Train
    trainer.train()
    
    # Final evaluation
    logger.info("\n" + "="*70)
    logger.info("Final Evaluation on Validation Set")
    logger.info("="*70)
    
    val_metrics = trainer.evaluate()
    
    # Classification report
    labels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    report = classification_report(
        val_metrics['labels'],
        val_metrics['predictions'],
        target_names=labels,
        digits=4
    )
    
    print("\nClassification Report:")
    print(report)
    
    # Plot confusion matrix
    plot_confusion_matrix(
        val_metrics['labels'],
        val_metrics['predictions'],
        labels,
        save_path=trainer.output_dir / 'confusion_matrix.png'
    )
    
    print("\n" + "="*70)
    print("✅ Training Complete!")
    print("="*70)
    print(f"\nModel saved to: {trainer.output_dir}")
    print("\nNext steps:")
    print("1. Review training curves and confusion matrix")
    print("2. Test on test set: python -m app.ai.training.evaluate_model")
    print("3. Deploy model: integrate into document processing pipeline")


if __name__ == '__main__':
    main()

