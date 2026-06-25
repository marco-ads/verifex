import os
import sys
import json
import cloudscraper
from curl_cffi import requests as curl_requests
import requests as std_requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from groq import Groq

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CREDIBLE_DOMAINS = {
    "milenio.com", "eluniversal.com.mx", "reforma.com", "proceso.com.mx",
    "jornada.com.mx", "lajornadadeoriente.com.mx", "excelsior.com.mx", "nmas.com.mx", "televisa.com",
    "cnn.com", "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com",
    "nytimes.com", "washingtonpost.com", "theguardian.com", "elpais.com",
    "infobae.com", "animalpolitico.com", "sinembargo.mx", "expansion.mx",
    "forbes.com.mx", "eleconomista.com.mx", "wradio.com.mx", "radioformula.com.mx",
    "cronica.com.mx", "24horas.mx",     "mvsnoticias.com", "noticieros.televisa.com",
    "aristeguinoticias.com",
}

FEW_SHOT_EXAMPLES = """
## EJEMPLO 1 — REAL (noticia periodística estándar)
Titular: "Banxico eleva tasa de interés a 11.25% por presiones inflacionarias"
Dominio: eluniversal.com.mx (reconocido)
Contenido: Reporta el anuncio oficial del Banco de México, cita declaraciones del gobernador, incluye contexto económico.
Veredicto:
{"verdict": "REAL", "confidence_score": 92, "summary": "El Banxico subió la tasa...", "extracted_claims": ["Banxico subió tasa a 11.25%", "presiones inflacionarias"], "reasoning": ["Medio reconocido (El Universal)", "Cita fuente oficial (gobernador del Banxico)", "Lenguaje neutral sin sensacionalismo"], "article_type": "informativa", "is_scam": false, "red_flags": [], "positive_signals": ["Medio reconocido", "Cita fuente oficial", "Reporta hecho verificable"]}

## EJEMPLO 2 — FALSO (afirmación médica falsa sin respaldo)
Titular: "¡Científicos de Harvard confirman que el limón cura el cáncer!"
Dominio: saludmilagrosa.net (no reconocido)
Contenido: Afirmación extraordinaria sin citar estudio específico, autor ni fecha. Titular con signos de exclamación. Lenguaje alarmista ("descubrimiento que ocultan").
Veredicto:
{"verdict": "FALSO", "confidence_score": 95, "summary": "Afirmación falsa sobre cura del cáncer...", "extracted_claims": ["limón cura el cáncer", "Harvard lo confirmó"], "reasoning": ["Afirmación médica extraordinaria sin respaldo de estudio verificable", "Titular sensacionalista con clickbait", "Sin autor, fecha ni fuente primaria", "Dominio no reconocido"], "article_type": "clickbait", "is_scam": true, "red_flags": ["Afirmación médica extraordinaria sin fuentes", "Clickbait", "Sin autor ni fecha", "Dominio desconocido"], "positive_signals": []}

## EJEMPLO 3 — NO VERIFICABLE (testimonio ambiguo sin fuentes)
Titular: "Fuentes anónimas revelan irregularidades en la secretaría"
Dominio: sitiodenoticias.mx (poco conocido)
Contenido: Acusaciones sin nombres concretos, sin documentos, sin fecha específica del evento.
Veredicto:
{"verdict": "NO VERIFICABLE", "confidence_score": 40, "summary": "Acusaciones sin fuentes concretas...", "extracted_claims": ["irregularidades en secretaría"], "reasoning": ["No se citan fuentes nombradas", "Sin documentos ni pruebas concretas", "Medio no reconocido ni contrastable"], "article_type": "denuncia", "is_scam": false, "red_flags": ["Fuentes anónimas", "Sin pruebas documentales"], "positive_signals": []}
"""

SYSTEM_PROMPT = """Eres VERIFEX, analizador experto de credibilidad de noticias en México y América Latina.

Tu tarea es analizar el contenido de un artículo periodístico y determinar su veracidad.
Debes CITAR TEXTUALMENTE las partes del artículo que sustentan tu veredicto (incluye frases exactas entre comillas en tu reasoning).

### REGLAS DE CLASIFICACIÓN (ordena de mayor a menor prioridad):

1. **CITA TEXTUAL OBLIGATORIA** — Cada punto en reasoning y cada extracted_claim debe incluir la frase exacta del artículo entre comillas. Ej: "El artículo dice: '...textual...'"

2. **REAL** → El contenido proviene de un medio establecido, reporta hechos de manera periodística estándar, cita fuentes identificables y usa lenguaje neutral. Un artículo normal de Milenio, Reforma, El Universal, Reuters, AP, BBC o similar es REAL aunque no puedas verificar cada detalle individualmente.

3. **FALSO** → SOLO si hay información DEMOSTRABLEMENTE INCORRECTA: afirmaciones que contradicen hechos establecidos, citas fabricadas, estadísticas inventadas, teorías conspirativas sin respaldo, titulares que NO corresponden al contenido real. NO uses FALSO por "no poder verificar".

4. **NO VERIFICABLE** → Cuando el contenido hace afirmaciones serias pero sin fuentes verificables, o cuando hay ambigüedad sin señales claras de fabricación. Es el veredicto por defecto para casos dudosos.

5. **SÁTIRA** → Solo si el formato, tono y contexto indican claramente humor/parodia.

6. **ESTAFA** → Solo para contenido diseñado para defraudar: phishing, productos milagro, inversiones falsas, suplantación de identidad.

### BANDERAS ROJAS A DETECTAR:
- Titular sensacionalista con signos de exclamación o MAYÚSCULAS
- Afirmaciones extraordinarias sin respaldo de fuentes verificables
- Ausencia de autor, fecha o fuentes primarias
- Lenguaje alarmista o emocional extremo ("lo que no quieren que sepas", "impactante")
- Promesas de curas milagrosas o productos con resultados garantizados
- Artículo de opinion presentado como noticia informativa
- Contradicción entre el titular y el contenido real

### TIPO DE ARTÍCULO (article_type):
- informativa → Noticia neutral que reporta hechos
- comercial → Anuncio empresarial, promoción, lanzamiento de producto
- opinion → Columna, editorial o contenido con postura del autor
- clickbait → Titular engañoso que no refleja el contenido
- denuncia → Reportaje de investigación o denuncia social

IMPORTANTE sobre article_type: Si es opinion, el estándar de veracidad es diferente — no la marques como FALSO por tener sesgo, a menos que contenga datos factualmente incorrectos.

Aplica estos ejemplos como guía:
""" + FEW_SHOT_EXAMPLES + """
Responde ÚNICAMENTE en JSON válido en español. Sin texto fuera del JSON. Sin bloques de código."""

USER_PROMPT_TEMPLATE = """Analiza este contenido periodístico de la URL: {url}
Dominio: {domain}
¿Es dominio de medio reconocido? {is_credible}

CONTENIDO EXTRAÍDO:
{content}

{similar_context}
INSTRUCCIONES ESPECÍFICAS:
1. CITA TEXTUALMENTE las partes relevantes del artículo entre comillas en cada punto de reasoning y extracted_claims.
2. Si hay "CONTEXTO DE OTRAS FUENTES" arriba, compáralo con el artículo analizado.
3. Si el dominio es de un medio reconocido y el contenido parece periodismo estándar, el veredicto debe ser REAL a menos que haya errores factuales EVIDENTES y DEMOSTRABLES.
4. Distingue entre artículo de opinion (permite sesgo editorial) y noticia informativa (debe ser neutral).
5. Para artículo_type="opinion", no uses FALSO solo por el sesgo — solo si hay datos factualmente incorrectos.

Responde con este JSON exacto (sin texto fuera del JSON):
{{
  "verdict": "REAL|FALSO|SÁTIRA|ESTAFA|NO VERIFICABLE",
  "confidence_score": número entero del 0 al 100,
  "summary": "resumen neutral del artículo en 2-3 oraciones",
  "extracted_claims": ["afirmación principal con cita textual del artículo", "dato clave 2 con cita textual", "dato clave 3 con cita textual"],
  "reasoning": ["razón detallada 1 CITANDO el texto relevante del artículo", "razón 2 con cita textual", "razón 3 con cita textual"],
  "article_type": "informativa|comercial|opinion|clickbait|denuncia",
  "is_scam": false,
  "red_flags": ["bandera roja concreta citando el texto que la genera, o lista vacía"],
  "positive_signals": ["señal positiva concreta citando el texto relevante, o lista vacía"]
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


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

def _get_platform() -> str:
    p = sys.platform.lower()
    if p.startswith("linux"):
        return "linux"
    if p.startswith("win"):
        return "windows"
    if p.startswith("darwin"):
        return "darwin"
    return "linux"

def _try_cloudscraper(url: str) -> tuple:
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": _get_platform(), "desktop": True},
            delay=15,
        )
        scraper.headers.update(BROWSER_HEADERS)
        for attempt in range(3):
            try:
                resp = scraper.get(url, timeout=30)
                resp.raise_for_status()
                return resp, None
            except Exception:
                if attempt == 2:
                    raise
                continue
        return None, "cloudscraper: retries exhausted"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def _try_curl_cffi(url: str) -> tuple:
    last_err = None
    for version in ("chrome124", "chrome123", "chrome120", "safari17_0", "safari16_5"):
        try:
            resp = curl_requests.get(url, impersonate=version, headers=BROWSER_HEADERS, timeout=30)
            resp.raise_for_status()
            return resp, None
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
    return None, f"curl_cffi: {last_err}"

def _try_requests(url: str) -> tuple:
    last_err = None
    for attempt in range(2):
        try:
            resp = std_requests.get(url, headers=BROWSER_HEADERS, timeout=15, verify=attempt == 1)
            resp.raise_for_status()
            return resp, None
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
    return None, f"requests: {last_err}"

def _try_playwright(url: str) -> tuple:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            page.wait_for_timeout(15000)
            content = page.content()
            browser.close()
            if "just a moment" not in content.lower():
                mock_resp = type("obj", (), {"text": content, "status_code": 200})()
                return mock_resp, None
            return None, "Cloudflare challenge not resolved"
    except ImportError:
        return None, "playwright: not installed"
    except Exception as e:
        return None, f"playwright: {type(e).__name__}: {e}"

def _http_get(url: str) -> tuple:
    all_errs = []
    for name, attempt in [
        ("cloudscraper", _try_cloudscraper),
        ("curl_cffi", _try_curl_cffi),
        ("requests", _try_requests),
        ("playwright", _try_playwright),
    ]:
        resp, err = attempt(url)
        if resp:
            return resp, None
        all_errs.append(f"{name}:{err}")
    return None, " | ".join(all_errs)

def _extract_from_html(html: str, domain: str = "") -> dict:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe", "noscript"]):
        tag.decompose()

    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""

    meta = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
    meta_desc = meta.get("content", "") if meta else ""

    article = soup.find("article") or soup.find("main") or soup.body

    if "instagram.com" in domain:
        if meta_desc and len(meta_desc) > 40:
            clean = meta_desc
            for prefix in [" on Instagram: ", " en Instagram: "]:
                idx = clean.find(prefix)
                if idx > 0:
                    clean = clean[idx + len(prefix):]
            content = (
                f"Título: {title}\n"
                f"Descripción: {meta_desc}\n"
                f"Texto del artículo: {clean[:5000]}"
            )
            return {"content": content, "title": title, "article_text": clean[:2000]}

        for el in soup.find_all(attrs={"role": "comment"}):
            el.decompose()
        for el in soup.find_all(class_=lambda c: c and "comment" in c.lower()):
            el.decompose()

    paragraphs = article.find_all("p") if article else soup.find_all("p")

    body_parts = []
    for p in paragraphs[:50]:
        text = p.get_text(strip=True)
        if len(text) > 40:
            body_parts.append(text)

    body = " ".join(body_parts)

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


def scrape_url(url: str) -> dict:
    resp, err = _http_get(url)
    if err or resp is None:
        return {"error": err or "No se pudo acceder a la URL"}
    domain = get_domain(url)
    try:
        result = _extract_from_html(resp.text, domain=domain)

        if len(result.get("article_text", "")) < 500:
            playwright_resp, _ = _try_playwright(url)
            if playwright_resp:
                pw_result = _extract_from_html(playwright_resp.text, domain=domain)
                if len(pw_result.get("article_text", "")) > len(result.get("article_text", "")):
                    result = pw_result

        return result
    except Exception as e:
        return {"error": f"Error al procesar el contenido: {str(e)}"}


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

    from news_finder import find_similar_news
    similar = find_similar_news(title, max_results=4)
    if similar:
        lines = ["CONTEXTO DE OTRAS FUENTES (para comparación):"]
        for s in similar:
            src = s.get("source", "Fuente desconocida")
            t = s.get("title", "Sin título")
            lines.append(f"- {src}: \"{t}\"")
        similar_context = "\n".join(lines) + "\n"
    else:
        similar_context = ""

    prompt = USER_PROMPT_TEMPLATE.format(
        url=url,
        domain=domain,
        is_credible=is_credible,
        content=content,
        similar_context=similar_context,
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
