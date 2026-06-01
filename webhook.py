import json
import os

from fastapi import FastAPI, Request

from ai_parser import load_local_env
from ai_parser import parse_order
from order_utils import is_sales_order_request

app = FastAPI()

load_local_env()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "aayush_odoo_verify")


def normalize_whatsapp_phone(phone):
    phone = str(phone).strip()

    if phone.startswith("+"):
        return phone

    return f"+{phone}"


def get_saved_contact_name(value):
    contacts = value.get("contacts", [])

    if not contacts:
        return None

    profile = contacts[0].get("profile", {})
    return profile.get("name")


@app.get("/webhook")
async def verify(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "verification failed"}


@app.post("/webhook")
async def receive(request: Request):

    print("\n========== POST HIT ==========")

    data = await request.json()

    print("\nFULL PAYLOAD:")
    print(data)

    try:
        value = (
            data["entry"][0]
                ["changes"][0]
                ["value"]
        )

        if "messages" in value:

            message = value["messages"][0]

            phone = normalize_whatsapp_phone(message["from"])
            saved_name = get_saved_contact_name(value)

            if "text" in message:
                text = message["text"]["body"]
            else:
                text = "[non-text message]"

            print("\nPHONE:", phone)
            print("SAVED NAME:", saved_name)
            print("MESSAGE:", text)

            if text != "[non-text message]":
                try:
                    parsed = parse_order(text)

                    print("\nAI PARSED RESULT:")
                    print(json.dumps(parsed, indent=2))

                    if not is_sales_order_request(parsed):
                        print("\nNO SALES ORDER CREATED:")
                        print("Message does not contain valid order items.")
                        return {"status": "ignored", "reason": "not_a_sales_order"}

                    from process_order import process_parsed_order

                    order_id = process_parsed_order(
                        whatsapp_number=phone,
                        parsed=parsed,
                        saved_name=saved_name
                    )

                    print("\nODOO QUOTATION CREATED:")
                    print("SALE ORDER ID:", order_id)

                except Exception as e:
                    print("\nERROR PROCESSING SALES ORDER:")
                    print(str(e))

        else:
            print("\nNo messages field found.")
            print("Webhook type:", value.keys())

    except Exception as e:
        print("\nERROR PARSING MESSAGE:")
        print(str(e))

    return {"status": "ok"}
