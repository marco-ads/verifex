import os
import json
import pytest
from unittest.mock import patch, MagicMock
from analyzer import (
    get_domain,
    scrape_url,
    parse_response,
    call_groq,
    analyze_url,
    CREDIBLE_DOMAINS,
)

# ── get_domain ──

def test_get_domain_normal():
    assert get_domain("https://milenio.com/politica/nota") == "milenio.com"

def test_get_domain_strips_www():
    assert get_domain("https://www.eluniversal.com.mx/nota") == "eluniversal.com.mx"

def test_get_domain_invalid_url():
    assert get_domain("") == ""

def test_get_domain_with_subdomain():
    assert get_domain("https://noticieros.televisa.com/news") == "noticieros.televisa.com"

# ── scrape_url ──

def _make_mock_resp(html: str):
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.status_code = 200
    return mock_resp


@patch("analyzer._http_get")
def test_scrape_url_success(mock_get):
    html = """<html><head><title>Test Article</title>
    <meta name="description" content="A test article">
    </head><body><article><p>This is a paragraph with enough text to be included in the extraction process because it exceeds the minimum length requirement of forty characters.</p>
    <p>Another paragraph that also exceeds the minimum character threshold so it gets picked up by the scraper for processing and analysis.</p>
    </article></body></html>"""

    mock_resp = _make_mock_resp(html)
    mock_get.return_value = (mock_resp, None)

    result = scrape_url("https://example.com/news")
    assert "error" not in result
    assert result["title"] == "Test Article"
    assert "paragraph" in result["content"]
    assert "Test Article" in result["content"]


@patch("analyzer._http_get")
def test_scrape_url_timeout(mock_get):
    mock_get.return_value = (None, "La URL tardó demasiado en responder (timeout).")
    result = scrape_url("https://example.com")
    assert "error" in result
    assert "timeout" in result["error"].lower()


@patch("analyzer._http_get")
def test_scrape_url_http_error(mock_get):
    mock_get.return_value = (None, "Error HTTP al acceder a la URL: 404 Not Found")
    result = scrape_url("https://example.com/404")
    assert "error" in result
    assert "HTTP" in result["error"]


@patch("analyzer._http_get")
def test_scrape_url_general_exception(mock_get):
    mock_get.return_value = (None, "Connection refused")
    result = scrape_url("https://example.com")
    assert "error" in result


@patch("analyzer._http_get")
def test_scrape_url_no_paragraphs_fallback(mock_get):
    html = """<html><head><title>No Paragraphs</title></head>
    <body>
      <div>Short text.</div>
      <div>This is a longer text that should be captured by the fallback mechanism because it exceeds the minimum character threshold required for extraction by the scraper component.</div>
    </body></html>"""

    mock_resp = _make_mock_resp(html)
    mock_get.return_value = (mock_resp, None)

    result = scrape_url("https://example.com/no-p")
    assert "error" not in result


@patch("analyzer._http_get")
def test_scrape_url_removes_unwanted_tags(mock_get):
    html = """<html><body><article>
    <script>alert('bad')</script>
    <style>.css{}</style>
    <nav>Navigation</nav>
    <footer>Footer</footer>
    <p>This is the actual article content that should be extracted by the scraper for further processing and analysis by the system.</p>
    </article></body></html>"""

    mock_resp = _make_mock_resp(html)
    mock_get.return_value = (mock_resp, None)

    result = scrape_url("https://example.com/stripped")
    assert "Navigation" not in result["content"]
    assert "Footer" not in result["content"]
    assert "actual article content" in result["content"]


# ── parse_response ──

def test_parse_response_valid_json():
    data = '{"verdict": "REAL", "confidence_score": 85}'
    result = parse_response(data)
    assert result is not None
    assert result["verdict"] == "REAL"
    assert result["confidence_score"] == 85


def test_parse_response_with_code_fences():
    data = '```json\n{"verdict": "FALSO", "confidence_score": 20}\n```'
    result = parse_response(data)
    assert result is not None
    assert result["verdict"] == "FALSO"


def test_parse_response_with_backtick_fences():
    data = '```\n{"verdict": "SÁTIRA", "confidence_score": 10}\n```'
    result = parse_response(data)
    assert result is not None
    assert result["verdict"] == "SÁTIRA"


def test_parse_response_json_within_text():
    data = 'Some text before {"verdict": "ESTAFA", "confidence_score": 5} and text after'
    result = parse_response(data)
    assert result is not None
    assert result["verdict"] == "ESTAFA"


def test_parse_response_invalid_json():
    data = "this is not json"
    result = parse_response(data)
    assert result is None


def test_parse_response_empty():
    assert parse_response("") is None
    assert parse_response(None) is None


def test_parse_response_partial_json():
    data = '{"verdict": "REAL" incomplete json here'
    result = parse_response(data)
    assert result is None


# ── call_groq ──

@patch("analyzer.get_groq_client")
def test_call_groq_no_client(mock_get_client):
    mock_get_client.return_value = None
    result = call_groq("system prompt", "user prompt")
    assert result is None


@patch("analyzer.get_groq_client")
def test_call_groq_success(mock_get_client):
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"verdict": "REAL"}'
    mock_chunk = MagicMock()
    mock_chunk.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_chunk
    mock_get_client.return_value = mock_client

    result = call_groq("system prompt", "user prompt")
    assert result == '{"verdict": "REAL"}'


@patch("analyzer.get_groq_client")
def test_call_groq_fallback_model(mock_get_client):
    mock_client = MagicMock()
    # First model fails
    mock_client.chat.completions.create.side_effect = [
        Exception("Model overloaded"),
        MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"verdict": "REAL"}'))]
        ),
    ]
    mock_get_client.return_value = mock_client

    result = call_groq("system prompt", "user prompt")
    assert result == '{"verdict": "REAL"}'


@patch("analyzer.get_groq_client")
def test_call_groq_all_fail(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [
        Exception("First model fails"),
        Exception("Second model fails"),
    ]
    mock_get_client.return_value = mock_client

    result = call_groq("system prompt", "user prompt")
    assert result is None


# ── analyze_url ──

@patch("analyzer.get_groq_client")
def test_analyze_url_no_api_key(mock_get_client):
    mock_get_client.return_value = None
    result = analyze_url("https://example.com/news")
    assert "error" in result
    assert "GROQ_API_KEY" in result["error"]


@patch("analyzer.get_groq_client")
@patch("analyzer.scrape_url")
def test_analyze_url_scrape_fails(mock_scrape, mock_get_client):
    mock_get_client.return_value = MagicMock()
    mock_scrape.return_value = {"error": "Failed to fetch"}
    result = analyze_url("https://example.com/news")
    assert "error" in result


@patch("analyzer.get_groq_client")
@patch("analyzer.scrape_url")
@patch("analyzer.call_groq")
def test_analyze_url_success(mock_call_groq, mock_scrape, mock_get_client):
    mock_get_client.return_value = MagicMock()
    mock_scrape.return_value = {
        "content": "Titulo: Test\nDescripcion: Test\nTexto del articulo: Content",
        "title": "Test",
        "article_text": "Content",
    }
    mock_call_groq.return_value = json.dumps({
        "verdict": "REAL",
        "confidence_score": 85,
        "summary": "Test summary",
        "extracted_claims": ["Claim 1"],
        "reasoning": ["Reason 1"],
        "article_type": "informativa",
        "is_scam": False,
        "red_flags": [],
        "positive_signals": [],
    })

    result = analyze_url("https://milenio.com/politica/nota")
    assert "error" not in result
    assert result["analysis"]["verdict"] == "REAL"
    assert result["domain"] == "milenio.com"
    assert result["is_credible_source"] is True
    assert result["title"] == "Test"


@patch("analyzer.get_groq_client")
@patch("analyzer.scrape_url")
@patch("analyzer.call_groq")
def test_analyze_url_credible_domain_override(mock_call_groq, mock_scrape, mock_get_client):
    mock_get_client.return_value = MagicMock()
    mock_scrape.return_value = {
        "content": "Content",
        "title": "Test",
        "article_text": "",
    }
    # Groq returns FALSO with no red_flags for a credible domain
    mock_call_groq.return_value = json.dumps({
        "verdict": "FALSO",
        "confidence_score": 30,
        "summary": "Test",
        "extracted_claims": [],
        "reasoning": ["Some reason"],
        "article_type": "informativa",
        "is_scam": False,
        "red_flags": [],
        "positive_signals": [],
    })

    result = analyze_url("https://milenio.com/politica/nota")
    # Should be overridden to NO VERIFICABLE
    assert result["analysis"]["verdict"] == "NO VERIFICABLE"
    assert "reconocido" in result["analysis"]["reasoning"][-1].lower()


@patch("analyzer.get_groq_client")
@patch("analyzer.scrape_url")
@patch("analyzer.call_groq")
def test_analyze_url_non_credible_domain_no_override(mock_call_groq, mock_scrape, mock_get_client):
    mock_get_client.return_value = MagicMock()
    mock_scrape.return_value = {
        "content": "Content",
        "title": "Test",
        "article_text": "",
    }
    mock_call_groq.return_value = json.dumps({
        "verdict": "FALSO",
        "confidence_score": 30,
        "summary": "Test",
        "extracted_claims": [],
        "reasoning": ["Some reason"],
        "article_type": "opinion",
        "is_scam": True,
        "red_flags": ["Suspicious claims"],
        "positive_signals": [],
    })

    result = analyze_url("https://fakenews-site.xyz/clickbait")
    assert result["analysis"]["verdict"] == "FALSO"
    assert result["is_credible_source"] is False


@patch("analyzer.get_groq_client")
@patch("analyzer.scrape_url")
@patch("analyzer.call_groq")
def test_analyze_url_groq_no_verdict(mock_call_groq, mock_scrape, mock_get_client):
    mock_get_client.return_value = MagicMock()
    mock_scrape.return_value = {
        "content": "Content",
        "title": "Test",
        "article_text": "",
    }
    mock_call_groq.return_value = json.dumps({
        "confidence_score": 50,
        "summary": "Test",
    })

    result = analyze_url("https://example.com/news")
    assert "error" in result
