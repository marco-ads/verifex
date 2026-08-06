"""Búsqueda de noticias similares vía Google News RSS.

Estrategia de búsqueda exhaustiva:
1. Genera varias consultas candidatas desde el título (más precisa primero):
   - El título completo
   - Frases de entidades (nombres propios/números) entrecomilladas
   - La entidad principal
2. Consulta Google News RSS probando varias ediciones regionales hasta
   obtener resultados (MX latino → MX → es general).
3. Filtra la noticia original (por similitud de título) y deduplica.
"""
import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

# Stopwords sin valor de búsqueda (ES/EN)
STOPWORDS = {
    "el", "la", "los", "las", "lo", "le", "les", "un", "una", "unos", "unas",
    "de", "del", "y", "e", "a", "al", "en", "por", "para", "con", "sin",
    "sobre", "entre", "tras", "que", "quien", "quienes", "se", "su", "sus",
    "es", "era", "fue", "fueron", "son", "ser", "estar", "estan", "esta",
    "como", "contra", "hasta", "desde", "ante", "segun", "mas", "menos",
    "ya", "asi", "cuando", "donde", "como", "porque", "pero", "ademas",
    "tambien", "pese", "caso", "casos", "noticia", "noticias", "tras",
    "the", "of", "and", "to", "in", "for", "with", "on", "at", "by", "from",
    "an", "this", "that", "these", "those", "its", "his", "her", "their",
    "after", "before", "during", "about", "into", "over", "under", "when",
}

# Verbos/acciones típicos de inicio de titular que no son entidades
TITLE_VERBS = {
    "detenido", "detenidos", "detienen", "detiene", "detuvo", "detuvieron",
    "muere", "muertos", "muertas", "mueren", "matan", "mataron", "asesinan",
    "hallan", "hallaron", "capturan", "capturaron", "acusan", "acusado",
    "condenan", "condenado", "reportan", "confirman", "anuncian", "presentan",
    "interponen", "piden", "exigen", "niegan", "revelan", "investigan",
    "abren", "cierran", "aprueban", "rechazan", "anuncio", "denuncian",
    "arrestan", "arrestado", "atrapan", "encuentran", "encuentra", "buscan",
    "operativo", "operacion", "nuevo", "nueva", "nuevos", "nuevas", "primer",
    "primera", "primeros", "ultimo", "ultima", "final", "tragico", "grave",
    "gran", "gran", "nacional", "internacional", "local", "fiscalia", "gobierno",
}

# Variantes de edición regional de Google News a probar
EDITION_PARAMS = [
    {"hl": "es-419", "gl": "MX", "ceid": "MX:es-419"},
    {"hl": "es", "gl": "MX", "ceid": "MX:es"},
    {"hl": "es-419", "gl": "US", "ceid": "US:es-419"},
]

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def _normalize(text: str) -> str:
    """Minúsculas y sin acentos, para comparar títulos."""
    text = text.lower()
    text = re.sub(r"[áàäâ]", "a", text)
    text = re.sub(r"[éèëê]", "e", text)
    text = re.sub(r"[íìïî]", "i", text)
    text = re.sub(r"[óòöô]", "o", text)
    text = re.sub(r"[úùüû]", "u", text)
    text = text.replace("ñ", "n")
    return text


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", _normalize(text)))


def _title_similarity(t1: str, t2: str) -> float:
    """Proporción de tokens compartidos entre dos títulos (0.0 a 1.0)."""
    a, b = _tokens(t1), _tokens(t2)
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a), len(b))


def _extract_entities(title: str) -> list:
    """Extrae frases de nombres propios y números de un titular."""
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", title)
    phrases, current = [], []
    last_was_digit = None
    for w in words:
        low = w.lower()
        is_entity = (
            (w[0].isupper() or w.isdigit())
            and low not in STOPWORDS
            and low not in TITLE_VERBS
        )
        if is_entity:
            is_digit = w.isdigit()
            # No mezclar un número con una palabra dentro de la misma frase
            if last_was_digit is not None and is_digit != last_was_digit and current:
                phrases.append(" ".join(current))
                current = []
            current.append(w)
            last_was_digit = is_digit
        else:
            if current:
                phrases.append(" ".join(current))
                current = []
            last_was_digit = None
    if current:
        phrases.append(" ".join(current))
    return [p for p in phrases if len(p) >= 2]


def build_search_queries(title: str) -> list:
    """Consultas candidatas para Google News, de la más precisa a la más general."""
    clean = re.sub(r"['\u2018\u2019\u201c\u201d\"]", "", title).strip()
    queries = []
    if len(clean) >= 10:
        queries.append(clean[:120])
    entities = _extract_entities(title)
    if entities:
        # "Frase compuesta" + entidades simples: p. ej. "Angel Aguirre" Ayotzinapa
        combined = " ".join(
            f'"{p}"' if len(p.split()) > 1 else p for p in entities
        )
        if len(entities) >= 2:
            queries.append(combined)
        primary = entities[0]
        if len(primary) >= 3 and primary != clean:
            queries.append(primary)
    return queries[:3]


def _fetch_rss(query: str) -> list:
    """Consulta Google News RSS; prueba ediciones regionales hasta obtener resultados."""
    q = quote(query)
    for params in EDITION_PARAMS:
        try:
            url = f"https://news.google.com/rss/search?q={q}"
            for k, v in params.items():
                url += f"&{k}={v}"
            resp = requests.get(url, timeout=8, headers={"User-Agent": _UA})
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            items = []
            for item in root.findall(".//item"):
                title = item.findtext("title", "") or ""
                link = item.findtext("link", "") or ""
                pub_date = item.findtext("pubDate", "") or ""
                src_el = item.find("source")
                src = src_el.text if src_el is not None else ""
                if title and link:
                    items.append({
                        "title": title,
                        "url": link,
                        "published": pub_date,
                        "source": src,
                    })
            if items:
                return items
        except Exception:
            continue
    return []


def find_similar_news(title: str, max_results: int = 5,
                      exclude_title: str | None = None,
                      exclude_url: str | None = None,
                      exclude_domain: str | None = None) -> list:
    """Encuentra noticias similares a `title` en Google News RSS.

    Devuelve items {title, url, published, source} sin la noticia original
    y sin duplicados, ordenados por relevancia del feed.
    """
    if not title or len(title.strip()) < 5:
        return []
    exclude_title = exclude_title or title
    exclude_url = exclude_url or ""

    queries = build_search_queries(title)
    seen_titles = set()
    results = []

    for q in queries:
        for it in _fetch_rss(q):
            norm = _normalize(it["title"])
            if norm in seen_titles:
                continue
            # No mostrar la noticia que ya se está analizando
            if _title_similarity(it["title"], exclude_title) > 0.85:
                continue
            if exclude_url and it["url"] == exclude_url:
                continue
            seen_titles.add(norm)
            results.append(it)
            if len(results) >= max_results:
                return results[:max_results]
    return results[:max_results]
