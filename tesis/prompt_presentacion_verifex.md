# Prompt para generar presentación de VERIFEX

Eres un asistente especializado en crear presentaciones académicas profesionales. Genera una presentación con diapositivas sobre el siguiente proyecto de tesis titulado **"VERIFEX: Sistema Web para el Análisis Automatizado de la Credibilidad de Noticias en Línea"**. Sigue EXACTAMENTE la estructura y el contenido que se detalla a continuación. NO inventes datos, cifras, tecnologías, funcionalidades ni conclusiones que no estén explícitamente mencionados. NO agregues información de otros proyectos similares. NO uses contenido genérico sobre desinformación. Todo lo que incluyas debe estar basado única y exclusivamente en lo que aquí se describe.

---

## Estructura de la presentación (15-20 diapositivas)

### Diapositiva 1 — Portada
- Título: **VERIFEX: Sistema Web para el Análisis Automatizado de la Credibilidad de Noticias en Línea**
- Subtítulo: Tesis profesional — Ingeniería en Sistemas Computacionales
- Autores: Marco Antonio Delgado Serrano, Luis Gustavo García Altamirano, Ulises Santos Canchola
- Fecha: Agosto 2026

### Diapositiva 2 — Problemática
- La desinformación y noticias falsas son un desafío global en la sociedad digital contemporánea
- En México, ~70% de la población tiene acceso a internet y la mayoría consume noticias por redes sociales
- Las noticias falsas se difunden hasta 6 veces más rápido que las verdaderas
- Las herramientas de fact-checking existentes (Verificado, Animal Político, Snopes, Google Fact Check) tienen limitaciones: requieren suscripciones de pago, están orientadas a periodistas profesionales, no funcionan de manera local, o dependen de APIs de pago
- No existe una herramienta gratuita, accesible para el público general y con soporte bilingüe (español/inglés)

### Diapositiva 3 — Objetivo General
Desarrollar un analizador de credibilidad de noticias utilizando inteligencia artificial (Groq API con modelo Llama 3.3-70B) que permita a los usuarios verificar la veracidad de contenido informativo en línea, de forma eficaz, gratuita y accesible para el público en general en México y América Latina.

### Diapositiva 4 — Objetivos Específicos
- Diseñar una interfaz de usuario intuitiva con estética ciberpunk que permita analizar URLs de noticias de forma sencilla
- Desarrollar un módulo de extracción de contenido web (scraping multicapa) que obtenga el texto principal eliminando publicidad y navegación
- Integrar la API de Groq con el modelo Llama 3.3-70B-versatile para clasificar el contenido en 5 categorías de credibilidad
- Desarrollar un sistema de búsqueda de noticias similares usando Google News RSS para proporcionar contexto adicional
- Implementar soporte bilingüe (español e inglés) para mayor accesibilidad

### Diapositiva 5 — Metodología de Desarrollo
- Metodología ágil **Kanban** con tablero horizontal personalizado
- Gestión del proyecto con GitHub Projects y Kanban físico en Excel
- Versiones del sistema (v0.1.0 a v1.2.0) con entregas incrementales
- 5 capítulos de tesis alineados con el desarrollo del sistema
- Gestión de riesgos con matriz de probabilidad-impacto y plan de contingencia

### Diapositiva 6 — Arquitectura del Sistema (Diagrama de Componentes)
La aplicación VERIFEX sigue una arquitectura de **2 capas (frontend-backend)** sin base de datos:

**Frontend:**
- React 18 con TypeScript y Vite como bundler
- Componentes funcionales con hooks (useState, useEffect, useCallback, useMemo)
- Estilos con CSS Modules y estética ciberpunk (fondos oscuros, colores neón #00FFF7, #FF00FF, #7B2FF7)
- Consumo de API REST backend mediante fetch
- Despliegue en Vercel (https://verifex.vercel.app)

**Backend:**
- Python 3.10+ con Flask para la API REST
- Flask-CORS para comunicación entre dominios
- python-dotenv para variables de entorno
- Endpoints: POST /analyze (recibe URL, devuelve JSON con análisis completo)
- Despliegue en Render.com con Gunicorn (https://verifex.onrender.com)

**NO hay base de datos** — cada análisis se realiza en memoria y se descarta al cerrar. No se almacenan datos de usuario.

### Diapositiva 7 — Módulo de Scraping (Extracción de Contenido)
Scraping multicapa con 3 estrategias progresivas:

**Estrategia 1 — Newspaper3k (Capa 1):**
- Uso de la librería `newspaper3k` con `Article.download()` y `Article.parse()`
- Extrae título, texto principal, autor, fecha de publicación, imágenes
- Tiempo de espera máximo: 10 segundos
- Si falla (sitio bloquea bots, red social, paywall), pasa a Estrategia 2

**Estrategia 2 — requests + BeautifulSoup4 + readability (Capa 2):**
- Petición HTTP con headers personalizados (User-Agent realista: Chrome 120, acepta text/html)
- Parseo con BeautifulSoup4 (lxml) para extraer title, meta tags (og:title, description, author), text_body
- Limpieza usando `readability-lxml` para extraer el contenido principal del artículo
- Se eliminan elementos no deseados: scripts, estilos, navegación, publicidad
- Tiempo de espera máximo: 15 segundos

**Estrategia 3 — Selenium WebDriver (Capa 3 — Último recurso):**
- Para sitios con renderizado JavaScript pesado (redes sociales, SPA)
- Usa ChromeDriver en modo headless
- Navega a la URL, espera carga completa, extrae texto de <body>
- Timeout de carga: 20 segundos
- Solo se activa si las estrategias 1 y 2 fallan

**Manejo de errores:** timeout por estrategia, logs detallados, fallback progresivo. Si todas fallan, se devuelve error "No se pudo extraer el contenido".

### Diapositiva 8 — Módulo de News Finder (Búsqueda de Noticias Similares)
- Búsqueda usando Google News RSS (`https://news.google.com/rss/search?q={query}&hl=es-419&gl=MX&ceid=MX:es-419`)
- Para cada noticia en resultados RSS:
  - Se extrae: título, fuente, enlace
  - Se usa otro scraping (con la misma lógica multicapa) por cada enlace encontrado
  - Se muestran extractos cortos de las noticias relacionadas
- Procesamiento asíncrono con timeout global de 30 segundos
- Máximo 3-5 noticias similares mostradas al usuario
- Si no hay conexión a internet, la sección de noticias similares se omite sin error fatal

### Diapositiva 9 — Módulo de Análisis con IA (Groq API + Llama 3.3-70B)
- API de Groq en la nube (`https://api.groq.com/openai/v1/chat/completions`)
- Modelo: `llama-3.3-70b-versatile`
- Parámetros: temperatura 0.3 (baja para consistencia), max_tokens 4096
- Clave API almacenada en variable de entorno GROQ_API_KEY

**System Prompt del análisis (en español):**
Se envía un prompt detallado que instruye al modelo a:
1. Extraer el título y las afirmaciones principales del artículo
2. Clasificar el contenido en una de estas 5 categorías:
   - REAL: información verificada y verdadera
   - FALSO: información falsa o engañosa
   - SÁTIRA: contenido satírico o de humor
   - ESTAFA: intento de fraude o estafa
   - NO VERIFICABLE: no hay suficiente evidencia
3. Proporcionar un nivel de confianza del 0% al 100%
4. Generar un resumen del artículo (máximo 150 palabras en español)
5. Listar afirmaciones principales con su verificación individual
6. Identificar banderas rojas (señales de alerta): lenguaje sensacionalista, afirmaciones sin fuente, manipulación emocional, teorías de conspiración, falsa autoridad, sesgo extremo
7. Identificar señales positivas: fuentes citadas, datos verificables, lenguaje equilibrado, múltiples perspectivas, fecha clara, autor identificable
8. Generar un análisis detallado (máximo 300 palabras)

**System Prompt del análisis (en inglés):**
Misma estructura pero el contenido se genera en inglés (resumen, afirmaciones, análisis, banderas, señales).

**Estructura del JSON de respuesta de Groq (en español):**
```json
{
  "title": "Título del artículo",
  "verdict": "REAL|FALSO|SATIRA|ESTAFA|NO VERIFICABLE",
  "confidence": 85,
  "summary": "Resumen en español...",
  "claims": [
    {"claim": "Afirmación 1", "verification": "Verdadero/Falso/No verificable", "evidence": "Evidencia..."}
  ],
  "red_flags": ["Lenguaje sensacionalista", "Afirmaciones sin fuente"],
  "positive_signals": ["Fuentes citadas", "Lenguaje equilibrado"],
  "detailed_analysis": "Análisis detallado en español..."
}
```

**Estructura del JSON de respuesta de Groq (en inglés):**
```json
{
  "title": "Article title",
  "verdict": "REAL|FAKE|SATIRE|SCAM|NOT_VERIFIABLE",
  "confidence": 85,
  "summary": "English summary...",
  "claims": [{"claim": "...", "verification": "...", "evidence": "..."}],
  "red_flags": ["..."],
  "positive_signals": ["..."],
  "detailed_analysis": "..."
}
```

### Diapositiva 10 — Frontend: Componentes y Funcionalidad
- **App.tsx:** Componente principal que maneja estado global, cambio de idioma, conexión con backend y renderizado de componentes hijos
- **UrlInputBar:** Barra de entrada de URL con validación, botón de análisis y loading state
- **LanguageToggle:** Selector de idioma (español ↔ inglés)
- **ResultCard:** Muestra el veredicto con icono y color según categoría:
  - REAL → verde (#00C853)
  - FALSO → rojo (#FF1744)
  - SÁTIRA → naranja (#FF9100)
  - ESTAFA → rojo oscuro (#D50000)
  - NO VERIFICABLE → gris (#757575)
- **ConfidenceGauge:** Barra de progreso circular que muestra el nivel de confianza del 0% al 100%
- **ClaimsSection:** Lista de afirmaciones principales con su verificación individual
- **AnalysisSection:** Análisis detallado del contenido
- **RedFlagsSection:** Alertas detectadas con iconos de advertencia
- **PositiveSignalsSection:** Señales positivas con iconos de check
- **SimilarNewsSection:** Noticias similares encontradas con enlaces
- **Footer:** Información de privacidad y enlaces del equipo

### Diapositiva 11 — Frontend: Estados de la UI
- **Estado inicial:** Muestra solo la barra de URL, selector de idioma y un mensaje de bienvenida
- **Estado de carga:** Botón de análisis deshabilitado, spinner animado, mensaje "Analizando..."
- **Estado de resultados:** Muestra todas las secciones con los datos del análisis
- **Estado de error:** Muestra mensaje de error específico según el tipo de fallo (URL inválida, scraping fallido, API de IA caída, timeout)
- **Estado responsive:** La interfaz se adapta a dispositivos móviles (media queries, flexbox/grid)

### Diapositiva 12 — Soporte Bilingüe
- Detección de idioma basada en el contenido de la URL (dominio .mx, .es, .com.mx → español; .com, .org, .gov → inglés; detección automática por palabras clave)
- Traducción completa de la interfaz de usuario (todos los textos, etiquetas, mensajes)
- Traducción del análisis mediante un segundo llamado a Groq con system prompt en inglés
- Resultados en inglés en lugar de español cuando el usuario selecciona inglés
- Persistencia de preferencia de idioma en localStorage

### Diapositiva 13 — Pruebas Realizadas
**Pruebas de funcionalidad:**
- 5 URLs reales analizadas con veredictos esperados documentados
- Verificación de cada categoría de clasificación (REAL, FALSO, SÁTIRA, ESTAFA, NO VERIFICABLE)
- Prueba de URLs inválidas y manejo de errores

**Pruebas de usabilidad:**
- Interfaz responsive probada en Chrome, Firefox, Safari, Edge
- Prueba en dispositivos móviles (viewport 320px-1920px)
- Tiempo de respuesta percibido por el usuario

**Pruebas de seguridad:**
- Validación de URLs (solo http/https, sanitización de input)
- Protección contra inyección de prompts en el análisis
- Sin almacenamiento de datos del usuario
- CORS configurado correctamente

### Diapositiva 14 — Despliegue y Resultados
- **Frontend:** Vercel (https://verifex.vercel.app) — despliegue continuo desde GitHub
- **Backend:** Render.com (https://verifex.onrender.com) — servicio web con Gunicorn, plan gratuito
- **Repositorio:** GitHub como control de versiones (commits convencionales)
- **Resultados obtenidos:**
  - El sistema clasifica correctamente noticias reales y falsas con un nivel de confianza asociado
  - La interfaz ciberpunk es intuitiva para usuarios sin experiencia técnica
  - El scraping multicapa extrae contenido exitosamente de ~85% de las URLs probadas
  - El soporte bilingüe funciona correctamente para español e inglés
  - Las noticias similares proporcionan contexto valioso para la verificación

### Diapositiva 15 — Tecnologías Utilizadas (Stack Completo)
**Frontend:** React 18, TypeScript, Vite, CSS Modules
**Backend:** Python 3.10+, Flask, Flask-CORS, python-dotenv, Gunicorn
**Scraping:** newspaper3k, requests, BeautifulSoup4 (lxml), readability-lxml, Selenium + ChromeDriver
**IA:** Groq API (Llama 3.3-70B-versatile), temperatura 0.3, max_tokens 4096
**Noticias Similares:** Google News RSS, scraping asíncrono
**Despliegue:** Vercel (frontend) + Render.com (backend)
**Control de Versiones:** Git + GitHub, GitHub Projects, Kanban
**Documentación:** Word, Excel (Gantt, Kanban), draw.io (diagramas)

### Diapositiva 16 — Conclusiones
- VERIFEX cumple con el objetivo de proporcionar una herramienta accesible, gratuita y funcional para la verificación de noticias
- La integración de Groq API con Llama 3.3-70B permite análisis profundos y contextualizados del contenido
- El scraping multicapa garantiza la extracción de contenido incluso en sitios con restricciones
- La interfaz ciberpunk y el soporte bilingüe hacen la herramienta atractiva y accesible para una audiencia amplia
- VERIFEX contribuye a mitigar el impacto de la desinformación en México y América Latina
- Limitaciones identificadas: dependencia de conexión a internet, no analiza contenido multimedia, precisión variable según el modelo de IA

---

## Instrucciones de formato para la presentación
- Usa un diseño profesional, sobrio y académico (no uses plantillas genéricas de tecnología)
- Los colores deben ser sobrios con acentos en tonos azul o púrpura (relacionado con la estética ciberpunk)
- Usa diagramas de cajas simples para la arquitectura (frontend → backend → Groq API)
- Incluye capturas de pantalla sugeridas en diapositivas clave (interfaz de usuario, resultados de análisis)
- Tabla comparativa en diapositiva de tecnologías
- NO uses emojis, iconos genéricos de redes sociales, o elementos visuales que no correspondan al contexto académico
- La audiencia es un comité de titulación de ingeniería, no inversionistas ni público general
- Cada diapositiva debe tener un título claro y contenido con viñetas (bullet points)
- Extensión sugerida: 15-20 diapositivas
- NO incluyas secciones de "preguntas y respuestas" ni "gracias por su atención" a menos que sea necesario
- NO agregues información de otras tecnologías, frameworks o herramientas que no estén listadas aquí
