CREATE TABLE category (
  category_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  parent_id   integer(10), 
  name        varchar(60) NOT NULL, 
  slug        varchar(60) NOT NULL UNIQUE, 
  detail_kind varchar(10) CHECK(detail_kind IN ('BOOK', 'LAPTOP', 'PHONE', 'APPAREL')));
CREATE TABLE product (
  product_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  category_id    integer(10) NOT NULL, 
  sku            varchar(20) NOT NULL UNIQUE, 
  name           varchar(120) NOT NULL, 
  brand          varchar(60), 
  price          integer(10) NOT NULL CHECK(price > 0), 
  stock_quantity integer(10) NOT NULL CHECK(stock_quantity >= 0), 
  description    varchar(1000), 
  image_file     varchar(120), 
  status         varchar(10) NOT NULL CHECK(status IN ('ACTIVE', 'HIDDEN')), 
  created_at     timestamp NOT NULL);
CREATE TABLE book_detail (
  product_id integer(10) NOT NULL, 
  author     varchar(100) NOT NULL, 
  publisher  varchar(100), 
  pages      integer(10) CHECK(pages > 0), 
  language   varchar(30), 
  PRIMARY KEY (product_id));
CREATE TABLE laptop_detail (
  product_id      integer(10) NOT NULL, 
  cpu             varchar(60) NOT NULL, 
  ram_gb          integer(10) NOT NULL CHECK(ram_gb > 0), 
  storage_gb      integer(10) NOT NULL CHECK(storage_gb > 0), 
  screen_inch     decimal(3, 1) NOT NULL, 
  warranty_months integer(10) NOT NULL CHECK(warranty_months >= 0), 
  PRIMARY KEY (product_id));
CREATE TABLE phone_detail (
  product_id      integer(10) NOT NULL, 
  os              varchar(30) NOT NULL, 
  storage_gb      integer(10) NOT NULL CHECK(storage_gb > 0), 
  camera_mp       integer(10) CHECK(camera_mp > 0), 
  screen_inch     decimal(3, 1) NOT NULL, 
  battery_mah     integer(10) CHECK(battery_mah > 0), 
  warranty_months integer(10) NOT NULL CHECK(warranty_months >= 0), 
  PRIMARY KEY (product_id));
CREATE TABLE apparel_detail (
  product_id integer(10) NOT NULL, 
  size_label varchar(10) NOT NULL, 
  color      varchar(30) NOT NULL, 
  material   varchar(60), 
  PRIMARY KEY (product_id));
CREATE TABLE customer (
  customer_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  first_name    varchar(50) NOT NULL, 
  middle_name   varchar(50), 
  last_name     varchar(50) NOT NULL, 
  email         varchar(100) NOT NULL UNIQUE, 
  phone         varchar(20), 
  date_of_birth date, 
  password_hash varchar(120) NOT NULL, 
  created_at    timestamp NOT NULL);
CREATE TABLE address (
  address_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  customer_id    integer(10) NOT NULL, 
  recipient_name varchar(100) NOT NULL, 
  phone          varchar(20) NOT NULL, 
  house_number   varchar(20), 
  street         varchar(100) NOT NULL, 
  district       varchar(50) NOT NULL, 
  city           varchar(50) NOT NULL, 
  is_default     integer(10) NOT NULL CHECK(is_default IN (0, 1)));
CREATE TABLE customer_vip (
  customer_id   integer(10) NOT NULL, 
  vip_level     integer(10) NOT NULL CHECK(vip_level BETWEEN 1 AND 3), 
  discount_rate decimal(4, 2) NOT NULL CHECK(discount_rate > 0 AND discount_rate <= 0.5), 
  reward_points integer(10) NOT NULL CHECK(reward_points >= 0), 
  PRIMARY KEY (customer_id));
CREATE TABLE customer_new (
  customer_id     integer(10) NOT NULL, 
  registered_date date NOT NULL, 
  welcome_voucher varchar(20), 
  PRIMARY KEY (customer_id));
CREATE TABLE staff (
  staff_id      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  full_name     varchar(100) NOT NULL, 
  email         varchar(100) NOT NULL UNIQUE, 
  password_hash varchar(120) NOT NULL, 
  role          varchar(10) NOT NULL CHECK(role IN ('SALES', 'WAREHOUSE')));
CREATE TABLE cart (
  cart_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  customer_id integer(10) NOT NULL UNIQUE, 
  created_at  timestamp NOT NULL, 
  updated_at  timestamp NOT NULL);
CREATE TABLE cart_item (
  cart_item_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  cart_id      integer(10) NOT NULL, 
  product_id   integer(10) NOT NULL, 
  quantity     integer(10) NOT NULL CHECK(quantity > 0), 
  cart_price   integer(10) NOT NULL CHECK(cart_price > 0));
CREATE TABLE customer_order (
  order_id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  customer_id    integer(10) NOT NULL, 
  address_id     integer(10) NOT NULL, 
  order_date     timestamp NOT NULL, 
  status         varchar(16) NOT NULL CHECK(status IN ('PENDING_PAYMENT', 'PLACED', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED')), 
  payment_method varchar(4) NOT NULL CHECK(payment_method IN ('CARD', 'COD')), 
  subtotal       integer(10) NOT NULL CHECK(subtotal > 0), 
  discount       integer(10) NOT NULL CHECK(discount >= 0), 
  shipping_fee   integer(10) NOT NULL CHECK(shipping_fee >= 0), 
  total_amount   integer(10) NOT NULL CHECK(total_amount = subtotal - discount + shipping_fee));
CREATE TABLE order_item (
  order_item_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  order_id      integer(10) NOT NULL, 
  product_id    integer(10) NOT NULL, 
  product_name  varchar(120) NOT NULL, 
  quantity      integer(10) NOT NULL CHECK(quantity > 0), 
  unit_price    integer(10) NOT NULL CHECK(unit_price > 0));
CREATE TABLE order_event (
  event_id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  order_id    integer(10) NOT NULL, 
  status      varchar(16) NOT NULL, 
  occurred_at timestamp NOT NULL, 
  actor       varchar(60) NOT NULL, 
  note        varchar(200));
CREATE TABLE payment (
  payment_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  order_id     integer(10) NOT NULL, 
  method       varchar(4) NOT NULL CHECK(method IN ('CARD', 'CASH')), 
  amount       integer(10) NOT NULL CHECK(amount > 0), 
  status       varchar(10) NOT NULL CHECK(status IN ('APPROVED', 'DECLINED', 'REFUNDED', 'COMPLETED')), 
  payment_date timestamp NOT NULL);
CREATE TABLE pay_cash (
  payment_id    integer(10) NOT NULL, 
  cash_received integer(10) NOT NULL CHECK(cash_received > 0), 
  change_amount integer(10) NOT NULL CHECK(change_amount >= 0), 
  PRIMARY KEY (payment_id));
CREATE TABLE pay_credit (
  payment_id     integer(10) NOT NULL, 
  card_holder    varchar(100) NOT NULL, 
  card_last4     char(4) NOT NULL, 
  expiry         varchar(5) NOT NULL, 
  provider_token varchar(64), 
  PRIMARY KEY (payment_id));
CREATE TABLE shipping (
  shipping_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
  order_id        integer(10) NOT NULL UNIQUE, 
  address_id      integer(10) NOT NULL, 
  carrier         varchar(50) NOT NULL, 
  tracking_number varchar(30) NOT NULL UNIQUE, 
  shipping_fee    integer(10) NOT NULL CHECK(shipping_fee >= 0), 
  status          varchar(12) NOT NULL CHECK(status IN ('IN_TRANSIT', 'DELIVERED')), 
  shipped_date    timestamp NOT NULL, 
  delivered_date  timestamp);
CREATE UNIQUE INDEX uq_cart_item_product_id 
  ON cart_item (cart_id, product_id);
CREATE UNIQUE INDEX uq_order_item_product_id 
  ON order_item (order_id, product_id);
