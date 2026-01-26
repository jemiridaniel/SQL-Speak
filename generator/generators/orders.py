import random
from faker import Faker

fake = Faker()

def generate(n, customer_count):
    for _ in range(n):
        yield (
            random.randint(1, customer_count),
            round(random.lognormvariate(4, 1), 2),
            random.choices(
                ["completed", "cancelled", "refunded"],
                weights=[0.85, 0.10, 0.05],
            )[0],
            fake.date_time_between("-2y", "now"),
        )
