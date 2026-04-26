# SCRIPTORIUM

No guardar ideas. Revelar relaciones.

SCRIPTORIUM es un segundo cerebro personal construido con Flask. Permite capturar ideas desde web y Telegram, clasificarlas, relacionarlas, revisarlas y visualizarlas como grafo interactivo.

## Objetivo

Transformar capturas sueltas (texto, audio, imagen) en conocimiento conectado y accionable sin perder ninguna entrada.

## Stack

- Python + Flask (MVC + capa de servicios)
- SQLite + SQLAlchemy
- Jinja2 + Bootstrap + JS simple
- Cytoscape.js para grafo
- python-telegram-bot para captura externa
- pytesseract (OCR configurable)
- Whisper/OpenAI (transcripcion configurable)

## Estructura

La app principal esta en `scriptorium/` con carpetas:

- `models/`: entidades SQLAlchemy.
- `controllers/`: rutas web y API interna.
- `services/`: logica de negocio (clasificacion, sugerencias, relaciones, inputs, grafo).
- `bot/`: bot de Telegram.
- `templates/` y `static/`: interfaz.
- `storage/`: archivos recibidos (`audio`, `images`, `documents`).
- `instance/`: base SQLite local.

## Instalacion

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Abrir: `http://127.0.0.1:5000`

## Deploy en VPS

Comando WSGI recomendado:

```bash
gunicorn --bind 127.0.0.1:5000 --workers 2 --threads 4 wsgi:application
```

Checklist minima de produccion:

- Configurar `SECRET_KEY` real.
- Configurar `AUTH_USERNAME` y `AUTH_PASSWORD_HASH`.
- Usar `SESSION_COOKIE_SECURE=1` si hay HTTPS con Nginx o proxy.
- Apuntar `DATABASE_URL` a PostgreSQL o dejar SQLite solo para instalaciones pequenas.
- Verificar el health check en `/healthz`.

El endpoint `/healthz` queda publico por defecto para monitoreo.

## Deploy con contenedor

Archivos incluidos para VPS:

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.https.yml`
- `deploy/nginx/scriptorium.conf`
- `deploy/nginx/scriptorium.ssl.conf`

Pasos minimos:

1. Copia `.env.example` a `.env`.
2. Define `SECRET_KEY`, `AUTH_USERNAME` y `AUTH_PASSWORD_HASH`.
3. Levanta la app con Nginx + app:

```bash
docker compose up -d --build
```

4. Verifica salud:

```bash
curl http://127.0.0.1:5000/healthz
```

Persistencia:

- `./data/instance` guarda la base SQLite.
- `./data/storage` guarda audios, imagenes y documentos.

HTTP por defecto:

- `docker-compose.yml` publica solo Nginx en `80`.
- La app Flask queda interna en la red Docker.

HTTPS con certificados montados:

1. Coloca tus certificados en `./deploy/certs/fullchain.pem` y `./deploy/certs/privkey.pem`.
2. Reemplaza `example.com` en `deploy/nginx/scriptorium.ssl.conf` por tu dominio real.
3. Levanta la variante HTTPS:

```bash
docker compose -f docker-compose.yml -f docker-compose.https.yml up -d --build
```

## Deploy automatico desde GitHub

El repo incluye:

- `.github/workflows/deploy.yml`
- `deploy/vps/deploy.sh`

Flujo:

1. Haces push a `main`.
2. GitHub Actions valida el codigo con `compileall`.
3. La action entra por SSH al VPS.
4. En el VPS hace `git pull --ff-only origin main`.
5. Ejecuta `docker compose up -d --build`.
6. Verifica `/healthz`.

Preparacion del VPS:

```bash
sudo mkdir -p /srv/scriptorium
cd /srv/scriptorium
git clone https://github.com/juanpablobaez1992/Scriptorium.git .
cp .env.example .env
```

Despues:

- Completa `.env` con tus secretos reales.
- Instala Docker y Docker Compose.
- Si usaras HTTPS, coloca los certificados y define `DEPLOY_HTTPS=1` en el entorno del proceso remoto o como secreto del workflow.

Secrets de GitHub necesarios:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_PORT`
- `VPS_APP_DIR`
- `VPS_HEALTHCHECK_URL`
- `VPS_DEPLOY_HTTPS`

Valores sugeridos:

- `VPS_PORT=22`
- `VPS_APP_DIR=/srv/scriptorium`
- `VPS_HEALTHCHECK_URL=http://127.0.0.1/healthz`
- `VPS_DEPLOY_HTTPS=0`

## Configuracion `.env`

Variables principales:

- `DATABASE_URL` (por defecto SQLite local).
- `AUTH_USERNAME` / `AUTH_PASSWORD_HASH` para login local por sesion.
- `PUBLIC_ENDPOINTS` (endpoints separados por coma que no requieren login).
- `APP_HOST` / `APP_PORT` para arranque directo con `python app.py`.
- `SESSION_COOKIE_SECURE` para cookies solo por HTTPS.
- `INIT_DB_ON_BOOT` para crear tablas y seed inicial al arrancar.
- `TELEGRAM_BOT_TOKEN`.
- `TRANSCRIPTION_ENGINE=none|openai`.
- `OPENAI_API_KEY` si usas OpenAI Whisper.
- `OCR_ENGINE=tesseract`.
- `TESSERACT_CMD` si tu instalacion de Tesseract no esta en PATH.

## Ejecutar bot de Telegram

```powershell
venv\Scripts\activate
python -m scriptorium.bot.telegram_bot
```

Comandos:

- `/start`, `/ayuda`
- `/idea ...`
- `/ultimas`
- `/buscar ...`
- `/pendientes`
- `/revisar`
- `/proyectos`
- `/describir ID descripcion`

## Autenticacion local

La app protege las rutas web con login de usuario unico.

1. Configura `AUTH_USERNAME` y `AUTH_PASSWORD_HASH` en `.env`.
2. Genera hash desde una clave en texto plano:

```powershell
venv\Scripts\python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu-clave'))"
```

3. Define `PUBLIC_ENDPOINTS` para excluir endpoints puntuales del login (ejemplo: `telegram.telegram_status`).
4. Inicia la app y entra por `/login`.
5. Cierra sesion desde el link `Salir` en la barra superior.

### CLI para rotar credenciales

Tambien puedes rotar credenciales desde CLI:

```powershell
venv\Scripts\python -m scriptorium.auth_cli rotate --env-file .env --username admin
```

Sin `--password`, el comando pide la clave de forma interactiva y guarda:

- `AUTH_USERNAME`
- `AUTH_PASSWORD_HASH`

Ademas elimina `AUTH_PASSWORD` si existia en texto plano.

## Funcionalidades implementadas

- Dashboard con metricas y nodos nucleo.
- CRUD base de ideas + filtros + detalle.
- Taxonomia manual: ambitos, proyectos, categorias/subcategorias, etiquetas.
- Sugerencias pendientes con aceptar/rechazar/ignorar.
- Relaciones automaticas y manuales (via acciones).
- Grafo tipo Obsidian en `/graph` y JSON en `/api/graph`.
- Inputs pendientes + reprocesamiento.
- Captura Telegram de texto, audio/voz e imagen/documento de imagen.
- Fallback seguro: si falla transcripcion/OCR, queda pendiente sin perder datos.
- Revision semanal y tareas.
- API interna:
  - `/api/ideas`
  - `/api/graph`
  - `/api/suggestions`
  - `/api/orphan-ideas`
  - `/api/core-ideas`
  - `/api/projects/emerging`

## Flujo de clasificacion

1. Se guarda entrada.
2. Se genera titulo y resumen por reglas.
3. Se clasifica por palabras clave.
4. Se sugieren tags y relaciones.
5. Se registra log de clasificacion.
6. Se generan sugerencias de taxonomia pendientes (nunca definitivas automaticas).

## Grafo

`/api/graph` devuelve nodos y edges para Cytoscape:

- Nodos: idea, ambito, proyecto, categoria, etiqueta.
- Aristas: idea-idea + taxonomia-idea.
- Filtros: ambito, proyecto, categoria, fuerza minima, nucleo, huerfanas.

## Storage y pendientes

Todo archivo se guarda de forma segura en `scriptorium/storage`.
Si no se puede procesar:

- audio: `pendiente_transcripcion`
- imagen: `pendiente_ocr`

Queda disponible para `/inputs/pending` y reproceso manual.

## Base de datos

La base se crea automaticamente al iniciar (`db.create_all`) y se cargan datos iniciales:

- Ambitos base.
- Categorias base.

Mas adelante podes migrar a PostgreSQL cambiando `DATABASE_URL`.

## Mantenimiento

- Revisar pendientes en `/inputs/pending`.
- Revisar sugerencias en `/suggestions`.
- Ejecutar revision semanal en `/review/weekly`.
- Mantener taxonomia limpia fusionando categorias/tags duplicados.

## Proximos pasos sugeridos

- Mejor clasificador (embeddings + LLM).
- Mejor OCR/transcripcion local (faster-whisper).
- Exportador PDF/DOCX.
- Busqueda semantica real.
