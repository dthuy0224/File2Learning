import torch
import torch.nn as nn
from transformers import (
    DistilBertModel,
    DistilBertConfig,
    DistilBertForSequenceClassification,
    PreTrainedModel
)
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DifficultyClassifier(nn.Module):
    """
    Difficulty Classifier using DistilBERT
    
    Lightweight BERT model optimized for sequence classification
    Perfect for RTX 3050 4GB VRAM
    
    Architecture:
        Input Text → DistilBERT Encoder → [CLS] Pooling → Dropout → Linear → Softmax → Output (A1-C2)
    """
    
    # CEFR Level mapping
    LABEL_MAP = {
        0: 'A1',  # Beginner
        1: 'A2',  # Elementary  
        2: 'B1',  # Intermediate
        3: 'B2',  # Upper Intermediate
        4: 'C1',  # Advanced
        5: 'C2',  # Proficiency
    }
    
    REVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}
    
    def __init__(
        self, 
        num_labels: int = 6,
        dropout: float = 0.3,
        pretrained_model: str = 'distilbert-base-uncased'
    ):
        """
        Initialize Difficulty Classifier
        
        Args:
            num_labels: Number of difficulty levels (default: 6 for A1-C2)
            dropout: Dropout probability (default: 0.3)
            pretrained_model: HuggingFace model name
        """
        super().__init__()
        
        self.num_labels = num_labels
        
        # Load pre-trained DistilBERT
        logger.info(f"Loading DistilBERT model: {pretrained_model}")
        self.distilbert = DistilBertModel.from_pretrained(pretrained_model)
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(
            self.distilbert.config.hidden_size,  # 768 for DistilBERT
            num_labels
        )
        
        # Initialize weights
        self._init_weights(self.classifier)
        
        logger.info(f"Initialized DifficultyClassifier with {num_labels} labels")
    
    def _init_weights(self, module):
        """Initialize weights for new layers"""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=0.02)
            if module.bias is not None:
                module.bias.data.zero_()
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            input_ids: Token IDs [batch_size, seq_length]
            attention_mask: Attention mask [batch_size, seq_length]
            labels: Ground truth labels [batch_size] (optional)
            
        Returns:
            Dictionary with loss, logits, and predictions
        """
        # Get DistilBERT outputs
        outputs = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Take [CLS] token representation (first token)
        pooled_output = outputs.last_hidden_state[:, 0]  # [batch_size, hidden_size]
        
        # Apply dropout
        pooled_output = self.dropout(pooled_output)
        
        # Classify
        logits = self.classifier(pooled_output)  # [batch_size, num_labels]
        
        # Calculate loss if labels provided
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits, labels)
        
        # Get predictions
        predictions = torch.argmax(logits, dim=-1)
        probabilities = torch.softmax(logits, dim=-1)
        
        return {
            'loss': loss,
            'logits': logits,
            'predictions': predictions,
            'probabilities': probabilities
        }
    
    def predict_text(
        self, 
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> Dict[str, Any]:
        """
        Predict difficulty level for text
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            
        Returns:
            Dictionary with predicted level, confidence, and all probabilities
        """
        self.eval()
        
        with torch.no_grad():
            outputs = self.forward(input_ids, attention_mask)
        
        # Get prediction
        predicted_idx = outputs['predictions'].item()
        predicted_label = self.LABEL_MAP[predicted_idx]
        confidence = outputs['probabilities'][0][predicted_idx].item()
        
        # Get all probabilities
        all_probs = {
            self.LABEL_MAP[i]: outputs['probabilities'][0][i].item()
            for i in range(self.num_labels)
        }
        
        return {
            'level': predicted_label,
            'confidence': confidence,
            'probabilities': all_probs,
            'prediction_index': predicted_idx
        }
    
    def save_model(self, save_path: str):
        """Save model weights"""
        torch.save({
            'model_state_dict': self.state_dict(),
            'num_labels': self.num_labels,
            'label_map': self.LABEL_MAP
        }, save_path)
        logger.info(f"Model saved to {save_path}")
    
    @classmethod
    def load_model(cls, load_path: str, device: str = 'cuda'):
        """Load model weights"""
        checkpoint = torch.load(load_path, map_location=device)
        
        model = cls(num_labels=checkpoint['num_labels'])
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        
        logger.info(f"Model loaded from {load_path}")
        return model
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            'model_name': 'DifficultyClassifier',
            'base_model': 'distilbert-base-uncased',
            'num_labels': self.num_labels,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'label_map': self.LABEL_MAP
        }


class DifficultyClassifierConfig:
    """Configuration for Difficulty Classifier"""
    
    def __init__(
        self,
        num_labels: int = 6,
        dropout: float = 0.3,
        max_length: int = 512,
        learning_rate: float = 2e-5,
        warmup_steps: int = 500,
        weight_decay: float = 0.01,
        **kwargs
    ):
        self.num_labels = num_labels
        self.dropout = dropout
        self.max_length = max_length
        self.learning_rate = learning_rate
        self.warmup_steps = warmup_steps
        self.weight_decay = weight_decay
        
        # Update with any additional kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

