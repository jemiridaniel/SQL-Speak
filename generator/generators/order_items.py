import random
from faker import Faker

fake = Faker()

def generate(num_order_items, max_order_id, max_product_id):
    """
    Generates order_items tuples:
    (order_id, product_id, quantity, unit_price, created_at)
    """
    for _ in range(num_order_items):
        order_id = random.randint(1, max_order_id)
        product_id = random.randint(1, max_product_id)
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(5, 500), 2)
        created_at = fake.date_time_between(start_date='-2y', end_date='now')
        yield (order_id, product_id, quantity, unit_price, created_at)
