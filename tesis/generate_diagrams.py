import graphviz
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────
# 1. DIAGRAMA DE CLASES (UML 2.x estándar)
# ──────────────────────────────────────────────
def class_diagram():
    g = graphviz.Digraph(
        name="class_diagram",
        format="png",
        engine="dot",
        graph_attr={
            "label": "Diagrama de Clases UML — Backend VERIFEX",
            "labelloc": "t",
            "fontsize": "20",
            "fontname": "Helvetica",
            "bgcolor": "#0d0d14",
            "rankdir": "TB",
            "pad": "0.6",
            "dpi": "150",
            "fontcolor": "#d0d0d0",
            "ranksep": "0.8",
            "nodesep": "0.5",
            "splines": "polyline",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "8",
            "shape": "plain",
            "color": "#2a2a3e",
            "fontcolor": "#c8c8d0",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "7",
            "color": "#555566",
            "fontcolor": "#888899",
            "penwidth": "1.0",
        },
    )

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def make_attrs(items):
        rows = []
        for v, name, t in items:
            rows.append(
                f'<TR><TD ALIGN="LEFT"><FONT COLOR="#c8a040" POINT-SIZE="7">{v}</FONT>'
                f'<FONT COLOR="#c8c8d0" POINT-SIZE="8"> {esc(name)}</FONT>'
                f'<FONT COLOR="#8888aa" POINT-SIZE="7">: {esc(t)}</FONT></TD></TR>'
            )
        return "".join(rows)

    def make_methods(items):
        rows = []
        for v, name, params, ret in items:
            rows.append(
                f'<TR><TD ALIGN="LEFT"><FONT COLOR="#c8a040" POINT-SIZE="7">{v}</FONT>'
                f'<FONT COLOR="#80c0d8" POINT-SIZE="8">{esc(name)}</FONT>'
                f'<FONT COLOR="#bbbbcc" POINT-SIZE="7">({esc(params)})</FONT>'
                f'<FONT COLOR="#8888aa" POINT-SIZE="7">: {esc(ret)}</FONT></TD></TR>'
            )
        return "".join(rows)

    def module_node(name, label, attrs, methods, color="#1a2744"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#e8e8e8" POINT-SIZE="8">&lt;&lt;module&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        if methods:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_methods(methods)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def data_node(name, label, attrs, color="#1e1a2e"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#c8c0e0" POINT-SIZE="8">&lt;&lt;datatype&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    # ─────────────────────────────────────────────────────────────
    # NOTA: El código backend es 100% procedural (funciones sueltas
    # a nivel de módulo). No existen clases. Se modela cada módulo
    # .py como clase <<module>> y cada dict de retorno implícito
    # como <<datatype>> para representación UML.
    # ─────────────────────────────────────────────────────────────

    # ── MÓDULO: app (app.py) ──
    module_node("app_mod", "app (app.py)", [
        ("+", "app", "Flask"),
    ], [
        ("+", "analyze", "", "flask.Response"),
        ("+", "health", "", "flask.Response"),
        ("+", "serve_frontend", "path: str", "flask.Response"),
    ], "#b400ff")

    # ── MÓDULO: analyzer (analyzer.py) ──
    module_node("analyzer_mod", "analyzer (analyzer.py)", [
        ("+", "CREDIBLE_DOMAINS", "Set[str]"),
        ("+", "SOCIAL_MEDIA_DOMAINS", "Set[str]"),
        ("+", "SYSTEM_PROMPT", "str"),
        ("+", "USER_PROMPT_BASE", "str"),
        ("+", "SOCIAL_MEDIA_PROMPT", "str"),
        ("+", "FEW_SHOT_EXAMPLES", "str"),
        ("+", "BROWSER_HEADERS", "Dict[str, str]"),
        ("+", "LOGIN_PATTERNS", "List[str]"),
    ], [
        ("+", "analyze_url", "url: str", "dict"),
        ("+", "scrape_url", "url: str", "dict"),
        ("+", "get_groq_client", "", "Groq | None"),
        ("+", "call_groq", "system_prompt: str, user_prompt: str", "str | None"),
        ("+", "get_domain", "url: str", "str"),
        ("+", "parse_response", "text: str", "dict | None"),
        ("+", "_extract_from_html", "html: str, domain: str = \\\"\\\"", "dict"),
        ("+", "_http_get", "url: str", "tuple"),
        ("-", "_get_platform", "", "str"),
        ("-", "_try_cloudscraper", "url: str", "tuple"),
        ("-", "_try_curl_cffi", "url: str", "tuple"),
        ("-", "_try_requests", "url: str", "tuple"),
        ("-", "_try_playwright", "url: str", "tuple"),
        ("-", "_is_login_blocked_page", "title: str, body: str", "bool"),
        ("-", "_extract_facebook_post_id", "url: str", "str | None"),
        ("-", "_try_facebook_graph_api", "url: str", "dict | None"),
    ], "#00aaff")

    # ── MÓDULO: news_finder (news_finder.py) ──
    module_node("news_finder_mod", "news_finder (news_finder.py)", [], [
        ("+", "find_similar_news", "query: str, max_results: int = 5", "List[dict]"),
    ], "#00f0ff")

    # ──────────────────────────────────────────────
    # ESTRUCTURAS DE DATOS (<<datatype>>)
    # ──────────────────────────────────────────────
    data_node("ScrapeResult", "ScrapeResult", [
        ("+", "content", "str"),
        ("+", "title", "str"),
        ("+", "article_text", "str"),
    ])

    data_node("AnalysisResult", "AnalysisResult", [
        ("+", "verdict", "str"),
        ("+", "confidence_score", "int"),
        ("+", "summary", "str"),
        ("+", "extracted_claims", "List[str]"),
        ("+", "reasoning", "List[str]"),
        ("+", "article_type", "str"),
        ("+", "is_scam", "bool"),
        ("+", "red_flags", "List[str]"),
        ("+", "positive_signals", "List[str]"),
    ])

    data_node("NewsItem", "NewsItem", [
        ("+", "title", "str"),
        ("+", "url", "str"),
        ("+", "published", "str"),
        ("+", "source", "str"),
    ])

    data_node("ApiResponse", "ApiResponse", [
        ("+", "analysis", "AnalysisResult | None"),
        ("+", "similar_news", "List[NewsItem]"),
        ("+", "title", "str"),
        ("+", "article_text", "str"),
        ("+", "domain", "str"),
        ("+", "is_credible_source", "bool"),
        ("+", "error", "str | None"),
    ])

    # ──────────────────────────────────────────────
    # DEPENDENCIAS ENTRE MÓDULOS (<<use>>)
    # ──────────────────────────────────────────────
    dep_style = {"style": "dashed", "arrowhead": "vee", "color": "#555566", "fontcolor": "#888899", "penwidth": "1.0"}

    g.edge("app_mod", "analyzer_mod", label="\u2192 analyze_url()", **dep_style)
    g.edge("app_mod", "news_finder_mod", label="\u2192 find_similar_news()", **dep_style)
    g.edge("analyzer_mod", "news_finder_mod", label="\u2192 find_similar_news()", **dep_style)

    # ──────────────────────────────────────────────
    # DEPENDENCIAS MÓDULO → DATATYPE (<<create>>)
    # ──────────────────────────────────────────────
    prod_style = {"style": "dashed", "arrowhead": "diamond", "color": "#7a6a9a", "fontcolor": "#7a6a9a", "penwidth": "1.0"}
    g.edge("analyzer_mod", "ScrapeResult", label="crea", **prod_style)
    g.edge("analyzer_mod", "AnalysisResult", label="crea", **prod_style)
    g.edge("news_finder_mod", "NewsItem", label="crea", **prod_style)
    g.edge("app_mod", "ApiResponse", label="retorna", **prod_style)

    # ──────────────────────────────────────────────
    # COMPOSICIÓN (ApiResponse contiene AnalysisResult/NewsItem)
    # ──────────────────────────────────────────────
    comp_style = {"color": "#7a6a9a", "fontcolor": "#7a6a9a", "arrowhead": "diamond", "style": "solid", "penwidth": "1.0"}
    g.edge("ApiResponse", "AnalysisResult", label="1", **comp_style)
    g.edge("ApiResponse", "NewsItem", label="0..*", color="#7a6a9a", fontcolor="#7a6a9a",
           arrowhead="none", style="solid", penwidth="1.0")

    g.render(os.path.join(OUT, "diagrams/class_diagram_backend"), cleanup=True)
    print("✅ class_diagram_backend.png")


# ─────────────────────────────────────────────────────────────
# 1b. DIAGRAMA DE CLASES COMPLETO (Backend + Frontend React)
# ─────────────────────────────────────────────────────────────
def full_class_diagram():
    g = graphviz.Digraph(
        name="full_class_diagram",
        format="png",
        engine="dot",
        graph_attr={
            "label": "Diagrama de Clases UML Completo — VERIFEX",
            "labelloc": "t",
            "fontsize": "20",
            "fontname": "Helvetica",
            "bgcolor": "#0d0d14",
            "rankdir": "TB",
            "pad": "0.6",
            "dpi": "150",
            "fontcolor": "#d0d0d0",
            "ranksep": "0.8",
            "nodesep": "0.4",
            "splines": "polyline",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "8",
            "shape": "plain",
            "color": "#2a2a3e",
            "fontcolor": "#c8c8d0",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "7",
            "color": "#555566",
            "fontcolor": "#888899",
            "penwidth": "1.0",
        },
    )

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def make_attrs(items):
        rows = []
        for v, name, t in items:
            rows.append(
                f'<TR><TD ALIGN="LEFT"><FONT COLOR="#c8a040" POINT-SIZE="7">{v}</FONT>'
                f'<FONT COLOR="#c8c8d0" POINT-SIZE="8"> {esc(name)}</FONT>'
                f'<FONT COLOR="#8888aa" POINT-SIZE="7">: {esc(t)}</FONT></TD></TR>'
            )
        return "".join(rows)

    def make_methods(items):
        rows = []
        for v, name, params, ret in items:
            rows.append(
                f'<TR><TD ALIGN="LEFT"><FONT COLOR="#c8a040" POINT-SIZE="7">{v}</FONT>'
                f'<FONT COLOR="#80c0d8" POINT-SIZE="8">{esc(name)}</FONT>'
                f'<FONT COLOR="#bbbbcc" POINT-SIZE="7">({esc(params)})</FONT>'
                f'<FONT COLOR="#8888aa" POINT-SIZE="7">: {esc(ret)}</FONT></TD></TR>'
            )
        return "".join(rows)

    def module_node(name, label, attrs, methods, color="#1a2744"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#e8e8e8" POINT-SIZE="8">&lt;&lt;module&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        if methods:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_methods(methods)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def data_node(name, label, attrs, color="#1e1a2e"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#c8c0e0" POINT-SIZE="8">&lt;&lt;datatype&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def react_node(name, label, attrs, methods, color="#1a3a2e"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#b0d8c0" POINT-SIZE="8">&lt;&lt;React.Component&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        if methods:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_methods(methods)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    # ──────────────────────────────────────────────
    # BACKEND — Módulos Python
    # ──────────────────────────────────────────────
    module_node("app_mod", "app (app.py)", [
        ("+", "app", "Flask"),
    ], [
        ("+", "analyze", "", "flask.Response"),
        ("+", "health", "", "flask.Response"),
        ("+", "serve_frontend", "path: str", "flask.Response"),
    ], "#1a2744")

    module_node("analyzer_mod", "analyzer (analyzer.py)", [
        ("+", "CREDIBLE_DOMAINS", "Set[str]"),
        ("+", "SOCIAL_MEDIA_DOMAINS", "Set[str]"),
        ("+", "SYSTEM_PROMPT", "str"),
        ("+", "USER_PROMPT_BASE", "str"),
        ("+", "SOCIAL_MEDIA_PROMPT", "str"),
        ("+", "FEW_SHOT_EXAMPLES", "str"),
        ("+", "BROWSER_HEADERS", "Dict[str, str]"),
        ("+", "LOGIN_PATTERNS", "List[str]"),
    ], [
        ("+", "analyze_url", "url: str", "dict"),
        ("+", "scrape_url", "url: str", "dict"),
        ("+", "get_groq_client", "", "Groq | None"),
        ("+", "call_groq", "system_prompt: str, user_prompt: str", "str | None"),
        ("+", "get_domain", "url: str", "str"),
        ("+", "parse_response", "text: str", "dict | None"),
        ("+", "_extract_from_html", "html: str, domain: str", "dict"),
        ("+", "_http_get", "url: str", "tuple"),
        ("-", "_get_platform", "", "str"),
        ("-", "_try_cloudscraper", "url: str", "tuple"),
        ("-", "_try_curl_cffi", "url: str", "tuple"),
        ("-", "_try_requests", "url: str", "tuple"),
        ("-", "_try_playwright", "url: str", "tuple"),
        ("-", "_is_login_blocked_page", "title: str, body: str", "bool"),
        ("-", "_extract_facebook_post_id", "url: str", "str | None"),
        ("-", "_try_facebook_graph_api", "url: str", "dict | None"),
    ], "#1a2d26")

    module_node("news_finder_mod", "news_finder (news_finder.py)", [], [
        ("+", "find_similar_news", "query: str, max_results: int = 5", "List[dict]"),
    ], "#2d1a26")

    # ──────────────────────────────────────────────
    # ESTRUCTURAS DE DATOS
    # ──────────────────────────────────────────────
    data_node("ScrapeResult", "ScrapeResult", [
        ("+", "content", "str"),
        ("+", "title", "str"),
        ("+", "article_text", "str"),
    ])

    data_node("AnalysisResult", "AnalysisResult", [
        ("+", "verdict", "str"),
        ("+", "confidence_score", "int"),
        ("+", "summary", "str"),
        ("+", "extracted_claims", "List[str]"),
        ("+", "reasoning", "List[str]"),
        ("+", "article_type", "str"),
        ("+", "is_scam", "bool"),
        ("+", "red_flags", "List[str]"),
        ("+", "positive_signals", "List[str]"),
    ])

    data_node("NewsItem", "NewsItem", [
        ("+", "title", "str"),
        ("+", "url", "str"),
        ("+", "published", "str"),
        ("+", "source", "str"),
    ])

    data_node("ApiResponse", "ApiResponse", [
        ("+", "analysis", "AnalysisResult | None"),
        ("+", "similar_news", "List[NewsItem]"),
        ("+", "title", "str"),
        ("+", "article_text", "str"),
        ("+", "domain", "str"),
        ("+", "is_credible_source", "bool"),
        ("+", "error", "str | None"),
    ])

    # ──────────────────────────────────────────────
    # FRONTEND — Componentes React (TypeScript)
    # ──────────────────────────────────────────────
    react_node("App", "App (App.tsx)", [
        ("-", "lang", "'es' | 'en'"),
        ("-", "loading", "boolean"),
        ("-", "result", "ApiResponse | null"),
        ("-", "error", "string | null"),
    ], [
        ("+", "handleAnalyze", "url: string", "Promise<void>"),
        ("+", "handleToggleLang", "", "void"),
        ("+", "handleClear", "", "void"),
        ("#", "adjustedVerdict", "", "string | null"),
    ])

    react_node("UrlInput", "UrlInput (UrlInput.tsx)", [
        ("+", "lang", "'es' | 'en'"),
        ("+", "loading", "boolean"),
        ("+", "onAnalyze", "(url: string) => void"),
        ("+", "onClear?", "() => void"),
        ("-", "url", "string"),
    ], [
        ("+", "handleSubmit", "e: React.FormEvent", "void"),
        ("+", "handleChange", "e: ChangeEvent", "void"),
    ])

    react_node("VerdictDisplay", "VerdictDisplay (VerdictDisplay.tsx)", [
        ("+", "verdict", "string"),
        ("+", "originalVerdict?", "string"),
        ("+", "lang", "'es' | 'en'"),
    ], [])

    react_node("ConfidenceBar", "ConfidenceBar (ConfidenceBar.tsx)", [
        ("+", "score", "number"),
        ("+", "lang", "'es' | 'en'"),
    ], [])

    react_node("RedFlags", "RedFlags (RedFlags.tsx)", [
        ("+", "redFlags", "string[]"),
        ("+", "positiveSignals", "string[]"),
        ("+", "lang", "'es' | 'en'"),
    ], [])

    react_node("SimilarNews", "SimilarNews (SimilarNews.tsx)", [
        ("+", "news", "NewsItem[]"),
        ("+", "lang", "'es' | 'en'"),
    ], [])

    react_node("LangToggle", "LanguageToggle (LanguageToggle.tsx)", [
        ("+", "lang", "'es' | 'en'"),
        ("+", "onToggle", "() => void"),
    ], [])

    # ──────────────────────────────────────────────
    # RELACIONES ENTRE BACKEND
    # ──────────────────────────────────────────────
    dep_style = {"style": "dashed", "arrowhead": "vee", "color": "#555566", "fontcolor": "#888899", "penwidth": "1.0"}
    g.edge("app_mod", "analyzer_mod", label="\u2192 analyze_url()", **dep_style)
    g.edge("app_mod", "news_finder_mod", label="\u2192 find_similar_news()", **dep_style)
    g.edge("analyzer_mod", "news_finder_mod", label="\u2192 find_similar_news()", **dep_style)

    prod_style = {"style": "dashed", "arrowhead": "diamond", "color": "#7a6a9a", "fontcolor": "#7a6a9a", "penwidth": "1.0"}
    g.edge("analyzer_mod", "ScrapeResult", label="crea", **prod_style)
    g.edge("analyzer_mod", "AnalysisResult", label="crea", **prod_style)
    g.edge("news_finder_mod", "NewsItem", label="crea", **prod_style)
    g.edge("app_mod", "ApiResponse", label="retorna", **prod_style)

    comp_style = {"color": "#7a6a9a", "fontcolor": "#7a6a9a", "arrowhead": "diamond", "style": "solid", "penwidth": "1.0"}
    g.edge("ApiResponse", "AnalysisResult", label="1", **comp_style)
    g.edge("ApiResponse", "NewsItem", label="0..*", color="#7a6a9a", fontcolor="#7a6a9a",
           arrowhead="none", style="solid", penwidth="1.0")

    # ──────────────────────────────────────────────
    # RELACIONES ENTRE FRONTEND
    # ──────────────────────────────────────────────
    fe_dep = {"color": "#4a6a5a", "fontcolor": "#4a6a5a", "style": "dashed", "arrowhead": "vee", "penwidth": "1.0"}
    fe_comp = {"color": "#4a6a5a", "fontcolor": "#4a6a5a", "arrowhead": "diamond", "style": "solid", "penwidth": "1.0"}

    g.edge("App", "ApiResponse", label="usa", **fe_dep)
    g.edge("App", "UrlInput", label="compone", **fe_comp)
    g.edge("App", "VerdictDisplay", label="compone", **fe_comp)
    g.edge("App", "ConfidenceBar", label="compone", **fe_comp)
    g.edge("App", "RedFlags", label="compone", **fe_comp)
    g.edge("App", "SimilarNews", label="compone 0..1", color="#4a6a5a", fontcolor="#4a6a5a",
           arrowhead="diamond", style="dashed", penwidth="1.0")
    g.edge("App", "LangToggle", label="compone", **fe_comp)

    g.edge("app_mod", "ApiResponse", label="retorna JSON \u2192", **fe_dep)
    g.edge("app_mod", "App", label="sirve SPA \u2192", **{"color": "#555566", "fontcolor": "#888899",
          "style": "dashed", "arrowhead": "vee", "penwidth": "1.0"})

    g.render(os.path.join(OUT, "diagrams/class_diagram_full"), cleanup=True)
    print("✅ class_diagram_full.png")


# ──────────────────────────────────────────────
# 2. DIAGRAMA DE FRONTEND
# ──────────────────────────────────────────────
def frontend_diagram():
    g = graphviz.Digraph(
        name="frontend_diagram",
        format="png",
        engine="dot",
        graph_attr={
            "label": "Diagrama de Frontend - VERIFEX",
            "labelloc": "t",
            "fontsize": "24",
            "fontname": "Helvetica",
            "bgcolor": "#0a0a1a",
            "rankdir": "TB",
            "pad": "0.5",
            "dpi": "150",
            "fontcolor": "white",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "10",
            "shape": "plain",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "9",
        },
    )

    def comp_node(name, label, details, color="#00f0ff"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="black" POINT-SIZE="11"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#cccccc" POINT-SIZE="9">{details}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="#0d0d24" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def module_node(name, label, details, color="#ffaa00"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="black" POINT-SIZE="11"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#cccccc" POINT-SIZE="9">{details}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="#0d0d24" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    # App principal
    comp_node("App", "App.tsx", "idioma: es|en\ncargando: bool\nresultado: RespuestaAPI\nmanejarAnalizar(url)\nmanejarCambiarIdioma()\nmanejarLimpiar()", "#00f0ff")

    # Componentes
    comp_node("UrlInput", "UrlInput", "props: idioma, cargando\nonAnalyze, onClear\nAnimación de carga\n(10 segmentos)", "#00cc88")
    comp_node("VerdictDisplay", "VerdictDisplay", "props: veredicto,\nveredictoOriginal, idioma\nColores: REAL=cian,\nFALSO=rojo, SATIRA=naranja,\nESTAFA=morado,\nDUDOSO=naranja", "#00cc88")
    comp_node("ConfidenceBar", "ConfidenceBar", "props: puntuacion, idioma\nBarra de 20 segmentos\nRojo/Verde/Cian/Naranja", "#00cc88")
    comp_node("RedFlags", "RedFlags", "props: banderasRojas,\nsenalesPositivas, idioma\nBanderas rojas + señales\npositivas (etiquetas)", "#00cc88")
    comp_node("SimilarNews", "SimilarNews", "props: noticias[], idioma\nCuadrícula de tarjetas\nTítulo, fuente, fecha\n(carga diferida)", "#00cc88")
    comp_node("LanguageToggle", "LanguageToggle", "props: idioma, onToggle\nBotón ES/EN", "#00cc88")

    # Módulos auxiliares
    module_node("Styles", "index.css", "Tema cyberpunk\nViñeta CRT, líneas de barrido\nCuadrícula animada\nTailwind CSS", "#ffaa00")
    module_node("Entry", "main.tsx", "React.StrictMode\nRenderiza App", "#ffaa00")
    module_node("Config", "vite.config.ts", "Proxy /analyze → :5001\nVitest + jsdom", "#ffaa00")

    # Conexiones
    g.edge("Entry", "App", color="#ffaa00", fontcolor="#ffaa00")
    g.edge("App", "UrlInput", color="#00cc88", fontcolor="#00cc88")
    g.edge("App", "VerdictDisplay", color="#00cc88", fontcolor="#00cc88")
    g.edge("App", "ConfidenceBar", color="#00cc88", fontcolor="#00cc88")
    g.edge("App", "RedFlags", color="#00cc88", fontcolor="#00cc88")
    g.edge("App", "SimilarNews", color="#00cc88", fontcolor="#00cc88")
    g.edge("App", "LanguageToggle", color="#00cc88", fontcolor="#00cc88")
    g.edge("App", "Styles", color="#ffaa00", fontcolor="#ffaa00", style="dashed", label="importa")
    g.edge("App", "Config", color="#ffaa00", fontcolor="#ffaa00", style="dashed", label="usa")

    g.render(os.path.join(OUT, "diagrams/frontend_diagram"), cleanup=True)
    print("✅ frontend_diagram.png")


# ──────────────────────────────────────────────
# 3. DIAGRAMA DE BACKEND
# ──────────────────────────────────────────────
def backend_diagram():
    g = graphviz.Digraph(
        name="backend_diagram",
        format="png",
        engine="dot",
        graph_attr={
            "label": "Diagrama de Backend - VERIFEX",
            "labelloc": "t",
            "fontsize": "24",
            "fontname": "Helvetica",
            "bgcolor": "#0a0a1a",
            "rankdir": "TB",
            "pad": "0.5",
            "dpi": "150",
            "fontcolor": "white",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "10",
            "shape": "plain",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "9",
        },
    )

    def layer_node(name, label, details, color="#b400ff"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="white" POINT-SIZE="11"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#cccccc" POINT-SIZE="9">{details}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="#0d0d24" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def process_node(name, label, details, color="#00f0ff"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="black" POINT-SIZE="11"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#cccccc" POINT-SIZE="9">{details}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="#0d0d24" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def external_node(name, label, details, color="#ff003c"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="white" POINT-SIZE="11"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#cccccc" POINT-SIZE="9">{details}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="#0d0d24" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    # Entidades externas
    external_node("Browser", "Navegador Web", "SPA en React\nPOST /analyze\nGET /health", "#ff003c")
    external_node("GroqAPI", "Groq API (LLM)", "llama-3.3-70b\nllama-3.1-8b\nRespuesta JSON", "#ff003c")
    external_node("GoogleNews", "Google News RSS", "Búsqueda de\nnoticias similares\nFormato XML", "#ff003c")
    external_node("TargetSite", "Sitio Web a Analizar", "URL ingresada\npor el usuario", "#ff003c")

    # Capa Flask
    layer_node("Flask", "Servidor Flask (app.py)", "gunicorn, 2 workers\nPuerto $PORT\nCORS habilitado", "#b400ff")

    # Procesos
    process_node("AnalyzeURL", "analyze_url()",
                 "1. Validar API key\n2. Scrapear URL\n3. Extraer contenido\n4. Buscar similares\n5. Construir prompt\n6. Llamar a Groq\n7. Parsear respuesta\n8. Override por dominio\n9. Retornar JSON", "#00f0ff")
    process_node("ScrapePipeline", "Pipeline de Scraping",
                 "4 estrategias en secuencia:\n1. cloudscraper (4 perfiles)\n2. curl_cffi (4 versiones)\n3. requests (2 intentos)\n4. Playwright (Firefox)", "#00f0ff")
    process_node("Extraction", "Extracción HTML",
                 "BeautifulSoup lxml\nEliminar: script, style,\nnav, footer, header…\nExtraer: title, meta,\narticle p, body p", "#00f0ff")
    process_node("NewsFinder", "Buscador de Noticias",
                 "find_similar_news()\nGoogle News RSS\nhasta 5 resultados", "#00f0ff")

    # Flujo de datos
    g.edge("Browser", "Flask", label="HTTP POST/GET", color="#ff003c", fontcolor="#ff003c")
    g.edge("Flask", "AnalyzeURL", label="enrutar", color="#b400ff", fontcolor="#b400ff")
    g.edge("AnalyzeURL", "ScrapePipeline", label="scrape_url()", color="#00f0ff", fontcolor="#00f0ff")
    g.edge("ScrapePipeline", "TargetSite", label="GET", color="#00f0ff", fontcolor="#00f0ff")
    g.edge("TargetSite", "Extraction", label="HTML", color="#ff003c", fontcolor="#ff003c")
    g.edge("Extraction", "AnalyzeURL", label="texto extraído", color="#00f0ff", fontcolor="#00f0ff")
    g.edge("AnalyzeURL", "NewsFinder", label="find_similar_news()", color="#00f0ff", fontcolor="#00f0ff")
    g.edge("NewsFinder", "GoogleNews", label="consulta RSS", color="#00f0ff", fontcolor="#00f0ff")
    g.edge("GoogleNews", "AnalyzeURL", label="resultados", color="#ff003c", fontcolor="#ff003c")
    g.edge("AnalyzeURL", "GroqAPI", label="prompt JSON", color="#00f0ff", fontcolor="#00f0ff")
    g.edge("GroqAPI", "AnalyzeURL", label="veredicto JSON", color="#ff003c", fontcolor="#ff003c")
    g.edge("AnalyzeURL", "Flask", label="respuesta JSON", color="#00f0ff", fontcolor="#00f0ff")

    g.render(os.path.join(OUT, "diagrams/backend_diagram"), cleanup=True)
    print("✅ backend_diagram.png")


# ──────────────────────────────────────────────
# 4. DIAGRAMA DE ARQUITECTURA DE INFORMACIÓN
# ──────────────────────────────────────────────
def info_arch_diagram():
    g = graphviz.Digraph(
        name="info_arch_diagram",
        format="png",
        engine="dot",
        graph_attr={
            "label": "Arquitectura de Información - VERIFEX",
            "labelloc": "t",
            "fontsize": "24",
            "fontname": "Helvetica",
            "bgcolor": "#0a0a1a",
            "rankdir": "TB",
            "pad": "0.5",
            "dpi": "150",
            "fontcolor": "white",
            "splines": "true",
            "ranksep": "0.8",
            "nodesep": "0.5",
            "newrank": "true",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "10",
            "shape": "plain",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "9",
            "color": "#7a7a8a",
            "fontcolor": "#bbbbcc",
            "penwidth": "1.6",
        },
    )

    def arch_node(name, label, details, color="#00f0ff", border="#00f0ff"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="black" POINT-SIZE="11"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#cccccc" POINT-SIZE="9">{details}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" BGCOLOR="#0d0d24" COLOR="{border}" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def data_node(name, label, fields, color="#b400ff"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="white" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
            f'<TR><TD BGCOLOR="#111122" COLSPAN="2"><FONT COLOR="#aaaacc" POINT-SIZE="8">{fields}</FONT></TD></TR>',
        ]
        g.node(name, f'<<TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="#0d0d24" COLOR="{color}" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    # === CAPA DE PRESENTACIÓN (Frontend) ===
    with g.subgraph(name="cluster_frontend") as sub:
        sub.attr(
            label="CAPA DE PRESENTACIÓN",
            style="dashed",
            color="#00cc88",
            fontcolor="#00cc88",
            fontsize="14",
            labeljust="l",
        )
        arch_node("UI_Input", "Input de URL", "UrlInput.tsx\nCampo de texto + botón\nAnalizar / Limpiar", "#00cc88", "#00cc88")
        arch_node("UI_Result", "Visualización de Resultado", "VerdictDisplay  ConfidenceBar\nRedFlags  SimilarNews  LangToggle", "#00cc88", "#00cc88")
        data_node("Dato_RespuestaAPI", "RespuestaAPI\n(desde backend)", "analysis: Analysis\ndomain: str  url_analyzed: str\nis_credible_source: bool\nsimilar_news: list\narticle_text: str\nerror: str | None", "#b400ff")

    # === CAPA DE NEGOCIO (Backend Flask) ===
    with g.subgraph(name="cluster_backend") as sub:
        sub.attr(
            label="CAPA DE NEGOCIO",
            style="dashed",
            color="#00f0ff",
            fontcolor="#00f0ff",
            fontsize="14",
            labeljust="l",
        )
        arch_node("FlaskAPI", "API REST (app.py)", "POST /analyze\nGET /health\nCORS habilitado", "#00f0ff", "#00f0ff")
        arch_node("AnalyzeURL", "analyze_url()", "1. Recibir URL\n2. scrape_url()\n3. find_similar_news()\n4. Construir prompt\n5. Llamar Groq API\n6. Parsear respuesta\n7. Override dominios\n8. Retornar JSON", "#00aaff", "#00aaff")
        arch_node("NewsFinder", "Buscador de Noticias", "news_finder.py\nfind_similar_news()\nGoogle News RSS\nHasta 5 resultados", "#00aaff", "#00aaff")

    # === CAPA DE DATOS (Scraping + Extracción) ===
    with g.subgraph(name="cluster_data") as sub:
        sub.attr(
            label="CAPA DE DATOS",
            style="dashed",
            color="#ffaa00",
            fontcolor="#ffaa00",
            fontsize="14",
            labeljust="l",
        )
        arch_node("ScraperPipeline", "Pipeline de Scraping", "4 estrategias:\n1. cloudscraper\n2. curl_cffi\n3. requests\n4. Playwright (Firefox)\nRetorna HTML crudo", "#ff8800", "#ff8800")
        arch_node("HTMLExtractor", "Extractor de Contenido", "_extract_from_html()\nBeautifulSoup + lxml\nLimpia: script, style, nav\nExtrae: title, meta, P\nCasos: Instagram og:desc\n       Threads JSON embebido", "#ff8800", "#ff8800")
        data_node("Dato_Extraido", "Datos Extraídos", "title: str\nmeta_desc: str\nbody: str (hasta 5000)\narticle_text: str\n(truncado a 2000)", "#b400ff")

    # === CAPA EXTERNA ===
    with g.subgraph(name="cluster_external") as sub:
        sub.attr(
            label="SERVICIOS EXTERNOS",
            style="dashed",
            color="#ff003c",
            fontcolor="#ff003c",
            fontsize="14",
            labeljust="l",
        )
        arch_node("TargetSite", "Sitio Web Objetivo", "URL a analizar\nPeriódico, blog,\nred social, etc.\nProvee HTML estático", "#ff003c", "#ff003c")
        arch_node("GroqAPI", "Groq LLM API", "llama-3.3-70b\nllama-3.1-8b (fallback)\nEntrada: prompt sistema\n  + prompt usuario\nSalida: JSON veredicto,\n  confianza, red_flags", "#ff003c", "#ff003c")
        arch_node("GoogleNews", "Google News RSS", "Búsqueda por título\nHasta 4 resultados\nFormato XML\nContexto para la IA", "#ff003c", "#ff003c")

    # === FLUJO DE DATOS (numerado) ===
    g.edge("UI_Input", "FlaskAPI", label="1")
    g.edge("FlaskAPI", "ScraperPipeline", label="2")
    g.edge("ScraperPipeline", "TargetSite", label="3")
    g.edge("TargetSite", "HTMLExtractor", label="4", arrowhead="diamond")
    g.edge("HTMLExtractor", "Dato_Extraido", label="5", arrowhead="diamond")
    g.edge("Dato_Extraido", "AnalyzeURL", label="6")
    g.edge("AnalyzeURL", "NewsFinder", label="7")
    g.edge("NewsFinder", "GoogleNews", label="8")
    g.edge("GoogleNews", "AnalyzeURL", label="9")
    g.edge("AnalyzeURL", "GroqAPI", label="10")
    g.edge("GroqAPI", "AnalyzeURL", label="11")
    g.edge("AnalyzeURL", "FlaskAPI", label="12")
    g.edge("FlaskAPI", "Dato_RespuestaAPI", label="13", arrowhead="diamond")
    g.edge("Dato_RespuestaAPI", "UI_Result", label="14")

    g.render(os.path.join(OUT, "diagrams/info_arch_diagram"), cleanup=True)
    print("✅ info_arch_diagram.png")


# ─────────────────────────────────────────────────────────────
# 5. DIAGRAMA DE CLASES DEL FRONTEND (UML formal, solo frontend)
# ─────────────────────────────────────────────────────────────
def frontend_class_diagram():
    g = graphviz.Digraph(
        name="frontend_class_diagram",
        format="png",
        engine="dot",
        graph_attr={
            "label": "Diagrama de Clases UML — Frontend VERIFEX",
            "labelloc": "t",
            "fontsize": "20",
            "fontname": "Helvetica",
            "bgcolor": "#0d0d14",
            "rankdir": "TB",
            "pad": "0.6",
            "dpi": "150",
            "fontcolor": "#d0d0d0",
            "ranksep": "0.8",
            "nodesep": "0.5",
            "splines": "polyline",
        },
        node_attr={
            "fontname": "Helvetica",
            "fontsize": "8",
            "shape": "plain",
            "color": "#2a2a3e",
            "fontcolor": "#c8c8d0",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "7",
            "color": "#555566",
            "fontcolor": "#888899",
            "penwidth": "1.0",
        },
    )

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def make_attrs(items):
        rows = []
        for v, name, t in items:
            rows.append(
                f'<TR><TD ALIGN="LEFT"><FONT COLOR="#c8a040" POINT-SIZE="7">{v}</FONT>'
                f'<FONT COLOR="#c8c8d0" POINT-SIZE="8"> {esc(name)}</FONT>'
                f'<FONT COLOR="#8888aa" POINT-SIZE="7">: {esc(t)}</FONT></TD></TR>'
            )
        return "".join(rows)

    def make_methods(items):
        rows = []
        for v, name, params, ret in items:
            rows.append(
                f'<TR><TD ALIGN="LEFT"><FONT COLOR="#c8a040" POINT-SIZE="7">{v}</FONT>'
                f'<FONT COLOR="#80c0d8" POINT-SIZE="8">{esc(name)}</FONT>'
                f'<FONT COLOR="#bbbbcc" POINT-SIZE="7">({esc(params)})</FONT>'
                f'<FONT COLOR="#8888aa" POINT-SIZE="7">: {esc(ret)}</FONT></TD></TR>'
            )
        return "".join(rows)

    def react_node(name, label, attrs, methods, color="#1a3a2e"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#b0d8c0" POINT-SIZE="8">&lt;&lt;React.Component&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        if methods:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_methods(methods)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def data_node(name, label, attrs, color="#1e1a2e"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#c8c0e0" POINT-SIZE="8">&lt;&lt;interface&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if attrs:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_attrs(attrs)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    def util_node(name, label, methods, color="#1a2744"):
        rows = [
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#a0c0e0" POINT-SIZE="8">&lt;&lt;module&gt;&gt;</FONT></TD></TR>',
            f'<TR><TD BGCOLOR="{color}" COLSPAN="2"><FONT COLOR="#ffffff" POINT-SIZE="10"><B>{label}</B></FONT></TD></TR>',
        ]
        if methods:
            rows.append(f'<TR><TD BGCOLOR="#0d0d14" COLSPAN="2"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">{make_methods(methods)}</TABLE></TD></TR>')
        g.node(name, f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="#0d0d14" COLOR="#2a2a3e" STYLE="ROUNDED">{ "".join(rows) }</TABLE>>')

    # ──────────────────────────────────────────────
    # INTERFACES / TYPES
    # ──────────────────────────────────────────────
    data_node("Lang", "Lang (type)", [
        ("+", "value", "'es' | 'en'"),
    ])

    data_node("Analysis", "Analysis", [
        ("+", "verdict", "string"),
        ("+", "confidence_score", "number"),
        ("+", "summary", "string"),
        ("+", "extracted_claims?", "string[]"),
        ("+", "reasoning", "string[]"),
        ("+", "red_flags", "string[]"),
        ("+", "positive_signals", "string[]"),
        ("+", "article_type?", "string"),
        ("+", "is_scam?", "boolean"),
    ])

    data_node("NewsItem", "NewsItem", [
        ("+", "title", "string"),
        ("+", "url", "string"),
        ("+", "published", "string"),
        ("+", "source", "string"),
    ])

    data_node("ApiResponse", "ApiResponse", [
        ("+", "analysis", "Analysis | null"),
        ("+", "similar_news", "NewsItem[]"),
        ("+", "url_analyzed", "string"),
        ("+", "article_text", "string"),
        ("+", "domain", "string"),
        ("+", "is_credible_source", "boolean"),
        ("+", "error", "string | null"),
    ])

    # ──────────────────────────────────────────────
    # REACT COMPONENTS
    # ──────────────────────────────────────────────
    react_node("App", "App (App.tsx)", [
        ("-", "lang", "'es' | 'en'"),
        ("-", "loading", "boolean"),
        ("-", "result", "ApiResponse | null"),
        ("-", "error", "string | null"),
    ], [
        ("+", "handleToggleLang", "", "void"),
        ("+", "handleClear", "", "void"),
        ("+", "handleAnalyze", "url: string", "Promise<void>"),
        ("#", "adjustedVerdict", "", "string | null"),
    ])

    react_node("UrlInput", "UrlInput (UrlInput.tsx)", [
        ("+", "lang", "'es' | 'en'"),
        ("+", "loading", "boolean"),
        ("+", "onAnalyze", "(url: string) => void"),
        ("+", "onClear?", "() => void"),
        ("-", "url", "string"),
    ], [
        ("+", "handleChange", "e: React.ChangeEvent", "void"),
        ("+", "handleClear", "", "void"),
        ("+", "handleSubmit", "e: React.FormEvent", "void"),
    ])

    react_node("LoadingSegments", "LoadingSegments (inner)", [], [])

    react_node("VerdictDisplay", "VerdictDisplay (VerdictDisplay.tsx)", [
        ("+", "verdict", "string"),
        ("+", "originalVerdict?", "string"),
        ("+", "lang", "'es' | 'en'"),
    ], [
        ("#", "containerStyle", "", "CSSProperties"),
        ("#", "wordStyle", "", "CSSProperties"),
    ])

    react_node("ConfidenceBar", "ConfidenceBar (ConfidenceBar.tsx)", [
        ("+", "score", "number"),
        ("+", "lang", "'es' | 'en'"),
    ], [
        ("#", "scoreStyle", "", "CSSProperties"),
    ])

    react_node("RedFlags", "RedFlags (RedFlags.tsx)", [
        ("+", "redFlags", "string[]"),
        ("+", "positiveSignals", "string[]"),
        ("+", "lang", "'es' | 'en'"),
    ], [])

    react_node("SimilarNews", "SimilarNews (SimilarNews.tsx)", [
        ("+", "news", "NewsItem[]"),
        ("+", "lang", "'es' | 'en'"),
    ], [])

    react_node("LanguageToggle", "LanguageToggle (LanguageToggle.tsx)", [
        ("+", "lang", "'es' | 'en'"),
        ("+", "onToggle", "() => void"),
    ], [])

    # ──────────────────────────────────────────────
    # UTILITY FUNCTIONS
    # ──────────────────────────────────────────────
    util_node("Utils", "Utilities", [
        ("+", "getColorKey", "score: number", "string"),
        ("+", "formatDate", "raw: string", "string"),
    ])

    # ──────────────────────────────────────────────
    # RELATIONSHIPS (Componentes → hijos)
    # ──────────────────────────────────────────────
    comp_style = {"color": "#4a6a5a", "fontcolor": "#4a6a5a", "arrowhead": "diamond", "style": "solid", "penwidth": "1.2"}
    lazy_style = {"color": "#4a6a5a", "fontcolor": "#4a6a5a", "arrowhead": "diamond", "style": "dashed", "penwidth": "1.0"}
    dep_style = {"style": "dashed", "arrowhead": "vee", "color": "#555566", "fontcolor": "#888899", "penwidth": "1.0"}
    prod_style = {"style": "dashed", "arrowhead": "diamond", "color": "#7a6a9a", "fontcolor": "#7a6a9a", "penwidth": "1.0"}

    # Composición: App → hijos
    g.edge("App", "UrlInput", label="compone", **comp_style)
    g.edge("App", "LanguageToggle", label="compone", **comp_style)
    g.edge("App", "VerdictDisplay", label="compone", **comp_style)
    g.edge("App", "ConfidenceBar", label="compone", **comp_style)
    g.edge("App", "RedFlags", label="compone", **comp_style)
    g.edge("App", "SimilarNews", label="compone (lazy)", **lazy_style)

    # Composición: UrlInput → LoadingSegments
    g.edge("UrlInput", "LoadingSegments", label="compone (cond.)", **comp_style)

    # Dependencia: App consume ApiResponse
    g.edge("App", "ApiResponse", label="usa (fetch)", **dep_style)

    # Composición: ApiResponse contiene Analysis + NewsItem[]
    g.edge("ApiResponse", "Analysis", label="1", color="#7a6a9a", fontcolor="#7a6a9a",
           arrowhead="diamond", style="solid", penwidth="1.0")
    g.edge("ApiResponse", "NewsItem", label="0..*", color="#7a6a9a", fontcolor="#7a6a9a",
           arrowhead="none", style="solid", penwidth="1.0")

    # Dependencias: componentes → tipos
    g.edge("SimilarNews", "NewsItem", label="usa", **dep_style)

    # Dependencias: componentes → utilidades
    g.edge("ConfidenceBar", "Utils", label="getColorKey()", **dep_style)
    g.edge("SimilarNews", "Utils", label="formatDate()", **dep_style)
    g.edge("VerdictDisplay", "Utils", label="VERDICT_CONFIG", **dep_style)

    g.render(os.path.join(OUT, "diagrams/frontend_class_diagram"), cleanup=True)
    print("✅ frontend_class_diagram.png")


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "diagrams"), exist_ok=True)
    class_diagram()
    full_class_diagram()
    frontend_diagram()
    frontend_class_diagram()
    backend_diagram()
    info_arch_diagram()
    print("\n✅ Todos los diagramas generados en diagrams/")
