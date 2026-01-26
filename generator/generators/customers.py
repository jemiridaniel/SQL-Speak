from faker import Faker

fake = Faker()

def generate(num_customers: int):
    """
    Generate unique customers with email, full_name, country, created_at.
    Uses deterministic unique email to avoid duplicate key errors.
    """
    def generator():
        for i in range(1, num_customers + 1):
            # Make email unique using the index
            email = f"{fake.first_name().lower()}.{fake.last_name().lower()}{i}@example.com"
            full_name = fake.name()
            country = fake.country()
            created_at = fake.date_time_between(start_date="-5y", end_date="now")
            yield (email, full_name, country, created_at)

    return generator()
