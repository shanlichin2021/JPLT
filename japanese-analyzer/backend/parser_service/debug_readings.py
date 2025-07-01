#!/usr/bin/env python3
"""
Debug script to examine how GiNZA provides readings for tokens
"""
import spacy
import ginza

# Load the GiNZA model
nlp = spacy.load("ja_ginza")

def debug_token_readings(text):
    print(f"Debugging readings for: {text}")
    print("=" * 50)
    
    doc = nlp(text)
    
    for i, token in enumerate(doc):
        print(f"Token {i}: '{token.text}'")
        print(f"  POS: {token.pos_}")
        print(f"  Lemma: {token.lemma_}")
        print(f"  Has reading attr: {hasattr(token._, 'reading')}")
        
        # Check for reading attribute
        if hasattr(token._, 'reading'):
            print(f"  Reading: {token._.reading}")
        else:
            print(f"  Reading: None (no reading attribute)")
        
        # Check morph features
        if token.morph:
            print(f"  Morph features: {token.morph}")
            morph_dict = token.morph.to_dict()
            if 'Reading' in morph_dict:
                print(f"  Morph Reading: {morph_dict['Reading']}")
        
        # Check if contains kanji
        has_kanji = any('\u4e00' <= c <= '\u9faf' for c in token.text)
        print(f"  Contains Kanji: {has_kanji}")
        
        # Check norm attribute
        if hasattr(token, 'norm_'):
            print(f"  Norm: {token.norm_}")
        
        print()

if __name__ == "__main__":
    test_texts = [
        "日本語",
        "勉強",
        "難しい",
        "素晴らしい",
        "今日",
        "本を読む"
    ]
    
    for text in test_texts:
        debug_token_readings(text)
        print()