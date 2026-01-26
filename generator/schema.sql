-- ===============================
-- SQL-Speak Benchmark Schema
-- Optimized for PostgreSQL 12+
-- ===============================

-- Customers
DROP TABLE IF EXISTS customers CASCADE;
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Products
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Orders
DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    order_total NUMERIC(12,2) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Order Items
DROP TABLE IF EXISTS order_items CASCADE;
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Payments
DROP TABLE IF EXISTS payments CASCADE;
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    amount NUMERIC(12,2) NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ================
-- Indexes for performance
-- ================

-- Fast lookups on foreign keys
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_payments_order ON payments(order_id);

-- Optional: Partial indexes for active orders/payments
CREATE INDEX idx_orders_active ON orders(status) WHERE status = 'active';
CREATE INDEX idx_payments_success ON payments(status) WHERE status = 'success';

-- Partitioning hint (optional for massive scale)
-- For extreme scale (100M+ rows), consider partitioning orders and order_items by created_at:
-- CREATE TABLE orders_y2026 PARTITION OF orders FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
