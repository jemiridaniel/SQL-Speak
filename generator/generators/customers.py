from faker import Faker
from datetime import datetime

fake = Faker()

def generate(n):
    for _ in range(n):
        yield (
            fake.email(),
            fake.name(),
            fake.country(),
            fake.date_time_between("-5y", "now"),
        )
