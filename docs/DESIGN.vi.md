# DESIGN: mô hình dữ liệu và thiết kế lớp của phần đã cài đặt

Đầu vào: SPEC.md, biểu đồ lớp phân tích (A10 trong `vp/1_Analysis.vpp`, Hình 2.1 của tiểu luận) và góp ý của giảng
viên về Product. Đầu ra: mô hình dữ liệu của `vp/2_DataModel.vpp`, `db/schema.sql` và các package dưới
`app/src/main/java/vn/ptit/ecom`, được mô hình hoá trong `vp/3_Design.vpp`.

## 1. Lớp và quan hệ (mô hình phân tích A10)

Category (cây) 1 - 0..* Product; BookDetail, LaptopDetail, PhoneDetail, ApparelDetail là lớp con của Product (loại chi
tiết của danh mục cho biết là lớp nào); Customer 1 - 0..* Address; Customer 1 - 0..1 Cart; Cart 1 - 0..* CartItem; CartItem 0..* - 1
Product; Customer 1 - 0..* Order; Order 1 - 1..* OrderItem; OrderItem 0..* - 1 Product; Order 1 - 0..* Payment
(Cash hoặc Credit); Order 1 - 0..1 Shipping; Shipping 0..* - 1 Address; Order 1 - 1..* OrderEvent; Customer có thể là VIP 0..1,
New 0..1; Staff (Sales hoặc Warehouse).

## 2. Từ mô hình phân tích đến cơ sở dữ liệu

Mô hình dữ liệu không vẽ tay. Trong `vp/2_DataModel.vpp`, các lớp của A10 trở thành sơ đồ lớp D1: mỗi thuộc tính có
kiểu và multiplicity (1 = NOT NULL, 0..1 = NULL), mỗi lớp có thuộc tính định danh và stereotype «ORM Persistable», mỗi
đầu liên kết có role name và multiplicity, ba quan hệ khái quát hoá dùng chiến lược kế thừa Table per subclass. Lệnh
Synchronize to Entity Relationship Diagram của VP sinh ra ERD D2 (20 bảng, 122 cột, 22 khoá ngoại); chỉnh tay chỉ có
tên cột khoá ngoại (`CategoryCategoryId` thành `CategoryId`, khoá cha của danh mục thành `ParentId`), đổi bảng `Order`
thành `Orders` (ORDER là từ khoá SQL) và bố cục. Tools > DB > Generate Database (SQLite) ghi ra `db/vp/vp_ddl.sql`.
`db/make_schema.py` chép mọi câu CREATE TABLE của DDL đó vào `db/schema.sql` và thêm các luật mà mô hình dữ liệu không
chứa được (34 CHECK, 9 UNIQUE, 5 ON DELETE CASCADE, mỗi luật đánh dấu `-- rule`); `db/compare_schema.py` kiểm tra hai bên
vẫn cùng bảng, cột, kiểu, NOT NULL, khoá và khoá ngoại.

| Lớp phân tích (A10) | Bảng sinh ra (D2) | Luật thêm trong schema.sql | Lý do |
|---|---|---|---|
| Category (cây) | `Category`, `ParentId` trỏ về chính nó | UNIQUE `Slug`; CHECK `DetailKind` thuộc BOOK, LAPTOP, PHONE, APPAREL | loại chi tiết cho biết sản phẩm của danh mục thuộc lớp con nào |
| Product và các lớp con BookDetail, LaptopDetail, PhoneDetail, ApparelDetail | `Product` và mỗi lớp con một bảng; `ProductId` vừa là khoá chính vừa là khoá ngoại tới `Product` | UNIQUE `Sku`; CHECK `Price > 0`, `StockQuantity >= 0`, `Status` thuộc ACTIVE, HIDDEN; ON DELETE CASCADE ở bốn bảng chi tiết | góp ý của giảng viên; Table per subclass giữ một khoá `ProductId` cho CartItem và OrderItem |
| Customer và các lớp con CustomerVIP, CustomerNew | `Customer`, `CustomerVIP`, `CustomerNew`, PK = FK | UNIQUE `Email`; CHECK `DiscountRate` lớn hơn 0 và không quá 0.5 | Table per subclass |
| Address | `Address` có người nhận và số điện thoại | CHECK `IsDefault` thuộc 0, 1 | giao hàng cần có người nhận |
| Cart, CartItem | `Cart`, `CartItem` | UNIQUE `Cart.CustomerId`; UNIQUE (`CartId`, `ProductId`); CHECK `Quantity > 0`; ON DELETE CASCADE từ `Cart` | BR02 |
| Order | `Orders` với trạng thái, phương thức thanh toán, tạm tính, giảm giá, phí vận chuyển, tổng | CHECK `TotalAmount = Subtotal - Discount + ShippingFee`; CHECK bảy trạng thái | BR04 được lưu thành dữ kiện có kiểm tra, BR09 |
| OrderItem | `OrderItem` với `UnitPrice` và bản chụp `ProductName` | UNIQUE (`OrderId`, `ProductId`); CHECK `Quantity > 0`, `UnitPrice > 0` | BR03, ngoại lệ 3NF được giải thích trong tiểu luận |
| OrderEvent | `OrderEvent` | | lịch sử mà UC09 hiển thị |
| Payment và các lớp con PayCash, PayCredit | `Payment`, `PayCash`, `PayCredit` (bốn số cuối, ngày hết hạn, token của nhà cung cấp) | CHECK `Method`, `Amount > 0`, `Status` | BR07: không có cột cho số thẻ |
| Shipping | `Shipping` | UNIQUE `OrderId`, UNIQUE `TrackingNumber` | BR10 |
| Staff | `Staff` có vai trò | UNIQUE `Email`; CHECK `Role` thuộc SALES, WAREHOUSE | tác nhân của UC14, UC15 cần tài khoản (UC02), BR13 |

Chuẩn hóa: 1NF (các cột nguyên tử, nhóm lặp tách thành bảng riêng), 2NF (khóa một cột; các khóa UNIQUE gồm nhiều cột
không phải khóa chính), 3NF trừ hai giá trị lịch sử có chủ ý (`OrderItem.UnitPrice`,
`OrderItem.ProductName`) và các tổng tiền được lưu của đơn hàng, vốn bằng giá trị tính toán lúc đặt hàng và được
bảo vệ bởi một ràng buộc CHECK.

## 3. Package và lớp (ba tầng)

Các lớp thiết kế trong VP (biểu đồ G1 đến G4b và G8, thư mục "5 Design" của `vp/3_Design.vpp`) và mã nguồn có cùng
package, lớp, thuộc tính và thao tác; `tests/design_vs_code.py` kiểm tra điều này với các lớp đã biên dịch và các view JS
(80 lớp: 72 lớp Java với 169 thuộc tính và 134 thao tác, 8 lớp view với 25 thao tác, và 48 lời gọi trong
các biểu đồ tuần tự thiết kế G5, G6, G7 và G9), đồng thời kiểm tra rằng không file nào của package `ai` import phần khác của ứng dụng.
`tests/vpgen_vs_code.py` đi từ phía ngược lại: 80 file mà Instant Generator của VP ghi ra từ cùng mô hình
(`docs/evidence/vp_codegen_v5`) đều phải có trong mã nguồn với cùng các field và phương thức (72 lớp, 173 field,
157 phương thức, và 25 thao tác của 8 lớp view).

| Tầng (G1) | Package | Các lớp | Trách nhiệm |
|---|---|---|---|
| Presentation (trình bày) | `view` (trình duyệt, ES modules) | CustomerForm, ProductForm, CartForm, OrderForm, PaymentForm, StaffOrderForm, StockForm, SearchForm | mỗi nhóm màn hình một lớp; `show…` hiển thị, `submit…` gửi dữ liệu người dùng nhập tới controller của nó |
| Presentation | `controller` | AuthController, ProductController, CartController, OrderController, PaymentController, ShippingController, SearchController, CurrentUser | chỉ xử lý HTTP: đọc người dùng từ session (BR08, BR13), phân tích và kiểm tra đầu vào, gọi một thao tác của service, trả về một view record |
| Business logic (logic nghiệp vụ) | `service` | AuthService, CatalogService, CartService, OrderService, PaymentService, ShippingService, SearchService, NotFound | mỗi bước của use case là một thao tác; sở hữu giao dịch (`Database.inTransaction`) và gọi các quy tắc của model cùng các DAO |
| Business logic | `model.product`, `model.customer`, `model.cart`, `model.order`, `model` | Category, Product và các lớp con BookDetail, LaptopDetail, PhoneDetail, ApparelDetail, DetailKind; Customer, CustomerVIP, CustomerNew, FullName, Address, Account, Role; Cart, CartItem, CartIssue; Order, Totals, OrderItem, OrderEvent, OrderStatus, PaymentMethod, Payment, PayCredit, PayCash, Shipping; RuleViolation | quy tắc miền: Cart (BR01 đến BR03), Order.place và Totals (BR04), bảng chuyển trạng thái của OrderStatus (BR09) |
| Data access (truy cập dữ liệu) | `dao` | Database, Daos, Work, DataAccessError, ProductDAO, CustomerDAO, StaffDAO, CartDAO, OrderDAO, PaymentDAO, ShippingDAO và mỗi lớp một `…DAOImpl` | JDBC trên file SQLite; mỗi `…DAOImpl` giữ `connection` của đơn vị công việc (unit of work); không chứa quy tắc nghiệp vụ |
| Business logic | `ai` (G8) | QueryInterpreter, SearchQuery, ProductIndex, ImageIndex, Document, Hit | tìm kiếm AI: đưa tài liệu vào, nhận ra các kết quả đã xếp hạng kèm lý do; không import gì khác của ứng dụng, nên SearchService là nơi duy nhất biết đến sản phẩm (tiểu luận chương 3, SPEC mục 6) |
| Data access | `integration` | CardProvider, SimulatedCardProvider, CardData, Result | cổng kết nối tới nhà cung cấp thanh toán (mô phỏng: thẻ kết thúc bằng 0002 bị từ chối) |

Các phụ thuộc chỉ hướng xuống: view → controller (HTTP, JSON) → service → dao → SQLite; service → integration →
nhà cung cấp thanh toán; controller, service và dao dùng model. Controller không bao giờ gọi DAO và không có SQL nào nằm phía trên
các DAO. Trước khi tầng service được đưa vào (commit feab5f3), các controller tự mở giao dịch;
việc chuyển đó là câu trả lời cho câu hỏi "logic nghiệp vụ nằm ở đâu?" khi bảo vệ.

## 4. Tương tác chính: Place Order (đặt hàng) bằng thẻ (biểu đồ tuần tự thiết kế G6 và G7)

1. `OrderForm.submitOrder(addressId, paymentMethod, expectedTotal)` → `POST /api/orders` → `OrderController.placeOrder(req, session)`.
2. Controller lấy id khách hàng từ session (BR08) và gọi `OrderService.placeOrder(customerId, addressId, method, expectedTotal)`.
3. Service chạy một giao dịch, `Database.inTransaction(work)`; trong đó: `CustomerDAO.findById`, `CustomerDAO.address` (BR06), `CartDAO.findOrCreate`, `Order.place(customer, cart, address, method, now)`, hàm này kiểm tra giỏ hàng (UC21, BR03) và tính các tổng tiền (BR04).
4. Tổng tiền thay đổi so với `expectedTotal` → `RuleViolation BR03`, giao dịch được rollback và khách hàng xác nhận lại.
5. `ProductDAO.reserveStock(productId, quantity)` cho mỗi dòng: `UPDATE Product SET StockQuantity = StockQuantity - ? WHERE ProductId = ? AND Status = 'ACTIVE' AND StockQuantity >= ?`; 0 dòng bị ảnh hưởng → `RuleViolation BR05` và rollback (được kiểm thử bởi `CheckoutFlowTest.aFailedOrderWriteRollsBackTheStockReservation`).
6. `OrderDAO.insert(order)` (các dòng hàng và sự kiện đầu tiên), `CartDAO.clear(cart)`, commit. Đơn hàng là `PENDING_PAYMENT` (thẻ) hoặc `PLACED` (thanh toán khi nhận hàng).
7. Thẻ (G7): `PaymentForm.submitPayment(order, card)` → `POST /api/orders/{id}/payments` → `PaymentController.pay` dựng `CardData` (kiểm tra định dạng, Luhn và ngày hết hạn) → `PaymentService.pay(orderId, customerId, card)`: giao dịch 1 nạp đơn hàng (BR08) và kiểm tra nó đang chờ thanh toán bằng thẻ; `CardProvider.charge(order code, total, card)` chạy ngoài mọi giao dịch, nên không có khóa cơ sở dữ liệu nào bị giữ trong lúc nhà cung cấp trả lời; giao dịch 2 nạp lại đơn hàng, `Order.recordCardPayment(payment, now)` (chỉ PAID khi được chấp nhận, BR07, BR09), `PaymentDAO.saveAll`, `OrderDAO.saveProgress`.
## 5. Tương tác chính: tìm kiếm AI bằng văn bản (biểu đồ tuần tự thiết kế G9)

1. `SearchForm.showResults(q)` → `GET /api/search?q=` → `SearchController.search(q)` (kiểm tra đầu vào: tối đa 200 ký tự, AI06).
2. `SearchService.search(text)` đọc các sản phẩm ACTIVE trong một giao dịch ngắn (`Database.inTransaction`, `ProductDAO.search`) với giá và tồn kho mới nhất.
3. Nếu danh mục sản phẩm đã thay đổi kể từ lần lập chỉ mục trước (FR-S7), `ProductIndex.build(documents)` dựng lại chỉ mục TF-IDF và từ vựng của nó; `ImageIndex` được dựng lại theo cách tương tự cho tìm bằng ảnh.
4. `QueryInterpreter.interpret(text)` trả về một `SearchQuery`: các từ khóa, các từ liên quan lấy từ lexicon, phần sửa lỗi chính tả (Damerau-Levenshtein so với từ vựng) và giới hạn giá.
5. `ProductIndex.rank(q, k)` trả về các `Hit` kèm điểm và lý do (những từ đóng góp nhiều nhất). Không có kết quả (AI04): tìm theo từ khóa của UC04 chạy thay thế và kết quả nói rõ điều đó.
6. AI07: sản phẩm hết hàng bị xếp thấp hơn (chỉ với tìm bằng văn bản), sau đó `SearchService.SearchResult(mode, understood, items, fallback, tookMs)` → `SearchView` → trang hiển thị truy vấn đã được hiểu ra sao và vì sao từng sản phẩm khớp.
