import argparse
import json

from ai_parser import parse_order


DEFAULT_MESSAGE = """
Hi, this is Sanad Suman.

Need 2 Cabinet with Doors
and 3 Acoustic Bloc Screens
"""


def main():
    parser = argparse.ArgumentParser(
        description="Test WhatsApp-to-Odoo order parsing before WhatsApp API integration."
    )
    parser.add_argument(
        "--phone",
        default="+9199999999999",
        help="WhatsApp phone number to search/create in Odoo."
    )
    parser.add_argument(
        "--saved-name",
        default=None,
        help="Saved WhatsApp contact name to use when the number is not in Odoo."
    )
    parser.add_argument(
        "--message",
        default=DEFAULT_MESSAGE,
        help="Message text to parse."
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Actually create/find the customer and create the Odoo quotation."
    )

    args = parser.parse_args()

    print("Parsing message with AI...")
    try:
        parsed = parse_order(args.message)
    except Exception as exc:
        print(f"\nAI parsing failed: {exc}")
        return

    print("\nParsed order:")
    print(json.dumps(parsed, indent=2))

    if not args.create:
        print("\nDry run only. Add --create to create the customer/quotation in Odoo.")
        return

    from process_order import process_parsed_order

    print("\nCreating quotation in Odoo...")
    order_id = process_parsed_order(
        whatsapp_number=args.phone,
        parsed=parsed,
        saved_name=args.saved_name
    )

    print(f"\nQuotation created. Sale Order ID: {order_id}")


if __name__ == "__main__":
    main()
