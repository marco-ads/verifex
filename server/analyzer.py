import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from groq import Groq

CREDIBLE_DOMAINS = {
    "milenio.com", "eluniversal.com.mx", "reforma.com", "proceso.com.mx",
    "jornada.com.mx", "excelsior.com.mx", "nmas.com.mx", "televisa.com",
    "cnn.com", "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com",
    "nytimes.com", "washingtonpost.com", "theguardian.com", "elpais.com",
    "infobae.com", "animalpolitico.com", "sinembargo.mx", "expansion.mx",
    "forbes.com.mx", "eleconomista.com.mx", "wradio.com.mx", "radioformula.com.mx",
    "cronica.com.mx", "24horas.mx", "mvsnoticias.com", "noticieros.televisa.com",
}

SYSTEM_PROMPT = """Eres VERIFEX, analizador experto de credibilidad de noticias en México y América Latina.

REGLAS ABSOLUTAS DE CLASIFICACIÓN — síguelas al pie de la letra:

1. REAL → El contenido proviene de un medio de comunicación establecido Y reporta hechos de manera periodística estándar. Un artículo periodístico normal de Milenio, nMAS, El Universal, Reforma, Proceso, Reuters, AP, BBC o cualquier medio reconocido es REAL aunque no puedas verificar cada dato individualmente.

2. FALSO → SOLO úsalo si el contenido contiene información DEMOSTRABLE Y CLARAMENTE INCORRECTA, citas fabricadas, estadísticas inventadas, o afirmaciones que contradicen hechos establecidos. NO uses FALSO solo porque no puedes verificar algo.

3. NO VERIFICABLE → Usa esto cuando las afirmaciones son serias pero requieren investigación adicional y no hay señales claras de fabricación. Es el veredicto correcto para contenido ambiguo.

4. SÁTIRA → SOLO si el contenido es claramente humorístico, paródico o de entretenimiento, no informativo real.

5. ESTAFA → SOLO para contenido diseñado para defraudar, phishing, o productos/inversiones fraudulentos.

CRITERIO CLAVE: Si el artículo parece periodismo profesional normal de un medio reconocido → REAL.
Si hay señales claras de fabricación o errores factuales graves → FALSO.
Si es ambiguo o no puedes confirmar → NO VERIFICABLE.

Responde ÚNICAMENTE en JSON válido en español. Sin texto fuera del JSON. Sin bloques de código."""

USER_PROMPT_TEMPLATE = """Analiza este contenido periodístico de la URL: {url}
Dominio: {domain}
¿Es dominio de medio reconocido? {is_credible}

CONTENIDO EXTRAÍDO:
{content}

IMPORTANTE: Si el dominio es de un medio reconocido y el contenido parece periodismo estándar, el veredicto debe ser REAL a menos que haya errores factuales EVIDENTES y DEMOSTRABLES.

Responde con este JSON exacto (sin texto fuera del JSON):
{{
  "verdict": "REAL|FALSO|SÁTIRA|ESTAFA|NO VERIFICABLE",
  "confidence_score": número entero del 0 al 100,
  "summary": "resumen neutral del artículo en 2-3 oraciones",
  "extracted_claims": ["afirmación principal del artículo", "dato clave 2", "dato clave 3"],
  "reasoning": ["razón detallada 1 para el veredicto", "razón 2", "razón 3"],
  "red_flags": ["señal de alarma concreta si existe, o lista vacía"],
  "positive_signals": ["señal positiva concreta si existe, o lista vacía"]
}}"""


def get_groq_client() -> Groq | None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def call_groq(system_prompt: str, user_prompt: str) -> str | None:
    client = get_groq_client()
    if not client:
        return None
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception:
            continue
    return None


def get_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def scrape_url(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe", "noscript"]):
            tag.decompose()

        title_el = soup.find("title")
        title = title_el.get_text(strip=True) if title_el else ""

        meta = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
        meta_desc = meta.get("content", "") if meta else ""

        article = soup.find("article") or soup.find("main") or soup.body
        paragraphs = article.find_all("p") if article else soup.find_all("p")

        body_parts = []
        for p in paragraphs[:50]:
            text = p.get_text(strip=True)
            if len(text) > 40:
                body_parts.append(text)

        body = " ".join(body_parts)

        # If no paragraphs found, grab all text from the article container
        if not body or len(body) < 100:
            text_content = article.get_text(separator=" ", strip=True) if article else ""
            lines = [t.strip() for t in text_content.split() if len(t.strip()) > 60]
            body = " ".join(lines[:80]) if lines else text_content[:5000]

        content = (
            f"Título: {title}\n"
            f"Descripción: {meta_desc}\n"
            f"Texto del artículo: {body[:5000]}"
        )
        return {"content": content, "title": title, "article_text": body[:2000]}
    except requests.exceptions.Timeout:
        return {"error": "La URL tardó demasiado en responder (timeout)."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Error HTTP al acceder a la URL: {e}"}
    except Exception as e:
        return {"error": f"No se pudo acceder a la URL: {str(e)}"}


def parse_response(text: str) -> dict | None:
    if not text:
        return None
    text = text.strip()
    if "```" in text:
        lines = text.split("\n")
        filtered = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(filtered)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return None


def analyze_url(url: str) -> dict:
    if not get_groq_client():
        return {
            "error": (
                "GROQ_API_KEY no configurada. "
                "Copia server/.env.example a server/.env y agrega tu API key de Groq.\n"
                "Obtén una gratis en: https://console.groq.com"
            ),
            "status": 503,
        }

    scraped = scrape_url(url)
    if "error" in scraped:
        return {"error": scraped["error"], "status": 500}

    content = scraped["content"]
    title = scraped["title"]
    article_text = scraped.get("article_text", "")

    domain = get_domain(url)
    is_credible = "SÍ" if domain in CREDIBLE_DOMAINS else "No confirmado"

    prompt = USER_PROMPT_TEMPLATE.format(
        url=url,
        domain=domain,
        is_credible=is_credible,
        content=content,
    )

    raw = call_groq(SYSTEM_PROMPT, prompt)
    if raw:
        parsed = parse_response(raw)
        if parsed and "verdict" in parsed:
            if (
                is_credible == "SÍ"
                and parsed.get("verdict") == "FALSO"
                and not parsed.get("red_flags")
            ):
                parsed["verdict"] = "NO VERIFICABLE"
                parsed["reasoning"] = parsed.get("reasoning", []) + [
                    f"El dominio {domain} es un medio de comunicación reconocido."
                ]

            return {
                "analysis": parsed,
                "title": title,
                "article_text": article_text,
                "domain": domain,
                "is_credible_source": is_credible == "SÍ",
            }

    return {
        "error": "No se obtuvo respuesta válida de Groq. Verifica tu API key y la conexión a internet.",
        "status": 500,
    }
