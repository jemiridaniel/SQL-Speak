import random
from faker import Faker

fake = Faker()

CATEGORIES = ["electronics", "fashion", "home", "sports", "books"]

def generate(n):
    for _ in range(n):
        yield (
            fake.word().title(),
            random.choice(CATEGORIES),
            round(random.uniform(5, 500), 2),
            fake.date_time_between("-3y", "now"),
        )
