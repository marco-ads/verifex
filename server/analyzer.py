import os
import sys
import json
import re
import random
import cloudscraper
from curl_cffi import requests as curl_requests
import requests as std_requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from groq import Groq

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CREDIBLE_DOMAINS = {
    "milenio.com", "eluniversal.com.mx", "reforma.com", "proceso.com.mx",
    "jornada.com.mx", "lajornadadeoriente.com.mx", "excelsior.com.mx", "nmas.com.mx", "televisa.com",
    "cnn.com", "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com",
    "nytimes.com", "washingtonpost.com", "theguardian.com", "elpais.com",
    "infobae.com", "animalpolitico.com", "sinembargo.mx", "expansion.mx",
    "forbes.com.mx", "eleconomista.com.mx", "wradio.com.mx", "radioformula.com.mx",
    "cronica.com.mx", "24horas.mx", "mvsnoticias.com", "noticieros.televisa.com",
    "aristeguinoticias.com",
    "heraldodemexico.com.mx", "elheraldo.hn", "elheraldo.co",
}

SOCIAL_MEDIA_DOMAINS = {
    "instagram.com", "threads.net", "threads.com", "x.com", "twitter.com",
    "tiktok.com", "facebook.com", "fb.com",
}

SOCIAL_MEDIA_PROMPT = """
### INSTRUCCIONES ESPECÍFICAS PARA {platform} (ANULAN LAS REGLAS GENERALES):
Este contenido es de {platform}, una red social. Primero identifica la categoría y asígnale el veredicto:

**Reglas (en este orden):**
- Categoría "noticia" (reporta hechos actuales reales) → **REAL**. Sin excusas de "falta de fuentes".
- Categoría "humor" o "sátira" → **SÁTIRA**. Confianza >= 80. NUNCA FALSO.
- Categoría "noticia_falsa" (afirmaciones falsas/fantásticas) → **FALSO**.
- Categoría "opinión" o "vida_personal" → **NO VERIFICABLE**. NUNCA FALSO.

Añade "content_category" al JSON con la categoría.

### EJEMPLOS:
---
EJEMPLO RS 1 — NOTICIA REAL:
Contenido: "ÚLTIMA HORA: Irán lanzó misiles a Israel. El mundo en alerta."
Categoría: noticia
→ {{"verdict": "REAL", "confidence_score": 85, "content_category": "noticia"}}
---
EJEMPLO RS 2 — HUMOR:
Contenido: "Mi cerebro a las 3 AM: ¿y si los aliens esperan que termine su serie? 😂"
Categoría: humor
→ {{"verdict": "SÁTIRA", "confidence_score": 90, "content_category": "humor"}}
---
EJEMPLO RS 3 — NOTICIA FALSA:
Contenido: "¡URGENTE! Gobierno declara ley marcial. No salgan de casa."
Categoría: noticia_falsa
→ {{"verdict": "FALSO", "confidence_score": 95, "content_category": "noticia_falsa"}}
---
EJEMPLO RS 4 — VIDA PERSONAL:
Contenido: "Hoy fue un día increíble, el atardecer en la playa era perfecto."
Categoría: vida_personal
→ {{"verdict": "NO VERIFICABLE", "confidence_score": 80, "content_category": "vida_personal"}}
"""

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
Responde ÚNICAMENTE en JSON válido. Sin texto fuera del JSON. Sin bloques de código.

IMPORTANTE: Todos los campos de texto (summary, extracted_claims, reasoning, red_flags, positive_signals) deben incluir su versión en ambos idiomas usando el sufijo '_en' para inglés. Ejemplo:
{{
  "verdict": "REAL",
  "confidence_score": 85,
  "summary": "texto en español",
  "summary_en": "English text",
  "extracted_claims": ["afirmación en español"],
  "extracted_claims_en": ["claim in English"],
  "reasoning": ["razón en español"],
  "reasoning_en": ["reason in English"],
  "article_type": "informativa",
  "is_scam": false,
  "red_flags": ["bandera roja en español"],
  "red_flags_en": ["red flag in English"],
  "positive_signals": ["señal positiva en español"],
  "positive_signals_en": ["positive signal in English"]
}}"""

USER_PROMPT_BASE = """Analiza este contenido periodístico de la URL: {url}
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
  "summary": "resumen neutral del artículo en 2-3 oraciones (ESPAÑOL)",
  "summary_en": "neutral article summary in 2-3 sentences (ENGLISH)",
  "extracted_claims": ["afirmación principal con cita textual en ESPAÑOL"],
  "extracted_claims_en": ["main claim with textual citation in ENGLISH"],
  "reasoning": ["razón detallada CITANDO el texto en ESPAÑOL"],
  "reasoning_en": ["detailed reasoning citing text in ENGLISH"],
  "article_type": "informativa|comercial|opinion|clickbait|denuncia",
  "is_scam": false,
  "red_flags": ["bandera roja concreta en ESPAÑOL"],
  "red_flags_en": ["concrete red flag in ENGLISH"],
  "positive_signals": ["señal positiva concreta en ESPAÑOL"],
  "positive_signals_en": ["concrete positive signal in ENGLISH"]
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


USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
]

# Optional: proxy URL for scraping behind Cloudflare/WAF
# Set HTTP_PROXY env var to use a proxy (e.g. http://user:pass@proxy:port)
SCRAPING_PROXY = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")

BROWSER_HEADERS = {
    "User-Agent": USER_AGENTS[0],
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
    last_err = None
    profiles = [
        {"browser": "chrome", "platform": _get_platform(), "desktop": True},
        {"browser": "firefox", "platform": _get_platform(), "desktop": True},
        {"browser": "chrome", "platform": "windows", "desktop": True},
        {"browser": "firefox", "platform": "windows", "desktop": True},
    ]
    for profile in profiles:
        for attempt in range(2):
            try:
                headers = BROWSER_HEADERS.copy()
                headers["User-Agent"] = random.choice(USER_AGENTS)
                scraper = cloudscraper.create_scraper(browser=profile, delay=5)
                scraper.headers.update(headers)
                proxies = {"http": SCRAPING_PROXY, "https": SCRAPING_PROXY} if SCRAPING_PROXY else None
                resp = scraper.get(url, timeout=30, proxies=proxies)
                resp.raise_for_status()
                return resp, None
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                continue
    return None, f"cloudscraper: {last_err}"

def _try_curl_cffi(url: str) -> tuple:
    last_err = None
    versions = ["chrome123", "chrome120", "safari17_0", "chrome124"]
    for version in versions:
        try:
            headers = BROWSER_HEADERS.copy()
            headers["User-Agent"] = random.choice(USER_AGENTS)
            proxies = {"http": SCRAPING_PROXY, "https": SCRAPING_PROXY} if SCRAPING_PROXY else None
            resp = curl_requests.get(url, impersonate=version, headers=headers, timeout=30, proxies=proxies)
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
            headers = BROWSER_HEADERS.copy()
            headers["User-Agent"] = random.choice(USER_AGENTS)
            proxies = {"http": SCRAPING_PROXY, "https": SCRAPING_PROXY} if SCRAPING_PROXY else None
            resp = std_requests.get(url, headers=headers, timeout=15, verify=attempt == 1, proxies=proxies)
            resp.raise_for_status()
            return resp, None
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
    return None, f"requests: {last_err}"

def _try_playwright(url: str) -> tuple:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright: not installed"

    PW_USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    ]

    engines = [
        ("firefox", lambda p: p.firefox),
        ("chromium", lambda p: p.chromium),
    ]

    last_err = None
    for engine_name, engine_getter in engines:
        for attempt in range(2):
            try:
                with sync_playwright() as pw:
                    launch_args = ["--no-sandbox"]
                    browser = engine_getter(pw).launch(
                        headless=True,
                        args=launch_args,
                    )
                    ua = random.choice(PW_USER_AGENTS)
                    ctx_kwargs = {
                        "user_agent": ua,
                        "viewport": {"width": 1920, "height": 1080},
                        "locale": "es-MX",
                        "timezone_id": "America/Mexico_City",
                        "device_scale_factor": 1,
                    }
                    if SCRAPING_PROXY:
                        ctx_kwargs["proxy"] = {"server": SCRAPING_PROXY}
                    context = browser.new_context(**ctx_kwargs)
                    page = context.new_page()

                    cf_indicators = [
                        "just a moment", "checking your browser",
                        "please wait", "attention required",
                        "cloudflare", "__cf_chl_opt",
                    ]

                    # Load page — use domcontentloaded (fast), then poll for Cloudflare
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")

                    # Poll every second up to 35s for Cloudflare to resolve
                    challenge_resolved = False
                    for _ in range(35):
                        page.wait_for_timeout(1000)
                        content = page.content()

                        # Check if Cloudflare challenge is gone
                        if not any(ind in content.lower() for ind in cf_indicators):
                            challenge_resolved = True
                            break

                        # If page title contains real content, we're through
                        title = page.title()
                        if title and len(title) > 10 and not any(ind in title.lower() for ind in cf_indicators):
                            challenge_resolved = True
                            break

                    browser.close()

                    if challenge_resolved:
                        mock_resp = type("obj", (), {"text": content, "status_code": 200})()
                        return mock_resp, None

                    last_err = f"{engine_name}: Cloudflare not resolved after 35s"
            except Exception as e:
                last_err = f"{engine_name}: {type(e).__name__}: {e}"
                continue

    return None, f"playwright: {last_err}"

LOGIN_PATTERNS = [
    "iniciar sesión", "contraseña", "olvidaste tu contraseña",
    "crear cuenta nueva", "correo electrónico o número de celular",
    "log in", "create new account", "forgot password",
    "sign up to see", "log in to see",
]


def _is_login_blocked_page(title: str, body: str) -> bool:
    if len(body) >= 800:
        return False
    text = f"{title} {body}".lower()
    hits = sum(1 for p in LOGIN_PATTERNS if p in text)
    return hits >= 2


def _extract_facebook_post_id(url: str) -> str | None:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    segments = path.split("/")

    # /{username}/posts/{post_id}
    if "posts" in segments:
        idx = segments.index("posts")
        if idx + 1 < len(segments):
            return segments[idx + 1]

    # /{username}/videos/{post_id}
    if "videos" in segments:
        idx = segments.index("videos")
        if idx + 1 < len(segments):
            return segments[idx + 1]

    # /{username}/photos/{post_id}
    if "photos" in segments:
        idx = segments.index("photos")
        if idx + 1 < len(segments):
            return segments[idx + 1]

    # story.php?story_fbid={post_id}&id={user_id}
    qs = parse_qs(parsed.query)
    if "story_fbid" in qs:
        return qs["story_fbid"][0]

    # photo.php?fbid={post_id}
    if "fbid" in qs:
        return qs["fbid"][0]

    return None


def _try_facebook_graph_api(url: str) -> dict | None:
    app_id = os.environ.get("FACEBOOK_APP_ID")
    app_secret = os.environ.get("FACEBOOK_APP_SECRET")
    if not app_id or not app_secret:
        return None

    post_id = _extract_facebook_post_id(url)
    if not post_id:
        return None

    token = f"{app_id}|{app_secret}"
    try:
        resp = std_requests.get(
            f"{FB_GRAPH_API}/{post_id}",
            params={
                "fields": "message,story,created_time,from,permalink_url",
                "access_token": token,
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        if "error" in data:
            return None

        text_parts = []
        if data.get("story"):
            text_parts.append(data["story"])
        if data.get("message"):
            text_parts.append(data["message"])
        if data.get("from", {}).get("name"):
            text_parts.insert(0, f"Publicado por: {data['from']['name']}")

        body = " - ".join(text_parts)
        title = data.get("story", data.get("message", ""))[:100]

        return {
            "content": f"Título: {title}\nTexto del artículo: {body[:5000]}",
            "title": title,
            "article_text": body[:2000],
        }
    except Exception:
        return None


def _try_google_cache(url: str) -> tuple:
    """Fallback: fetch from Google's web cache (bypasses Cloudflare entirely)."""
    cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
    for attempt in range(2):
        try:
            headers = BROWSER_HEADERS.copy()
            headers["User-Agent"] = random.choice(USER_AGENTS)
            resp = std_requests.get(cache_url, headers=headers, timeout=20)
            resp.raise_for_status()
            return resp, None
        except Exception as e:
            continue
    return None, "google_cache: blocked or not cached"

def _http_get(url: str) -> tuple:
    all_errs = []
    for name, attempt in [
        ("cloudscraper", _try_cloudscraper),
        ("curl_cffi", _try_curl_cffi),
        ("requests", _try_requests),
        ("playwright", _try_playwright),
        ("google_cache", _try_google_cache),
    ]:
        resp, err = attempt(url)
        if resp:
            return resp, None
        all_errs.append(f"{name}:{err}")
    return None, " | ".join(all_errs)

def _extract_from_html(html: str, domain: str = "") -> dict:
    soup = BeautifulSoup(html, "lxml")

    # Google cache: strip the outer wrapper and use the cached content div
    cache_div = soup.find("div", id="google-cache") or soup.find("div", class_="cached-page")
    if cache_div:
        inner = cache_div.decode_contents()
        soup = BeautifulSoup(inner, "lxml")
    else:
        # Some Google cache formats wrap in <pre> with the raw HTML
        pre = soup.find("pre")
        if pre and "google" in html.lower()[:500] and len(pre.get_text(strip=True)) > 1000:
            inner = pre.decode_contents()
            soup = BeautifulSoup(inner, "lxml")

    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""

    meta = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
    meta_desc = meta.get("content", "") if meta else ""

    # Threads: extraer posts del JSON embebido
    threads_text = ""
    if "threads.com" in domain or "threads.net" in domain:
        for script in soup.find_all("script", type="application/json"):
            s = script.string or ""
            if "text_post_app_thread" in s:
                texts = re.findall(r'"text"\s*:\s*"((?:\\.|[^"\\])*)"', s)
                cleaned = []
                for t in texts:
                    decoded = t.replace("\\n", " ")
                    decoded = re.sub(r"\\u[0-9a-fA-F]{4}", "", decoded)
                    if len(decoded) > 15:
                        cleaned.append(decoded)
                if cleaned:
                    threads_text = "\n".join(cleaned[:20])
                break

    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "iframe", "noscript"]):
        tag.decompose()

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

    if not body or len(body) < 500:
        all_p = soup.body.find_all("p") if soup.body else soup.find_all("p")
        all_body_parts = []
        for p in all_p[:75]:
            text = p.get_text(strip=True)
            if len(text) > 40 and text not in body_parts:
                all_body_parts.append(text)
        wider_body = " ".join(all_body_parts)
        if len(wider_body) > len(body):
            body = wider_body

    if not body or len(body) < 100:
        text_content = article.get_text(separator=" ", strip=True) if article else ""
        lines = [t.strip() for t in text_content.split() if len(t.strip()) > 60]
        body = " ".join(lines[:80]) if lines else text_content[:5000]

    if threads_text:
        body = f"{threads_text}\n\n{body}"

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

        is_fb = "facebook.com" in domain or "fb.com" in domain

        if _is_login_blocked_page(result.get("title", ""), result.get("article_text", "")):
            if is_fb:
                fb_result = _try_facebook_graph_api(url)
                if fb_result:
                    return fb_result
                app_id = os.environ.get("FACEBOOK_APP_ID")
                app_secret = os.environ.get("FACEBOOK_APP_SECRET")
                if not app_id or not app_secret:
                    return {"error": (
                        "Facebook bloquea el acceso automatizado. "
                        "Para analizar posts de Facebook:\n"
                        "1. Crea una app en https://developers.facebook.com\n"
                        "2. Copia el App ID y App Secret a server/.env:\n"
                        "   FACEBOOK_APP_ID=tu_app_id\n"
                        "   FACEBOOK_APP_SECRET=tu_app_secret"
                    )}
                return {"error": "No se pudo extraer el contenido de esta publicación de Facebook. Verifica que el post sea público y tus credenciales de API sean correctas."}

            return {"error": "La página solicitada requiere inicio de sesión o bloquea el acceso automatizado."}

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

    prompt = USER_PROMPT_BASE.format(
        url=url,
        domain=domain,
        is_credible=is_credible,
        content=content,
        similar_context=similar_context,
    )

    # Extract social media context from URL
    social_context = ""
    if "threads.com" in domain or "threads.net" in domain:
        m = re.search(r"@(\w+)", url)
        if m:
            social_context = f"\nUsuario/publicación objetivo: @{m.group(1)}\n"

    for sm_domain, sm_name in [
        ("instagram.com", "Instagram"),
        ("threads.net", "Threads"),
        ("threads.com", "Threads"),
        ("x.com", "X/Twitter"),
        ("twitter.com", "X/Twitter"),
        ("tiktok.com", "TikTok"),
    ]:
        if sm_domain in domain:
            prompt += SOCIAL_MEDIA_PROMPT.format(platform=sm_name)
            prompt += social_context
            break

    raw = call_groq(SYSTEM_PROMPT, prompt)
    if raw:
        parsed = parse_response(raw)
        if parsed and "verdict" in parsed:
            if is_credible == "SÍ" and parsed.get("verdict") == "FALSO":
                parsed["verdict"] = "NO VERIFICABLE"
                parsed["reasoning"] = parsed.get("reasoning", []) + [
                    f"El dominio {domain} es un medio de comunicación reconocido. "
                    "Contenido de fuente fiable reclasificado como NO VERIFICABLE."
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
