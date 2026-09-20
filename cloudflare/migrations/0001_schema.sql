-- Generated from the SIF Mobile & Computer SQLite schema.
PRAGMA foreign_keys=ON;

CREATE TABLE account_payments (
	id INTEGER NOT NULL, 
	party_type VARCHAR(20) NOT NULL, 
	party_id INTEGER NOT NULL, 
	amount NUMERIC(14, 2) NOT NULL, 
	payment_method VARCHAR(30) NOT NULL, 
	notes VARCHAR(500), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	image_url TEXT, 
	active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE customers (
	id INTEGER NOT NULL, 
	code VARCHAR(40) NOT NULL, 
	name VARCHAR(180) NOT NULL, 
	phone VARCHAR(50), 
	address VARCHAR(250), 
	balance NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE devices (
	id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	imei1 VARCHAR(80), 
	imei2 VARCHAR(80), 
	serial_number VARCHAR(120), 
	color VARCHAR(50), 
	storage VARCHAR(50), 
	status VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	UNIQUE (imei1), 
	UNIQUE (imei2), 
	UNIQUE (serial_number)
);

CREATE TABLE expenses (
	id INTEGER NOT NULL, 
	description VARCHAR(250) NOT NULL, 
	amount NUMERIC(14, 2) NOT NULL, 
	created_at DATETIME NOT NULL, category VARCHAR(100) DEFAULT 'General', payment_method VARCHAR(30) DEFAULT 'cash', notes VARCHAR(500), 
	PRIMARY KEY (id)
);

CREATE TABLE product_types (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE products (
	id INTEGER NOT NULL, 
	sku VARCHAR(80) NOT NULL, 
	barcode VARCHAR(120), 
	name VARCHAR(200) NOT NULL, 
	category VARCHAR(80) NOT NULL, 
	product_type VARCHAR(40) NOT NULL, 
	cost NUMERIC(14, 2) NOT NULL, 
	sale_price NUMERIC(14, 2) NOT NULL, 
	quantity INTEGER NOT NULL, 
	reorder_level INTEGER NOT NULL, 
	imei_required BOOLEAN NOT NULL, 
	serial_required BOOLEAN NOT NULL, 
	warranty_months INTEGER NOT NULL, 
	image_url VARCHAR(500), 
	wholesale_price NUMERIC(14, 2) NOT NULL, 
	vip_price NUMERIC(14, 2) NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (barcode)
);

CREATE TABLE purchase_items (
	id INTEGER NOT NULL, 
	purchase_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_cost NUMERIC(14, 2) NOT NULL, 
	total NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(purchase_id) REFERENCES purchases (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE purchase_return_items (
	id INTEGER NOT NULL, 
	return_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_cost NUMERIC(14, 2) NOT NULL, 
	total NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(return_id) REFERENCES purchase_returns (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE purchase_returns (
	id INTEGER NOT NULL, 
	return_no VARCHAR(50) NOT NULL, 
	purchase_id INTEGER NOT NULL, 
	supplier_id INTEGER, 
	total NUMERIC(14, 2) NOT NULL, 
	payment_method VARCHAR(30) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(purchase_id) REFERENCES purchases (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
);

CREATE TABLE purchases (
	id INTEGER NOT NULL, 
	invoice_no VARCHAR(50) NOT NULL, 
	supplier_id INTEGER, 
	subtotal NUMERIC(14, 2) NOT NULL, 
	vat_rate NUMERIC(5, 2) NOT NULL, 
	vat_enabled BOOLEAN NOT NULL, 
	total NUMERIC(14, 2) NOT NULL, 
	payment_method VARCHAR(30) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
);

CREATE TABLE repairs (
	id INTEGER NOT NULL, 
	ticket_no VARCHAR(50) NOT NULL, 
	customer_id INTEGER, 
	device_name VARCHAR(180) NOT NULL, 
	imei_or_serial VARCHAR(120), 
	problem VARCHAR(500) NOT NULL, 
	status VARCHAR(40) NOT NULL, 
	estimated_cost NUMERIC(14, 2) NOT NULL, 
	created_at DATETIME NOT NULL, sales_price NUMERIC(14,2) DEFAULT 0, customer_phone VARCHAR(50), customer_address VARCHAR(250), technician VARCHAR(120), warranty_days INTEGER DEFAULT 0, notes VARCHAR(1000), 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE TABLE sale_items (
	id INTEGER NOT NULL, 
	sale_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price NUMERIC(14, 2) NOT NULL, 
	total NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE sales (
	id INTEGER NOT NULL, 
	invoice_no VARCHAR(50) NOT NULL, 
	customer_id INTEGER, 
	subtotal NUMERIC(14, 2) NOT NULL, 
	discount NUMERIC(14, 2) NOT NULL, 
	total NUMERIC(14, 2) NOT NULL, 
	payment_method VARCHAR(30) NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	vat_enabled BOOLEAN NOT NULL, 
	vat_rate NUMERIC(5, 2) NOT NULL, 
	vat_amount NUMERIC(14, 2) NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE TABLE sales_return_items (
	id INTEGER NOT NULL, 
	return_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price NUMERIC(14, 2) NOT NULL, 
	total NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(return_id) REFERENCES sales_returns (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE sales_returns (
	id INTEGER NOT NULL, 
	return_no VARCHAR(50) NOT NULL, 
	sale_id INTEGER NOT NULL, 
	customer_id INTEGER, 
	total NUMERIC(14, 2) NOT NULL, 
	payment_method VARCHAR(30) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
);

CREATE TABLE settings (
	id INTEGER NOT NULL, 
	"key" VARCHAR(80) NOT NULL, 
	value VARCHAR(500) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE suppliers (
	id INTEGER NOT NULL, 
	code VARCHAR(40) NOT NULL, 
	name VARCHAR(180) NOT NULL, 
	phone VARCHAR(50), 
	address VARCHAR(250), 
	balance NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(40) NOT NULL, 
	active BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_categories_name ON categories (name);

CREATE UNIQUE INDEX ix_customers_code ON customers (code);

CREATE INDEX ix_customers_name ON customers (name);

CREATE UNIQUE INDEX ix_product_types_code ON product_types (code);

CREATE UNIQUE INDEX ix_product_types_name ON product_types (name);

CREATE INDEX ix_products_name ON products (name);

CREATE UNIQUE INDEX ix_products_sku ON products (sku);

CREATE UNIQUE INDEX ix_purchase_returns_return_no ON purchase_returns (return_no);

CREATE UNIQUE INDEX ix_purchases_invoice_no ON purchases (invoice_no);

CREATE UNIQUE INDEX ix_repairs_ticket_no ON repairs (ticket_no);

CREATE UNIQUE INDEX ix_sales_invoice_no ON sales (invoice_no);

CREATE UNIQUE INDEX ix_sales_returns_return_no ON sales_returns (return_no);

CREATE UNIQUE INDEX ix_settings_key ON settings ("key");

CREATE UNIQUE INDEX ix_suppliers_code ON suppliers (code);

CREATE INDEX ix_suppliers_name ON suppliers (name);

CREATE UNIQUE INDEX ix_users_username ON users (username);

