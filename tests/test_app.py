from app import app, predict_url, rule_based_is_phishing


def test_home_page():
    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"Check a URL" in response.data


def test_check_url_get_returns_verdict_page():
    with app.test_client() as client:
        response = client.get("/check_url", query_string={"url": "https://example.com"})

    assert response.status_code == 200
    assert b"URL Analysis" in response.data
    assert b"https://example.com" in response.data


def test_empty_url_shows_index_page():
    with app.test_client() as client:
        response = client.post("/check_url", data={"url": ""})

    assert response.status_code == 200
    assert b"Check a URL" in response.data


def test_rule_based_detector_flags_high_risk_url():
    assert rule_based_is_phishing("http://192.168.0.1/login") is True


def test_predict_url_returns_known_label():
    result = predict_url("https://example.com")

    assert result in {"Safe", "Phishing/Not Safe"}
