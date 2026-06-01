from product import get_product_id

from odoo_client import models, uid
from config import DB, PASSWORD


def create_sales_order(partner_id, items):
    """
    Creates quotation in Odoo.

    Example:

    create_sales_order(
        58,
        [
            ("Cabinet with Doors", 2),
            ("Acoustic Bloc Screens", 3)
        ]
    )
    """

    order_lines = []

    for product_name, quantity in items:

        product_id = get_product_id(product_name)

        order_lines.append(
            (
                0,
                0,
                {
                    "product_id": product_id,
                    "product_uom_qty": quantity
                }
            )
        )

    sale_order_id = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "sale.order",
        "create",
        [{
            "partner_id": partner_id,
            "order_line": order_lines
        }]
    )

    return sale_order_id
