import typer
import psycopg2
from pathlib import Path
from .postgres import copy_rows
from .generators import customers, products, orders, payments

app = typer.Typer(help="SQL-Speak benchmark data generator")

@app.command()
def generate(
    db: str = typer.Option(..., help="PostgreSQL connection string"),
    scale: int = typer.Option(1, help="Scale factor (1 = ~10M orders)"),
):
    conn = psycopg2.connect(db)

    base_customers = 1_000_000 * scale
    base_products = 50_000
    base_orders = 10_000_000 * scale
    base_payments = base_orders

    typer.echo("🚀 Generating customers...")
    copy_rows(
        conn,
        "customers",
        ("email", "full_name", "country", "created_at"),
        customers.generate(base_customers),
    )

    typer.echo("📦 Generating products...")
    copy_rows(
        conn,
        "products",
        ("name", "category", "price", "created_at"),
        products.generate(base_products),
    )

    typer.echo("🧾 Generating orders...")
    copy_rows(
        conn,
        "orders",
        ("customer_id", "order_total", "status", "created_at"),
        orders.generate(base_orders, base_customers),
    )

    typer.echo("💳 Generating payments...")
    copy_rows(
        conn,
        "payments",
        ("order_id", "amount", "payment_method", "status", "created_at"),
        payments.generate(base_payments),
    )

    typer.echo("✅ Done!")


if __name__ == "__main__":
    app()
