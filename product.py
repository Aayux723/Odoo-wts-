from odoo_client import models, uid
from config import DB, PASSWORD


def normalize_text(value):
    return " ".join(str(value).lower().split())


def get_search_words(product_name):
    ignored_words = {"a", "an", "and", "for", "i", "need", "of", "the", "to", "with"}

    return [
        word
        for word in normalize_text(product_name).split()
        if word not in ignored_words
    ]


def search_products(domain, limit=20):
    return models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.product",
        "search_read",
        [domain],
        {
            "fields": ["id", "name", "default_code"],
            "limit": limit
        }
    )


def score_product(product, search_words):
    product_name = normalize_text(product["name"])
    product_words = set(product_name.split())

    score = 0

    for word in search_words:
        if word in product_words:
            score += 3
        elif word in product_name:
            score += 1

    return score


def choose_best_product(products, product_name):
    search_words = get_search_words(product_name)

    if not products or not search_words:
        return None

    scored_products = [
        (score_product(product, search_words), product)
        for product in products
    ]
    scored_products.sort(key=lambda item: item[0], reverse=True)

    best_score, best_product = scored_products[0]

    if best_score <= 0:
        return None

    return best_product


def get_product_id(product_name):
    """
    Returns product ID from natural product text.
    Raises exception if no matching Odoo product exists.
    """

    products = search_products(
        [["name", "=", product_name]],
        limit=1
    )

    if products:
        print(f"Matched product '{product_name}' -> '{products[0]['name']}'")
        return products[0]["id"]

    products = search_products(
        [["name", "ilike", product_name]],
        limit=10
    )

    best_product = choose_best_product(products, product_name)

    if best_product:
        print(f"Matched product '{product_name}' -> '{best_product['name']}'")
        return best_product["id"]

    search_words = get_search_words(product_name)

    if search_words:
        domain = []

        for index, word in enumerate(search_words):
            if index:
                domain.insert(0, "&")

            domain.append(("name", "ilike", word))

        products = search_products(domain, limit=20)
        best_product = choose_best_product(products, product_name)

        if best_product:
            print(f"Matched product '{product_name}' -> '{best_product['name']}'")
            return best_product["id"]

    raise Exception(
        f"Product '{product_name}' not found"
    )
