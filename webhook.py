import json
import os

from fastapi import FastAPI, Request

from ai_parser import parse_order
from env_utils import load_local_env
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

            text = "[non-text message]"
            image_id = None
            message_type = message.get("type")
            
            if message_type == "text":
                text = message.get("text", {}).get("body", text)
            elif message_type == "image":
                image_info = message.get("image", {})
                image_id = image_info.get("id")
                text = image_info.get("caption", "[image message]")

            print("\nPHONE:", phone)
            print("SAVED NAME:", saved_name)
            print("MESSAGE:", text)

            if text != "[non-text message]" or image_id:
                image_path = None
                try:
                    if image_id:
                        from config import WHATSAPP_ACCESS_TOKEN
                        if WHATSAPP_ACCESS_TOKEN:
                            from whatsapp_media import download_media
                            try:
                                print(f"\nDOWNLOADING IMAGE: {image_id}")
                                image_path = download_media(image_id, WHATSAPP_ACCESS_TOKEN)
                                print(f"Downloaded image to {image_path}")
                            except Exception as e:
                                print(f"Failed to download image: {e}")
                        else:
                            print("WHATSAPP_ACCESS_TOKEN not set, skipping image download.")

                    parsed = parse_order(text, image_path=image_path)

                    print("\nAI PARSED RESULT:")
                    print(json.dumps(parsed, indent=2))

                    if not is_sales_order_request(parsed):
                        print("\nNO SALES ORDER CREATED:")
                        print("Message does not contain valid order items.")
                        # We still want to return a response if this is the only message being processed
                        # But since we are in a loop (conceptually), we can't return immediately if there are more
                        # In this simplified code, we return immediately which matches original behaviour
                        
                        # Wait, the finally block needs to execute before return.
                        # Using a return inside a try block will execute finally.
                    else:
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
                finally:
                    if image_path and os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            print(f"Cleaned up {image_path}")
                        except Exception as e:
                            print(f"Failed to clean up image {image_path}: {e}")

        else:
            print("\nNo messages field found.")
            print("Webhook type:", value.keys())

    except Exception as e:
        print("\nERROR PARSING MESSAGE:")
        print(str(e))

    return {"status": "ok"}
