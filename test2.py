from customer import get_customer_id
from product import get_product_id
from sales import create_sales_order


print("===== CUSTOMER TEST =====")

customer_id = get_customer_id(
    "Aayush Test Customer"
)

print("Customer ID:", customer_id)


print("\n===== PRODUCT TEST =====")

product_id = get_product_id(
    "Cabinet with Doors"
)

print("Product ID:", product_id)


print("\n===== SALES ORDER TEST =====")

order_id = create_sales_order(
    partner_id=customer_id,
    items=[
        ("Cabinet with Doors", 2)
    ]
)

print("Sales Order ID:", order_id)


print("\n===== MULTI-PRODUCT TEST =====")

order_id = create_sales_order(
    partner_id=customer_id,
    items=[
        ("Cabinet with Doors", 2),
        ("Acoustic Bloc Screens", 3)
    ]
)

print("Sales Order ID:", order_id)

print("\nAll tests passed.")
