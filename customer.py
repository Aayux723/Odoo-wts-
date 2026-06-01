from odoo_client import models
from odoo_client import uid
from config import DB, PASSWORD


def get_customer_by_phone(phone):

    customers = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [["|", ("phone", "=", phone), ("mobile", "=", phone)]],
        {
            "fields": ["id", "name", "phone", "mobile"],
            "limit": 1
        }
    )

    if customers:
        return customers[0]

    return None


def get_customer_id(customer_name):

    customers = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [[("name", "=", customer_name)]],
        {
            "fields": ["id", "name"],
            "limit": 1
        }
    )

    if not customers:
        raise Exception(
            f"Customer '{customer_name}' not found"
        )

    return customers[0]["id"]


def create_customer(name, phone):

    customer_id = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "create",
        [{
            "name": name,
            "phone": phone,
            "mobile": phone
        }]
    )

    return customer_id
