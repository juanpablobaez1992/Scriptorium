"""
bot/telegram_bot.py
Bot de Telegram para capturar ideas por texto, audio e imagen.
Arquitectura: Bot.
"""

from __future__ import annotations

from pathlib import Path
import sys
from uuid import uuid4

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Permite ejecutar `python bot/telegram_bot.py` desde el directorio `scriptorium/`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scriptorium.app import create_app
from scriptorium.models import Idea, InputFile, Project
from scriptorium.services.input_service import InputService
from scriptorium.services.search_service import SearchService


def _storage_path(app, section: str, filename: str) -> str:
    folder = Path(app.config["STORAGE_PATH"]) / section / "pending"
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder / f"{uuid4().hex}_{filename}")


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SCRIPTORIUM: No guardar ideas. Revelar relaciones.\n"
        "Enviame texto, audio, nota de voz o imagen y lo convierto en idea."
    )


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/idea <texto>\n/ultimas\n/buscar <texto>\n/pendientes\n/revisar\n/proyectos\n/describir <id> <desc>"
    )


async def handle_idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Uso: /idea Tu idea aqui")
        return
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        idea = InputService().process_text_input(text, source="telegram", source_detail=str(update.effective_user.id))
        await update.message.reply_text(
            f"Idea guardada.\n\nTitulo: {idea.title}\nResumen: {idea.summary}\nEstado: {idea.status}"
        )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        idea = InputService().process_text_input(text, source="telegram", source_detail=str(update.effective_user.id))
        await update.message.reply_text(
            f"Idea guardada.\nTitulo: {idea.title}\nCategoria sugerida: "
            f"{idea.category.name if idea.category else 'Sin categoria'}"
        )


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    voice = update.message.voice
    tg_file = await context.bot.get_file(voice.file_id)
    local_path = _storage_path(app, "audio", "voice.ogg")
    await tg_file.download_to_drive(local_path)
    with app.app_context():
        idea, input_file = InputService().process_audio_input(
            {
                "file_type": "voice",
                "local_path": local_path,
                "telegram_file_id": voice.file_id,
                "original_filename": "voice.ogg",
                "mime_type": voice.mime_type,
            },
            source="telegram",
            source_detail=str(update.effective_user.id),
        )
        if idea:
            await update.message.reply_text(
                f"Audio transcripto y guardado.\nTitulo: {idea.title}\nResumen: {idea.summary}"
            )
        else:
            await update.message.reply_text(
                f"Guardado como pendiente (ID {input_file.id}). Usa /pendientes para revisar."
            )


async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    audio = update.message.audio
    tg_file = await context.bot.get_file(audio.file_id)
    filename = audio.file_name or "audio.mp3"
    local_path = _storage_path(app, "audio", filename)
    await tg_file.download_to_drive(local_path)
    with app.app_context():
        idea, input_file = InputService().process_audio_input(
            {
                "file_type": "audio",
                "local_path": local_path,
                "telegram_file_id": audio.file_id,
                "original_filename": filename,
                "mime_type": audio.mime_type,
            },
            source="telegram",
            source_detail=str(update.effective_user.id),
        )
        if idea:
            await update.message.reply_text(f"Audio procesado como idea: {idea.title}")
        else:
            await update.message.reply_text(f"Audio guardado pendiente (ID {input_file.id}).")


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    photo = update.message.photo[-1]
    caption = update.message.caption
    tg_file = await context.bot.get_file(photo.file_id)
    local_path = _storage_path(app, "images", "photo.jpg")
    await tg_file.download_to_drive(local_path)
    with app.app_context():
        idea, input_file = InputService().process_image_input(
            {
                "file_type": "image",
                "local_path": local_path,
                "telegram_file_id": photo.file_id,
                "original_filename": "photo.jpg",
                "mime_type": "image/jpeg",
            },
            caption=caption,
            source="telegram",
            source_detail=str(update.effective_user.id),
        )
        if idea:
            await update.message.reply_text(f"Imagen procesada y guardada como idea: {idea.title}")
        else:
            await update.message.reply_text(
                "Guardé la imagen como referencia. No pude extraer texto todavia. "
                f"Usa /describir {input_file.id} <descripcion>."
            )


async def handle_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    document = update.message.document
    mime = document.mime_type or ""
    if not mime.startswith("image/"):
        await update.message.reply_text("Documento recibido. Esta version procesa solo imagenes.")
        return
    tg_file = await context.bot.get_file(document.file_id)
    filename = document.file_name or "document_image.jpg"
    local_path = _storage_path(app, "documents", filename)
    await tg_file.download_to_drive(local_path)
    with app.app_context():
        idea, input_file = InputService().process_image_input(
            {
                "file_type": "document_image",
                "local_path": local_path,
                "telegram_file_id": document.file_id,
                "original_filename": filename,
                "mime_type": mime,
            },
            caption=update.message.caption,
            source="telegram",
            source_detail=str(update.effective_user.id),
        )
        if idea:
            await update.message.reply_text(f"Documento de imagen procesado: {idea.title}")
        else:
            await update.message.reply_text(f"Documento guardado pendiente (ID {input_file.id}).")


async def handle_latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        ideas = Idea.query.order_by(Idea.created_at.desc()).limit(5).all()
    if not ideas:
        await update.message.reply_text("Todavia no hay ideas.")
        return
    msg = "\n".join([f"{idea.id}. {idea.title}" for idea in ideas])
    await update.message.reply_text(f"Ultimas ideas:\n{msg}")


async def handle_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = " ".join(context.args).strip()
    if not q:
        await update.message.reply_text("Uso: /buscar texto")
        return
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        ideas = SearchService().search_ideas({"q": q})[:8]
    if not ideas:
        await update.message.reply_text("No encontré resultados.")
        return
    msg = "\n".join([f"{idea.id}. {idea.title}" for idea in ideas])
    await update.message.reply_text(f"Resultados:\n{msg}")


async def handle_pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        pending = (
            InputFile.query.filter(InputFile.source == "telegram", InputFile.status != "procesado_como_idea")
            .order_by(InputFile.created_at.desc())
            .limit(10)
            .all()
        )
    if not pending:
        await update.message.reply_text("No hay pendientes.")
        return
    msg = "\n".join([f"{p.id}. {p.file_type} - {p.status}" for p in pending])
    await update.message.reply_text(f"Pendientes:\n{msg}")


async def handle_review_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        idea = Idea.query.filter(Idea.review_at.is_(None)).order_by(Idea.created_at.asc()).first()
    if not idea:
        await update.message.reply_text("No hay ideas pendientes de revision.")
        return
    await update.message.reply_text(
        f"Idea para revisar:\n{idea.id}. {idea.title}\nResumen: {idea.summary or '-'}"
    )


async def handle_projects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        projects = Project.query.filter(Project.status.in_(["activo", "emergente"])).limit(10).all()
    if not projects:
        await update.message.reply_text("No hay proyectos activos.")
        return
    msg = "\n".join([f"{p.id}. {p.name} ({p.status})" for p in projects])
    await update.message.reply_text(f"Proyectos:\n{msg}")


async def handle_describe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /describir ID descripcion")
        return
    try:
        input_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID invalido.")
        return
    description = " ".join(context.args[1:]).strip()
    app = context.application.bot_data["flask_app"]
    with app.app_context():
        pending = InputFile.query.get(input_id)
        if not pending:
            await update.message.reply_text("No encuentro esa entrada pendiente.")
            return
        idea = InputService().create_idea_from_processed_text(
            description,
            source="telegram",
            source_detail=str(update.effective_user.id),
            input_type="pending_input",
        )
        pending.idea_id = idea.id
        pending.status = "procesado_como_idea"
        from scriptorium.extensions import db

        db.session.commit()
    await update.message.reply_text(f"Descripcion aplicada. Nueva idea: {idea.title}")


def build_application() -> Application:
    flask_app = create_app()
    token = flask_app.config.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en .env")
    application = Application.builder().token(token).build()
    application.bot_data["flask_app"] = flask_app

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("ayuda", handle_help))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("idea", handle_idea_command))
    application.add_handler(CommandHandler("ultimas", handle_latest_command))
    application.add_handler(CommandHandler("buscar", handle_search_command))
    application.add_handler(CommandHandler("pendientes", handle_pending_command))
    application.add_handler(CommandHandler("revisar", handle_review_command))
    application.add_handler(CommandHandler("proyectos", handle_projects_command))
    application.add_handler(CommandHandler("describir", handle_describe_command))

    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    return application


def main() -> None:
    app = build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
