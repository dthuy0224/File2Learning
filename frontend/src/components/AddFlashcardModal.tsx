import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import FlashcardService from '../services/flashcardService';
import toast from 'react-hot-toast';

interface AddFlashcardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AddFlashcardModal({ isOpen, onClose }: AddFlashcardModalProps) {
  const [frontText, setFrontText] = useState('');
  const [backText, setBackText] = useState('');
  const [example, setExample] = useState('');
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: FlashcardService.createFlashcard,
    onSuccess: () => {
      toast.success('Flashcard created successfully!');
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      onClose();
      // Reset form
      setFrontText('');
      setBackText('');
      setExample('');
    },
    onError: () => {
      toast.error('Failed to create flashcard.');
    }
  });

  const handleSubmit = () => {
    if (!frontText || !backText) {
      toast.error('Front and back text cannot be empty.');
      return;
    }
    createMutation.mutate({
      front_text: frontText,
      back_text: backText,
      example_sentence: example
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg w-full max-w-md mx-4">
        <h2 className="text-2xl font-bold mb-4">Create New Flashcard</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Front (Word/Phrase)
            </label>
            <Input
              value={frontText}
              onChange={(e) => setFrontText(e.target.value)}
              placeholder="e.g., Resilient"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Back (Definition)
            </label>
            <Textarea
              value={backText}
              onChange={(e) => setBackText(e.target.value)}
              placeholder="e.g., Able to withstand or recover quickly..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Example Sentence (Optional)
            </label>
            <Textarea
              value={example}
              onChange={(e) => setExample(e.target.value)}
              placeholder="e.g., The company proved to be resilient during the recession."
            />
          </div>
        </div>
        <div className="mt-6 flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? 'Saving...' : 'Save Flashcard'}
          </Button>
        </div>
      </div>
    </div>
  );
}
