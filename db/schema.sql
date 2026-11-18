-- ABC Online Shop: the schema of the running shop.
-- Tables, columns, types, NOT NULL, primary keys and foreign keys are copied from db/vp/vp_ddl.sql, the DDL that
-- Visual Paradigm generated (Tools > DB > Generate Database, SQLite) from the data model of vp/2_DataModel.vpp.
-- Added by hand (marked "-- rule"): UNIQUE, CHECK and ON DELETE CASCADE, which the data model cannot express.
-- Built by db/make_schema.py. Money is integer VND. Run with PRAGMA foreign_keys = ON.

CREATE TABLE Category (
  CategoryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  ParentId integer(10),
  Name varchar(255) NOT NULL,
  Slug varchar(255) NOT NULL UNIQUE,  -- rule
  DetailKind varchar(255) CHECK (DetailKind IN ('BOOK', 'LAPTOP', 'PHONE', 'APPAREL')),  -- rule
  FOREIGN KEY (ParentId) REFERENCES Category (CategoryId)
);

CREATE TABLE Product (
  ProductId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  CategoryId integer(10) NOT NULL,
  Sku varchar(255) NOT NULL UNIQUE,  -- rule
  Name varchar(255) NOT NULL,
  Brand varchar(255),
  Price integer(10) NOT NULL CHECK (Price > 0),  -- rule
  StockQuantity integer(10) NOT NULL CHECK (StockQuantity >= 0),  -- rule
  Description varchar(255),
  ImageFile varchar(255),
  Status varchar(255) NOT NULL CHECK (Status IN ('ACTIVE', 'HIDDEN')),  -- rule
  CreatedAt date NOT NULL,
  FOREIGN KEY (CategoryId) REFERENCES Category (CategoryId)
);

CREATE TABLE BookDetail (
  Author varchar(255) NOT NULL,
  Publisher varchar(255),
  Pages integer(10) CHECK (Pages > 0),  -- rule
  Language varchar(255),
  ProductId integer(10) NOT NULL,
  PRIMARY KEY (ProductId),
  FOREIGN KEY (ProductId) REFERENCES Product (ProductId) ON DELETE CASCADE  -- rule
);

CREATE TABLE LaptopDetail (
  Cpu varchar(255) NOT NULL,
  RamGb integer(10) NOT NULL CHECK (RamGb > 0),  -- rule
  StorageGb integer(10) NOT NULL CHECK (StorageGb > 0),  -- rule
  ScreenInch double(10) NOT NULL,
  WarrantyMonths integer(10) NOT NULL CHECK (WarrantyMonths >= 0),  -- rule
  ProductId integer(10) NOT NULL,
  PRIMARY KEY (ProductId),
  FOREIGN KEY (ProductId) REFERENCES Product (ProductId) ON DELETE CASCADE  -- rule
);

CREATE TABLE PhoneDetail (
  Os varchar(255) NOT NULL,
  StorageGb integer(10) NOT NULL CHECK (StorageGb > 0),  -- rule
  CameraMp integer(10) CHECK (CameraMp > 0),  -- rule
  ScreenInch double(10) NOT NULL,
  BatteryMah integer(10) CHECK (BatteryMah > 0),  -- rule
  WarrantyMonths integer(10) NOT NULL CHECK (WarrantyMonths >= 0),  -- rule
  ProductId integer(10) NOT NULL,
  PRIMARY KEY (ProductId),
  FOREIGN KEY (ProductId) REFERENCES Product (ProductId) ON DELETE CASCADE  -- rule
);

CREATE TABLE ApparelDetail (
  SizeLabel varchar(255) NOT NULL,
  Color varchar(255) NOT NULL,
  Material varchar(255),
  ProductId integer(10) NOT NULL,
  PRIMARY KEY (ProductId),
  FOREIGN KEY (ProductId) REFERENCES Product (ProductId) ON DELETE CASCADE  -- rule
);

CREATE TABLE Customer (
  CustomerId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  FirstName varchar(255) NOT NULL,
  MiddleName varchar(255),
  LastName varchar(255) NOT NULL,
  Email varchar(255) NOT NULL UNIQUE,  -- rule
  Phone varchar(255),
  DateOfBirth date,
  PasswordHash varchar(255) NOT NULL,
  CreatedAt date NOT NULL
);

CREATE TABLE Address (
  AddressId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  CustomerId integer(10) NOT NULL,
  RecipientName varchar(255) NOT NULL,
  Phone varchar(255) NOT NULL,
  HouseNumber varchar(255),
  Street varchar(255) NOT NULL,
  District varchar(255) NOT NULL,
  City varchar(255) NOT NULL,
  IsDefault integer(1) NOT NULL CHECK (IsDefault IN (0, 1)),  -- rule
  FOREIGN KEY (CustomerId) REFERENCES Customer (CustomerId)
);

CREATE TABLE CustomerVIP (
  VipLevel integer(10) NOT NULL CHECK (VipLevel BETWEEN 1 AND 3),  -- rule
  DiscountRate double(10) NOT NULL CHECK (DiscountRate > 0 AND DiscountRate <= 0.5),  -- rule
  RewardPoints integer(10) NOT NULL CHECK (RewardPoints >= 0),  -- rule
  CustomerId integer(10) NOT NULL,
  PRIMARY KEY (CustomerId),
  FOREIGN KEY (CustomerId) REFERENCES Customer (CustomerId)
);

CREATE TABLE CustomerNew (
  RegisteredDate date NOT NULL,
  WelcomeVoucher varchar(255),
  CustomerId integer(10) NOT NULL,
  PRIMARY KEY (CustomerId),
  FOREIGN KEY (CustomerId) REFERENCES Customer (CustomerId)
);

CREATE TABLE Staff (
  StaffId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  FullName varchar(255) NOT NULL,
  Email varchar(255) NOT NULL UNIQUE,  -- rule
  PasswordHash varchar(255) NOT NULL,
  Role varchar(255) NOT NULL CHECK (Role IN ('SALES', 'WAREHOUSE'))  -- rule
);

CREATE TABLE Cart (
  CartId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  CustomerId integer(10) NOT NULL UNIQUE,  -- rule
  CreatedAt date NOT NULL,
  UpdatedAt date NOT NULL,
  FOREIGN KEY (CustomerId) REFERENCES Customer (CustomerId)
);

CREATE TABLE CartItem (
  CartItemId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  ProductId integer(10) NOT NULL,
  CartId integer(10) NOT NULL,
  Quantity integer(10) NOT NULL CHECK (Quantity > 0),  -- rule
  CartPrice integer(10) NOT NULL CHECK (CartPrice > 0),  -- rule
  FOREIGN KEY (CartId) REFERENCES Cart (CartId) ON DELETE CASCADE,  -- rule
  FOREIGN KEY (ProductId) REFERENCES Product (ProductId),
  UNIQUE (CartId, ProductId)  -- rule
);

CREATE TABLE Orders (
  OrderId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  AddressId integer(10) NOT NULL,
  CustomerId integer(10) NOT NULL,
  OrderDate date NOT NULL,
  Status varchar(255) NOT NULL CHECK (Status IN ('PENDING_PAYMENT', 'PLACED', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED')),  -- rule
  PaymentMethod varchar(255) NOT NULL CHECK (PaymentMethod IN ('CARD', 'COD')),  -- rule
  Subtotal integer(10) NOT NULL CHECK (Subtotal > 0),  -- rule
  Discount integer(10) NOT NULL CHECK (Discount >= 0),  -- rule
  ShippingFee integer(10) NOT NULL CHECK (ShippingFee >= 0),  -- rule
  TotalAmount integer(10) NOT NULL CHECK (TotalAmount = Subtotal - Discount + ShippingFee),  -- rule
  FOREIGN KEY (CustomerId) REFERENCES Customer (CustomerId),
  FOREIGN KEY (AddressId) REFERENCES Address (AddressId)
);

CREATE TABLE OrderItem (
  OrderItemId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  ProductId integer(10) NOT NULL,
  OrderId integer(10) NOT NULL,
  ProductName varchar(255) NOT NULL,
  Quantity integer(10) NOT NULL CHECK (Quantity > 0),  -- rule
  UnitPrice integer(10) NOT NULL CHECK (UnitPrice > 0),  -- rule
  FOREIGN KEY (OrderId) REFERENCES Orders (OrderId),
  FOREIGN KEY (ProductId) REFERENCES Product (ProductId),
  UNIQUE (OrderId, ProductId)  -- rule
);

CREATE TABLE OrderEvent (
  EventId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  OrderId integer(10) NOT NULL,
  Status varchar(255) NOT NULL,
  OccurredAt date NOT NULL,
  Actor varchar(255) NOT NULL,
  Note varchar(255),
  FOREIGN KEY (OrderId) REFERENCES Orders (OrderId)
);

CREATE TABLE Payment (
  PaymentId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  OrderId integer(10) NOT NULL,
  Method varchar(255) NOT NULL CHECK (Method IN ('CARD', 'CASH')),  -- rule
  Amount integer(10) NOT NULL CHECK (Amount > 0),  -- rule
  Status varchar(255) NOT NULL CHECK (Status IN ('APPROVED', 'DECLINED', 'REFUNDED', 'COMPLETED')),  -- rule
  PaymentDate date NOT NULL,
  FOREIGN KEY (OrderId) REFERENCES Orders (OrderId)
);

CREATE TABLE PayCash (
  CashReceived integer(10) NOT NULL CHECK (CashReceived > 0),  -- rule
  ChangeAmount integer(10) NOT NULL CHECK (ChangeAmount >= 0),  -- rule
  PaymentId integer(10) NOT NULL,
  PRIMARY KEY (PaymentId),
  FOREIGN KEY (PaymentId) REFERENCES Payment (PaymentId)
);

CREATE TABLE PayCredit (
  CardHolder varchar(255) NOT NULL,
  CardLast4 varchar(255) NOT NULL,
  Expiry varchar(255) NOT NULL,
  ProviderToken varchar(255),
  PaymentId integer(10) NOT NULL,
  PRIMARY KEY (PaymentId),
  FOREIGN KEY (PaymentId) REFERENCES Payment (PaymentId)
);

CREATE TABLE Shipping (
  ShippingId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  AddressId integer(10) NOT NULL,
  OrderId integer(10) NOT NULL UNIQUE,  -- rule
  Carrier varchar(255) NOT NULL,
  TrackingNumber varchar(255) NOT NULL UNIQUE,  -- rule
  ShippingFee integer(10) NOT NULL CHECK (ShippingFee >= 0),  -- rule
  Status varchar(255) NOT NULL CHECK (Status IN ('IN_TRANSIT', 'DELIVERED')),  -- rule
  ShippedDate date NOT NULL,
  DeliveredDate date,
  FOREIGN KEY (OrderId) REFERENCES Orders (OrderId),
  FOREIGN KEY (AddressId) REFERENCES Address (AddressId)
);
