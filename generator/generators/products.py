from faker import Faker

fake = Faker()

def generate(num_products: int):
    """Unique products generator"""
    categories = ["Electronics", "Books", "Clothing", "Home", "Toys", "Sports"]
    
    def generator():
        for i in range(1, num_products + 1):
            name = f"{fake.word().capitalize()} Product {i}"  # unique
            category = fake.random.choice(categories)
            price = round(fake.random_number(digits=3) + fake.random.random(), 2)
            created_at = fake.date_time_between(start_date="-3y", end_date="now")
            yield (name, category, price, created_at)
    
    return generator()
