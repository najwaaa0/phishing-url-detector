from flask import Flask, render_template, request
import joblib
import re

from phishing_detector.features import extract_features

app = Flask(__name__)

# Try loading pre-trained machine learning model; fall back to None on error
model = None
try:
    model = joblib.load('models/phishing_model.pkl')
except Exception as e:
    print(f"Warning: failed to load ML model: {e}\nFalling back to rule-based detection.")


def rule_based_is_phishing(url: str) -> bool:
    # Simple heuristic rules
    score = 0
    url_lower = url.lower()

    # IP address in domain
    if re.search(r'://\d{1,3}(?:\.\d{1,3}){3}', url):
        score += 3

    # Suspicious keywords
    suspicious = ['login', 'secure', 'update', 'verify', 'account', 'confirm', 'signin', 'bank', 'wp-admin']
    if any(word in url_lower for word in suspicious):
        score += 2

    # '@' in URL
    if '@' in url:
        score += 3

    # many '-' or long URL
    if url.count('-') > 3 or len(url) > 75:
        score += 1

    # too many subdomains
    host = re.sub(r'^https?://', '', url_lower).split('/')[0]
    if host.count('.') >= 4:
        score += 1

    return score >= 3  # threshold


def predict_url(url: str) -> str:
    if model is not None:
        try:
            features = extract_features(url)
            pred = model.predict([features])
            return 'Safe' if pred[0] == 0 else 'Phishing/Not Safe'
        except Exception as e:
            print(f"Model prediction failed, using rule-based fallback: {e}")
            return 'Phishing/Not Safe' if rule_based_is_phishing(url) else 'Safe'
    else:
        # No model, use rule-based detection
        return 'Phishing/Not Safe' if rule_based_is_phishing(url) else 'Safe'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_url', methods=['GET', 'POST'])
def check_url():
    # accept POST form or GET query param for easier testing
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
    else:
        url = request.args.get('url', '').strip()

    if not url:
        # show the index page with a small message if no URL was provided
        return render_template('index.html', error='Please enter a URL to check.')

    result = predict_url(url)
    return render_template('result.html', url=url, result=result)


if __name__ == '__main__':
    # helpful debug: show registered routes
    print(app.url_map)
    app.run(debug=True)