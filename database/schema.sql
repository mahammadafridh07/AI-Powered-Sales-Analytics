-- AI-Powered Sales Analytics & Forecasting Platform
-- Reference schema (mirrors backend/app/models/models.py).
-- In practice, SQLAlchemy's Base.metadata.create_all() creates these tables
-- automatically on backend startup. This file is provided for documentation,
-- manual PostgreSQL setup, and interview walkthroughs.

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id     SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(255),
    city            VARCHAR(100),
    state           VARCHAR(100),
    region          VARCHAR(50),
    segment         VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS ix_customers_region ON customers (region);
CREATE INDEX IF NOT EXISTS ix_customers_segment ON customers (segment);

CREATE TABLE IF NOT EXISTS products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(200) NOT NULL,
    category        VARCHAR(100),
    subcategory     VARCHAR(100),
    price           FLOAT NOT NULL,
    cost            FLOAT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_products_category ON products (category);

CREATE TABLE IF NOT EXISTS orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(customer_id),
    order_date      DATE NOT NULL,
    region          VARCHAR(50),
    salesperson     VARCHAR(120),
    order_status    VARCHAR(30) DEFAULT 'Completed'
);
CREATE INDEX IF NOT EXISTS ix_orders_customer_id ON orders (customer_id);
CREATE INDEX IF NOT EXISTS ix_orders_order_date ON orders (order_date);
CREATE INDEX IF NOT EXISTS ix_orders_region ON orders (region);
CREATE INDEX IF NOT EXISTS ix_orders_date_region_composite ON orders (order_date, region);

CREATE TABLE IF NOT EXISTS order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER REFERENCES orders(order_id),
    product_id      INTEGER REFERENCES products(product_id),
    quantity        INTEGER NOT NULL,
    unit_price      FLOAT NOT NULL,
    discount        FLOAT DEFAULT 0.0,
    revenue         FLOAT NOT NULL,
    profit          FLOAT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items (order_id);
CREATE INDEX IF NOT EXISTS ix_order_items_product_id ON order_items (product_id);
CREATE INDEX IF NOT EXISTS ix_order_items_revenue ON order_items (revenue);

CREATE TABLE IF NOT EXISTS upload_jobs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    filename        VARCHAR(255),
    status          VARCHAR(30) DEFAULT 'uploaded',
    rows_processed  INTEGER DEFAULT 0,
    error_message   VARCHAR(1000),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Example analytical queries (used conceptually by app/analytics/engine.py):

-- Revenue by category with a CTE and window function for rank:
-- WITH category_revenue AS (
--     SELECT p.category, SUM(oi.revenue) AS revenue
--     FROM order_items oi
--     JOIN products p ON p.product_id = oi.product_id
--     GROUP BY p.category
-- )
-- SELECT category, revenue, RANK() OVER (ORDER BY revenue DESC) AS rank
-- FROM category_revenue;
