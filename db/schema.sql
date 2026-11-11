-- ABC Online Shop, physical data model (revised design, docs/DESIGN.md section 2).
-- 20 tables. Money is integer VND. Run with PRAGMA foreign_keys = ON.

CREATE TABLE category (
  category_id INTEGER NOT NULL,
  parent_id INTEGER,
  name VARCHAR(60) NOT NULL,
  slug VARCHAR(60) NOT NULL UNIQUE,
  detail_kind VARCHAR(10) CHECK (detail_kind IN ('BOOK', 'LAPTOP', 'PHONE', 'APPAREL')),
  PRIMARY KEY (category_id),
  FOREIGN KEY (parent_id) REFERENCES category (category_id)
);

CREATE TABLE product (
  product_id INTEGER NOT NULL,
  category_id INTEGER NOT NULL,
  sku VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(120) NOT NULL,
  brand VARCHAR(60),
  price INTEGER NOT NULL CHECK (price > 0),
  stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
  description VARCHAR(1000),
  image_file VARCHAR(120),
  status VARCHAR(10) NOT NULL CHECK (status IN ('ACTIVE', 'HIDDEN')),
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (product_id),
  FOREIGN KEY (category_id) REFERENCES category (category_id)
);

CREATE TABLE book_detail (
  product_id INTEGER NOT NULL,
  author VARCHAR(100) NOT NULL,
  publisher VARCHAR(100),
  pages INTEGER CHECK (pages > 0),
  language VARCHAR(30),
  PRIMARY KEY (product_id),
  FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
);

CREATE TABLE laptop_detail (
  product_id INTEGER NOT NULL,
  cpu VARCHAR(60) NOT NULL,
  ram_gb INTEGER NOT NULL CHECK (ram_gb > 0),
  storage_gb INTEGER NOT NULL CHECK (storage_gb > 0),
  screen_inch DECIMAL(3,1) NOT NULL,
  warranty_months INTEGER NOT NULL CHECK (warranty_months >= 0),
  PRIMARY KEY (product_id),
  FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
);

CREATE TABLE phone_detail (
  product_id INTEGER NOT NULL,
  os VARCHAR(30) NOT NULL,
  storage_gb INTEGER NOT NULL CHECK (storage_gb > 0),
  camera_mp INTEGER CHECK (camera_mp > 0),
  screen_inch DECIMAL(3,1) NOT NULL,
  battery_mah INTEGER CHECK (battery_mah > 0),
  warranty_months INTEGER NOT NULL CHECK (warranty_months >= 0),
  PRIMARY KEY (product_id),
  FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
);

CREATE TABLE apparel_detail (
  product_id INTEGER NOT NULL,
  size_label VARCHAR(10) NOT NULL,
  color VARCHAR(30) NOT NULL,
  material VARCHAR(60),
  PRIMARY KEY (product_id),
  FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE
);

CREATE TABLE customer (
  customer_id INTEGER NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  middle_name VARCHAR(50),
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20),
  date_of_birth DATE,
  password_hash VARCHAR(120) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  PRIMARY KEY (customer_id)
);

CREATE TABLE address (
  address_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  recipient_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  house_number VARCHAR(20),
  street VARCHAR(100) NOT NULL,
  district VARCHAR(50) NOT NULL,
  city VARCHAR(50) NOT NULL,
  is_default INTEGER NOT NULL CHECK (is_default IN (0, 1)),
  PRIMARY KEY (address_id),
  FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

CREATE TABLE customer_vip (
  customer_id INTEGER NOT NULL,
  vip_level INTEGER NOT NULL CHECK (vip_level BETWEEN 1 AND 3),
  discount_rate DECIMAL(4,2) NOT NULL CHECK (discount_rate > 0 AND discount_rate <= 0.5),
  reward_points INTEGER NOT NULL CHECK (reward_points >= 0),
  PRIMARY KEY (customer_id),
  FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

CREATE TABLE customer_new (
  customer_id INTEGER NOT NULL,
  registered_date DATE NOT NULL,
  welcome_voucher VARCHAR(20),
  PRIMARY KEY (customer_id),
  FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

CREATE TABLE staff (
  staff_id INTEGER NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(120) NOT NULL,
  role VARCHAR(10) NOT NULL CHECK (role IN ('SALES', 'WAREHOUSE')),
  PRIMARY KEY (staff_id)
);

CREATE TABLE cart (
  cart_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (cart_id),
  FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

CREATE TABLE cart_item (
  cart_item_id INTEGER NOT NULL,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  cart_price INTEGER NOT NULL CHECK (cart_price > 0),
  PRIMARY KEY (cart_item_id),
  UNIQUE (cart_id, product_id),
  FOREIGN KEY (cart_id) REFERENCES cart (cart_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES product (product_id)
);

CREATE TABLE customer_order (
  order_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  address_id INTEGER NOT NULL,
  order_date TIMESTAMP NOT NULL,
  status VARCHAR(16) NOT NULL CHECK (status IN ('PENDING_PAYMENT', 'PLACED', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED')),
  payment_method VARCHAR(4) NOT NULL CHECK (payment_method IN ('CARD', 'COD')),
  subtotal INTEGER NOT NULL CHECK (subtotal > 0),
  discount INTEGER NOT NULL CHECK (discount >= 0),
  shipping_fee INTEGER NOT NULL CHECK (shipping_fee >= 0),
  total_amount INTEGER NOT NULL CHECK (total_amount = subtotal - discount + shipping_fee),
  PRIMARY KEY (order_id),
  FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
  FOREIGN KEY (address_id) REFERENCES address (address_id)
);

CREATE TABLE order_item (
  order_item_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  product_name VARCHAR(120) NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price INTEGER NOT NULL CHECK (unit_price > 0),
  PRIMARY KEY (order_item_id),
  UNIQUE (order_id, product_id),
  FOREIGN KEY (order_id) REFERENCES customer_order (order_id),
  FOREIGN KEY (product_id) REFERENCES product (product_id)
);

CREATE TABLE order_event (
  event_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  status VARCHAR(16) NOT NULL,
  occurred_at TIMESTAMP NOT NULL,
  actor VARCHAR(60) NOT NULL,
  note VARCHAR(200),
  PRIMARY KEY (event_id),
  FOREIGN KEY (order_id) REFERENCES customer_order (order_id)
);

CREATE TABLE payment (
  payment_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  method VARCHAR(4) NOT NULL CHECK (method IN ('CARD', 'CASH')),
  amount INTEGER NOT NULL CHECK (amount > 0),
  status VARCHAR(10) NOT NULL CHECK (status IN ('APPROVED', 'DECLINED', 'REFUNDED', 'COMPLETED')),
  payment_date TIMESTAMP NOT NULL,
  PRIMARY KEY (payment_id),
  FOREIGN KEY (order_id) REFERENCES customer_order (order_id)
);

CREATE TABLE pay_cash (
  payment_id INTEGER NOT NULL,
  cash_received INTEGER NOT NULL CHECK (cash_received > 0),
  change_amount INTEGER NOT NULL CHECK (change_amount >= 0),
  PRIMARY KEY (payment_id),
  FOREIGN KEY (payment_id) REFERENCES payment (payment_id)
);

CREATE TABLE pay_credit (
  payment_id INTEGER NOT NULL,
  card_holder VARCHAR(100) NOT NULL,
  card_last4 CHAR(4) NOT NULL,
  expiry VARCHAR(5) NOT NULL,
  provider_token VARCHAR(64),
  PRIMARY KEY (payment_id),
  FOREIGN KEY (payment_id) REFERENCES payment (payment_id)
);

CREATE TABLE shipping (
  shipping_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL UNIQUE,
  address_id INTEGER NOT NULL,
  carrier VARCHAR(50) NOT NULL,
  tracking_number VARCHAR(30) NOT NULL UNIQUE,
  shipping_fee INTEGER NOT NULL CHECK (shipping_fee >= 0),
  status VARCHAR(12) NOT NULL CHECK (status IN ('IN_TRANSIT', 'DELIVERED')),
  shipped_date TIMESTAMP NOT NULL,
  delivered_date TIMESTAMP,
  PRIMARY KEY (shipping_id),
  FOREIGN KEY (order_id) REFERENCES customer_order (order_id),
  FOREIGN KEY (address_id) REFERENCES address (address_id)
);
