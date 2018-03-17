from quoine.client import Quoinex
client = Quoinex(api_key, api_secret)

# get products
products = client.get_products()

# get market depth
depth = client.get_order_book(product_id=products[0]['id'])

# place market buy order
order = client.create_market_buy(
    product_id=products[0]['id'],
    quantity='100',
    price_range='0.01')

# get list of filled orders
filled_orders = client.get_orders(status=client.STATUS_FILLED)

