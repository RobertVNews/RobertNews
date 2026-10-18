"""Avisa por Telegram cuando un contacto (p. ej. tu hijo) pasa a "en línea".

Requiere que el contacto tenga visible su "última vez en línea" para ti.
Usa la API oficial de Telegram para cuentas de usuario (Telethon).
"""
import asyncio
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
TARGET = os.environ["TG_TARGET"]  # @usuario, teléfono +34... o ID numérico
MIN_GAP = int(os.getenv("MIN_GAP_SECONDS", "300"))  # anti-spam entre avisos
NAME = os.getenv("TARGET_LABEL", "Tu contacto")

client = TelegramClient("session", API_ID, API_HASH)
last_alert = 0.0


async def main():
    await client.start()
    target = await client.get_entity(TARGET)
    print(f"Vigilando a {target.first_name} ({target.id}). Ctrl+C para salir.")

    @client.on(events.UserUpdate(chats=target))
    async def on_update(event):
        global last_alert
        if not event.online:
            return
        now = time.time()
        if now - last_alert < MIN_GAP:
            return
        last_alert = now
        msg = f"🟢 {NAME} está en línea ({datetime.now():%H:%M})"
        print(msg)
        await client.send_message("me", msg)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
