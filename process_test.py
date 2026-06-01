from process_order import process_order

order_id = process_order(
    whatsapp_number="+919999999999",
    message="""
Hi

I need

2 Cabinet with Doors

3 Acoustic Bloc Screens
"""
)

print(order_id)