import os

from env_utils import load_local_env


load_local_env()

URL = os.getenv("ODOO_URL", "http://localhost:8069")
DB = os.getenv("ODOO_DB", "poc_db")
USERNAME = os.getenv("ODOO_USERNAME", "admin")
PASSWORD = os.getenv("ODOO_PASSWORD")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

if not PASSWORD:
    raise RuntimeError(
        "Set ODOO_PASSWORD in .env before connecting to Odoo."
    )
