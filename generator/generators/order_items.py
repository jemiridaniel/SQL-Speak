import random
from faker import Faker

fake = Faker()

def generate(num_orders: int, num_products: int, min_items: int = 1, max_items: int = 5):
    """
    Generate order_items for benchmark database.
    
    Each order gets between min_items and max_items products.
    """
    def generator():
        for order_id in range(1, num_orders + 1):
            num_items = random.randint(min_items, max_items)
            for _ in range(num_items):
                product_id = random.randint(1, num_products)
                quantity = random.randint(1, 5)
                price = round(random.uniform(5.0, 500.0), 2)
                created_at = fake.date_time_between(start_date="-2y", end_date="now")
                yield (order_id, product_id, quantity, price, created_at)

    return generator()
