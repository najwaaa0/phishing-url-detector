def preprocess_url(url):
    # Function to preprocess the URL for feature extraction
    # This can include normalization, removing unwanted characters, etc.
    return url.strip().lower()

def log_prediction(url, prediction):
    # Function to log the URL and its prediction result
    with open("predictions.log", "a") as log_file:
        log_file.write(f"{url} - {prediction}\n")

def validate_url(url):
    # Function to validate the URL format
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None