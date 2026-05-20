# VERIFEX — Analizador de Credibilidad

Detecta noticias falsas, estafas y desinformación. Utiliza la API de Groq (gratis) con modelos llama3 para análisis rápidos en 1-3 segundos.

---

## Requisitos previos

- **Node.js** v18, v20 o v22 — [nodejs.org](https://nodejs.org)
- **Python 3.10+** — [python.org](https://python.org)
- **API key de Groq** — gratis en https://console.groq.com (sin tarjeta)

---

## 1. Obtener API key de Groq

1. Ve a https://console.groq.com y crea una cuenta (solo email)
2. Ve a **API Keys** y genera una key nueva
3. Copia la key (empieza con `gsk_...`)

---

## 2. Configurar el backend

```bash
cd verifex/server
pip3 install -r requirements.txt
```

Copia el archivo de configuración y pega tu API key:

```bash
cp .env.example .env
# Edita .env y pega tu key: GROQ_API_KEY=gsk_tu_key_aqui
```

Inicia el backend:

```bash
python3 app.py
```

Deberías ver:
```
🔥 VERIFEX backend corriendo en http://localhost:5001
```

Deja esa terminal abierta.

---

## 3. Iniciar el frontend

Abre **otra terminal** en la raíz del proyecto:

```bash
cd verifex
npm install
npm run dev
```

---

## 4. Abrir la aplicación

Abre tu navegador en:

```
http://localhost:5173
```

¡Listo! Pega cualquier URL de noticia y haz clic en **Analizar**.

---

## Solución de problemas

**"GROQ_API_KEY no configurada"**  
→ Crea `server/.env` con `GROQ_API_KEY=gsk_tu_key`

**Error de puerto ocupado**  
→ Otro proceso usa el puerto 5001. Cambia `FLASK_PORT` en `server/.env`

**"python no encontrado"**  
→ Usa `python3` en lugar de `python`

**Error de permisos con pip**  
→ Usa `pip3 install --user -r requirements.txt`

---

## Notas

- El análisis tarda entre **1 y 3 segundos** (vs 30-60s con Ollama local)
- No se guarda ningún dato — cada análisis es completamente en memoria
- No necesitas GPU ni instalar modelos de IA local
- **No requiere Ollama** — funciona con la API en la nube de Groq

---

## Despliegue en Railway (producción)

1. Sube el proyecto a GitHub
2. Ve a https://railway.app y conecta tu repo
3. Railway detecta el `Procfile` automáticamente
4. Agrega la variable de entorno:
   - `GROQ_API_KEY` = `gsk_tu_key`
5. Railway usará el `Procfile` para iniciar el servidor
6. Construye el frontend: agrega un script en Railway:
   ```bash
   cd frontend && npm install && npm run build
   ```
   O manualmente: `npm run build` antes de hacer deploy

La app quedará en una URL pública como `https://verifex.up.railway.app`.
