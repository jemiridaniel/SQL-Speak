import random
from faker import Faker

fake = Faker()

METHODS = ["card", "paypal", "bank_transfer"]

def generate(n):
    for _ in range(n):
        yield (
            random.randint(1, n),
            round(random.lognormvariate(4, 1), 2),
            random.choice(METHODS),
            random.choices(
                ["success", "failed"],
                weights=[0.92, 0.08],
            )[0],
            fake.date_time_between("-2y", "now"),
        )
