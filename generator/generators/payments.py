import random
from faker import Faker

fake = Faker()

def generate(num_payments: int):
    """Payments generator"""
    methods = ["credit_card", "paypal", "bank_transfer", "gift_card"]
    statuses = ["pending", "completed", "failed"]

    def generator():
        for order_id in range(1, num_payments + 1):  # 1 payment per order
            amount = round(random.uniform(20.0, 2000.0), 2)
            payment_method = fake.random.choice(methods)
            status = fake.random.choice(statuses)
            created_at = fake.date_time_between(start_date="-2y", end_date="now")
            yield (order_id, amount, payment_method, status, created_at)
    
    return generator()
