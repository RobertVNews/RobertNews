# online-alert

Notificación en tu móvil cuando un contacto de Telegram pasa a "en línea".

## Uso
1. Crea credenciales en https://my.telegram.org (API development tools).
2. `cp .env.example .env` y rellénalo.
3. `pip install -r requirements.txt`
4. `python online_alert.py` (la primera vez pide tu teléfono y el código de Telegram).
5. Déjalo corriendo (VPS, Raspberry Pi o `tmux`). El aviso llega a "Mensajes guardados".

## Límites
- Solo funciona si el contacto muestra su "última vez en línea" a tu cuenta.
- Es para uso familiar y transparente: avisa a la persona vigilada.
- No guardes `.env` ni `*.session` en git: dan acceso a tu cuenta.
