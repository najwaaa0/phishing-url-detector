from phishing_detector.features import extract_features


def test_extract_features_returns_implemented_keys():
    features = extract_features("https://www.example.com/login")

    assert set(features) == {
        "length",
        "num_digits",
        "num_special_chars",
        "suspicious_word_count",
    }


def test_extract_features_counts_url_characteristics():
    features = extract_features("https://www.example.com/login")

    assert features["length"] == 29
    assert features["num_digits"] == 0
    assert features["num_special_chars"] == 6
    assert features["suspicious_word_count"] == 1


def test_extract_features_counts_digits_in_ip_url():
    features = extract_features("http://192.168.0.1/admin")

    assert features["num_digits"] == 8
    assert features["num_special_chars"] == 7
