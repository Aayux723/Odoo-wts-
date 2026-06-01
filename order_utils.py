def get_valid_order_items(parsed):
    items = []

    for item in parsed.get("items", []):
        product = str(item.get("product", "")).strip()
        qty = item.get("qty", 0)

        try:
            qty = float(qty)
        except (TypeError, ValueError):
            continue

        if product and qty > 0:
            items.append((product, qty))

    return items


def is_sales_order_request(parsed):
    if "is_order" in parsed and not parsed.get("is_order"):
        return False

    return bool(get_valid_order_items(parsed))
