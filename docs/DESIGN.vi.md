# DESIGN: mô hình dữ liệu và thiết kế lớp của phần đã cài đặt

Đầu vào: SPEC.md, biểu đồ lớp phân tích (Hình 4.1 của tiểu luận, mười chín lớp của Test 01) và góp ý của giảng viên
về Product. Đầu ra: `db/schema.sql` và các package dưới `app/src/main/java/vn/ptit/ecom`.

## 1. Mô hình khái niệm (thực thể và quan hệ)

Category (cây) 1 - 0..* Product; BookDetail, LaptopDetail, PhoneDetail, ApparelDetail là lớp con của Product (loại chi
tiết của danh mục cho biết là lớp nào); Customer 1 - 0..* Address; Customer 1 - 0..1 Cart; Cart 1 - 0..* CartItem; CartItem 0..* - 1
Product; Customer 1 - 0..* Order; Order 1 - 1..* OrderItem; OrderItem 0..* - 1 Product; Order 1 - 0..* Payment
(Cash hoặc Credit); Order 1 - 0..1 Shipping; Shipping 0..* - 1 Address; Order 1 - 1..* OrderEvent; Customer có thể là VIP 0..1,
New 0..1; Staff (Sales hoặc Warehouse).

## 2. Từ mô hình phân tích đến mô hình vật lý đã chỉnh sửa

| Thành phần của mô hình phân tích (Hình 4.1) | Thiết kế sau chỉnh sửa | Lý do |
|---|---|---|
| Book, Electronics, Laptop, Mobile, Clothes, Shoes, mỗi lớp có productId, price, stockQuantity | `product` giữ định danh và các thuộc tính chung (sku, name, brand, price, stock, status); `category` phân loại; mỗi bộ thuộc tính có một bảng chi tiết riêng: `book_detail`, `laptop_detail`, `phone_detail`, `apparel_detail` | góp ý của giảng viên; dữ liệu chung chỉ lưu một lần; danh mục mới dùng bộ thuộc tính đã có thì không cần bảng mới |
| Khái quát hóa Electronics (warrantyMonths) | danh mục cha "Electronics"; thời hạn bảo hành nằm trong các bảng chi tiết của laptop và phone | việc nhóm là dữ liệu, không phải cấu trúc |
| Clothes và Shoes | một bảng `apparel_detail` (nhãn kích cỡ, màu sắc, chất liệu) | bộ thuộc tính giống nhau |
| {xor} từ CartItem/OrderItem tới bốn lớp | FK thông thường tới `product` | mỗi dòng tham chiếu đúng một sản phẩm |
| Customer ◆ FullName | các cột tên của `customer` | thành phần quan hệ 1 đến 1, không có định danh |
| Customer ◇ Address | bảng `address`, thêm người nhận và số điện thoại | giao hàng cần có người nhận |
| CustomerVIP, CustomerNew | `customer_vip`, `customer_new`, PK = FK | mỗi lớp con một bảng |
| Order (phân tích) | `customer_order` với trạng thái, phương thức thanh toán, tạm tính, giảm giá, phí vận chuyển, tổng (CHECK total = subtotal − discount + fee) | BR04 được lưu thành một dữ kiện có ràng buộc kiểm tra |
| OrderItem.unitPrice | `order_item.unit_price` + bản chụp `product_name` | dữ kiện lịch sử (ngoại lệ của 3NF đã được giải thích) |
| Payment, PayCash, PayCredit (cardNumber) | `payment` + `pay_cash` / `pay_credit` (bốn số cuối, ngày hết hạn, token của nhà cung cấp) | BR07 |
| Shipping | `shipping` với UNIQUE(order_id), UNIQUE(tracking_number) | BR10 |
| (không có trong phân tích) Staff | `staff` với vai trò SALES hoặc WAREHOUSE | các tác nhân của UC14, UC15 cần có tài khoản (UC02) |
| (không có trong phân tích) lịch sử trạng thái | `order_event` | UC09 hiển thị lịch sử |
| mã varchar (C001, O001) | khóa số nguyên; mã được định dạng khi hiển thị (ORD-000123) | khóa đơn giản hơn, do cơ sở dữ liệu sinh ra |

Chuẩn hóa: 1NF (các cột nguyên tử, nhóm lặp tách thành bảng riêng), 2NF (khóa một cột; các khóa UNIQUE gồm nhiều cột
không phải khóa chính), 3NF trừ hai giá trị lịch sử có chủ ý (`order_item.unit_price`,
`order_item.product_name`) và các tổng tiền được lưu của đơn hàng, vốn bằng giá trị tính toán lúc đặt hàng và được
bảo vệ bởi một ràng buộc CHECK.

## 3. Package và lớp (ba tầng)

Các lớp thiết kế trong VP (biểu đồ G1 đến G4b và G8, thư mục "4 Design") và mã nguồn có cùng package, lớp,
thuộc tính và thao tác; `tests/design_vs_code.py` kiểm tra điều này với các lớp đã biên dịch và các view JS
(80 lớp: 72 lớp Java với 169 thuộc tính và 134 thao tác, 8 lớp view với 25 thao tác, và 48 lời gọi trong
các biểu đồ tuần tự thiết kế G5, G6, G7 và G9), đồng thời kiểm tra rằng không file nào của package `ai` import phần khác của ứng dụng.
`tests/vpgen_vs_code.py` đi từ phía ngược lại: 81 file mà Instant Generator của VP ghi ra từ cùng mô hình
(`docs/evidence/vp_codegen`) đều phải có trong mã nguồn với cùng các field và phương thức (190 field, 157 phương thức).

| Tầng (G0) | Package | Các lớp | Trách nhiệm |
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
5. `ProductDAO.reserveStock(productId, quantity)` cho mỗi dòng: `UPDATE product SET stock_quantity = stock_quantity − ? WHERE product_id = ? AND status = 'ACTIVE' AND stock_quantity >= ?`; 0 dòng bị ảnh hưởng → `RuleViolation BR05` và rollback (được kiểm thử bởi `CheckoutFlowTest.aFailedOrderWriteRollsBackTheStockReservation`).
6. `OrderDAO.insert(order)` (các dòng hàng và sự kiện đầu tiên), `CartDAO.clear(cart)`, commit. Đơn hàng là `PENDING_PAYMENT` (thẻ) hoặc `PLACED` (thanh toán khi nhận hàng).
7. Thẻ (G7): `PaymentForm.submitPayment(order, card)` → `POST /api/orders/{id}/payments` → `PaymentController.pay` dựng `CardData` (kiểm tra định dạng, Luhn và ngày hết hạn) → `PaymentService.pay(orderId, customerId, card)`: giao dịch 1 nạp đơn hàng (BR08) và kiểm tra nó đang chờ thanh toán bằng thẻ; `CardProvider.charge(order code, total, card)` chạy ngoài mọi giao dịch, nên không có khóa cơ sở dữ liệu nào bị giữ trong lúc nhà cung cấp trả lời; giao dịch 2 nạp lại đơn hàng, `Order.recordCardPayment(payment, now)` (chỉ PAID khi được chấp nhận, BR07, BR09), `PaymentDAO.saveAll`, `OrderDAO.saveProgress`.
## 5. Tương tác chính: tìm kiếm AI bằng văn bản (biểu đồ tuần tự thiết kế G9)

1. `SearchForm.showResults(q)` → `GET /api/search?q=` → `SearchController.search(q)` (kiểm tra đầu vào: tối đa 200 ký tự, AI06).
2. `SearchService.search(text)` đọc các sản phẩm ACTIVE trong một giao dịch ngắn (`Database.inTransaction`, `ProductDAO.search`) với giá và tồn kho mới nhất.
3. Nếu danh mục sản phẩm đã thay đổi kể từ lần lập chỉ mục trước (FR-S7), `ProductIndex.build(documents)` dựng lại chỉ mục TF-IDF và từ vựng của nó; `ImageIndex` được dựng lại theo cách tương tự cho tìm bằng ảnh.
4. `QueryInterpreter.interpret(text)` trả về một `SearchQuery`: các từ khóa, các từ liên quan lấy từ lexicon, phần sửa lỗi chính tả (Damerau-Levenshtein so với từ vựng) và giới hạn giá.
5. `ProductIndex.rank(q, k)` trả về các `Hit` kèm điểm và lý do (những từ đóng góp nhiều nhất). Không có kết quả (AI04): tìm theo từ khóa của UC04 chạy thay thế và kết quả nói rõ điều đó.
6. AI07: sản phẩm hết hàng bị xếp thấp hơn (chỉ với tìm bằng văn bản), sau đó `SearchService.SearchResult(mode, understood, items, fallback, tookMs)` → `SearchView` → trang hiển thị truy vấn đã được hiểu ra sao và vì sao từng sản phẩm khớp.
