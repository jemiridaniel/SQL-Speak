import random
from faker import Faker

fake = Faker()

def generate(num_orders: int, num_customers: int):
    """Orders generator"""
    statuses = ["pending", "completed", "shipped", "cancelled"]

    def generator():
        for order_id in range(1, num_orders + 1):
            customer_id = random.randint(1, num_customers)
            order_total = round(random.uniform(20.0, 2000.0), 2)
            status = fake.random.choice(statuses)
            created_at = fake.date_time_between(start_date="-2y", end_date="now")
            yield (customer_id, order_total, status, created_at)
    
    return generator()
