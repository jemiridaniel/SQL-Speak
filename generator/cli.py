import typer
import psycopg2
from psycopg2.extras import execute_values
from .generators import customers, products, orders, order_items, payments

app = typer.Typer(help="SQL-Speak benchmark data generator (10M+ rows)")

BATCH_SIZE = 100_000  # Adjust for memory/performance tradeoff


def copy_rows(conn, table_name, columns, data_gen):
    """
    Bulk insert rows into Postgres using COPY-like efficiency via execute_values.
    Commits in batches to avoid huge transactions.
    """
    cursor = conn.cursor()
    cols_str = ", ".join(columns)

    batch = []
    for row in data_gen:
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            execute_values(cursor,
                           f"INSERT INTO {table_name} ({cols_str}) VALUES %s",
                           batch)
            conn.commit()
            batch.clear()

    if batch:
        execute_values(cursor,
                       f"INSERT INTO {table_name} ({cols_str}) VALUES %s",
                       batch)
        conn.commit()

    cursor.close()


def truncate_tables(conn):
    """
    Safely truncate all benchmark tables and reset sequences.
    """
    cursor = conn.cursor()
    cursor.execute("""
        TRUNCATE TABLE payments, order_items, orders, products, customers
        RESTART IDENTITY CASCADE;
    """)
    conn.commit()
    cursor.close()
    typer.secho("🗑️  All tables truncated successfully!", fg=typer.colors.YELLOW)


@app.command()
def generate(
    db: str = typer.Option(..., help="PostgreSQL connection string"),
    scale: int = typer.Option(1, help="Scale factor (1 = ~10M orders)"),
    truncate: bool = typer.Option(False, help="Truncate existing tables before generating"),
):
    """
    Generate benchmark data for SQL-Speak:
    customers, products, orders, order_items, payments
    """

    conn = psycopg2.connect(db)

    if truncate:
        truncate_tables(conn)

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

    typer.echo("📦 Generating order_items...")
    copy_rows(
        conn,
        "order_items",
        ("order_id", "product_id", "quantity", "price", "created_at"),
        order_items.generate(base_orders, base_products),
    )

    typer.echo("💳 Generating payments...")
    copy_rows(
        conn,
        "payments",
        ("order_id", "amount", "payment_method", "status", "created_at"),
        payments.generate(base_payments),
    )

    typer.echo("✅ Done generating all benchmark data!")
    conn.close()


if __name__ == "__main__":
    app()
# To run the CLI, use: python -m generator.cli generate --db "your_connection_string" --scale 1 --truncate