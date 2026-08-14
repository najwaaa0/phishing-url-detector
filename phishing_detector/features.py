def extract_features(url):
    features = {}
    
    # Example feature extraction
    features['length'] = len(url)
    features['num_digits'] = sum(c.isdigit() for c in url)
    features['num_special_chars'] = sum(not c.isalnum() for c in url)
    
    # Check for the presence of suspicious words
    suspicious_words = ['login', 'secure', 'account', 'update', 'verify']
    features['suspicious_word_count'] = sum(word in url for word in suspicious_words)
    
    # Add more feature extraction logic as needed
    
    return features