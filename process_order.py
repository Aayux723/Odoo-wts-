from ai_parser import parse_order
from customer import (
    get_customer_by_phone,
    create_customer
)
from order_utils import get_valid_order_items
from sales import create_sales_order


def process_parsed_order(
    whatsapp_number,
    parsed,
    saved_name=None
):
    items = get_valid_order_items(parsed)

    if not items:
        raise ValueError("No valid order items found. Odoo quotation was not created.")

    customer = get_customer_by_phone(
        whatsapp_number
    )

    if customer:

        customer_id = customer["id"]

    else:

        extracted_name = (
            saved_name
            or parsed.get("customer_name")
            or whatsapp_number
        )

        customer_id = create_customer(
            extracted_name,
            whatsapp_number
        )

    order_id = create_sales_order(
        customer_id,
        items
    )

    return order_id


def process_order(
    whatsapp_number,
    message,
    saved_name=None
):

    parsed = parse_order(
        message
    )

    return process_parsed_order(
        whatsapp_number,
        parsed,
        saved_name
    )
