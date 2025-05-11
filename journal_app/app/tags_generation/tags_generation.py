"""
This module provides functionality for generating relevant tags for text input
using a pre-trained zero-shot classification model from the Hugging Face
transformers library ('MoritzLaurer/deberta-v3-base-zeroshot-v2.0').

Loading errors during import are caught and suppressed, resulting in the
tags generator function returning an empty list if the classifier is not available.

The primary function, `tags_generator`, takes a text string and classifies it
against a list of candidate tags, returning the top 3 most relevant tags.
It includes basic validation for the input text and handles potential
classification errors by returning an empty list.

Dependencies:
    - transformers: Requires the Hugging Face transformers library.
      Install with: pip install transformers
    - An underlying deep learning framework (PyTorch or TensorFlow), required by transformers.
"""

classifier = None

try:
    from transformers import pipeline
    classifier = pipeline("zero-shot-classification",
                          model="MoritzLaurer/deberta-v3-base-zeroshot-v2.0")
except Exception:
    pass

def tags_generator(text):
    """
    Generates relevant tags for a given text using zero-shot classification.

    Args:
        text: The input string to classify.

    Returns:
        A list of the top 3 predicted tags, or an empty list if classification
        fails or input is invalid.
    """
    if classifier is None:
        return ['NO', 'CLASSIFIER']
    if not isinstance(text, str):
        return ['NO', 'INSTANCE']
    if not text.strip():
        return ['NOT', 'TEXT']
    
    candidate_tags = ["Daily Reflection", "Gratitude", "Mood", "Feelings", "Thoughts",
                      "Emotions", "Day in Review", "Morning", "Evening", "Night",
                      "Goals", "Progress", "Challenges", "Successes", "Learning",
                      "Ideas", "Inspiration", "Dreams", "Work", "Career",
                      "Project", "Relationships", "Family", "Friends", "Love",
                      "Health", "Well-being", "Mindfulness", "Self-Care", "Personal Growth",
                      "Travel", "Adventure", "Hobbies", "Creativity", "Writing",
                      "Art", "Music", "Reading", "Memories", "Future",
                      "Planning", "Weekend", "Holiday", "Stress", "Anxiety",
                      "Happiness", "Joy", "Sadness", "Hope", "Reflection"]
    try:
        prediction = classifier(text, candidate_tags, hypothesis_template="{}", multi_label=True)            
    except Exception:
        return
    top_3_tags = prediction['labels'][:3]
    return top_3_tags