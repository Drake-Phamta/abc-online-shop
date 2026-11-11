# SPEC: yêu cầu của phần đã cài đặt

Xuất phát từ tiểu luận (chương 1 FR/NFR, chương 2 các use case UC01 đến UC21 và đặc tả UC07). File này
chỉ đặc tả những gì ứng dụng cài đặt; mỗi quy tắc đều có một mã định danh để mã nguồn và kiểm thử viện dẫn.

## 1. Phạm vi

| Use case | Tác nhân | FR / NFR | Đã cài đặt |
|---|---|---|---|
| UC02 Login (đăng nhập) | Customer (khách hàng), Sales Staff (nhân viên bán hàng), Warehouse Staff (nhân viên kho) | FR02, NFR03, NFR04 | có |
| UC04 Browse / Search Products (duyệt / tìm kiếm sản phẩm), kèm tìm kiếm AI ở mục 6 (văn bản, giọng nói, ảnh) | Customer (cả khách vãng lai) | FR04, FR05, NFR01, FR-S1 đến FR-S7 | có |
| UC05 View Product (xem sản phẩm) | Customer (cả khách vãng lai) | FR06 | có |
| UC06 Manage Shopping Cart (quản lý giỏ hàng) | Customer | FR07, FR08 | có |
| UC07 Place Order / Checkout (đặt hàng / thanh toán), include UC21 Validate Cart (kiểm tra giỏ hàng) | Customer | FR09, FR10, FR11, FR15, FR16, NFR10 | có |
| UC08 Make Payment (thanh toán) | Customer, Payment Provider (nhà cung cấp thanh toán, mô phỏng) | FR14 | có |
| UC09 Track Order (theo dõi đơn hàng) | Customer | FR12, FR18 | có |
| UC14 Process Orders (xử lý đơn hàng, gồm cả dữ liệu vận chuyển của UC16) | Sales Staff | FR13, FR17, FR18 | có |
| UC15 Manage Inventory (quản lý tồn kho) | Warehouse Staff | FR16 | có |
| UC01, UC03, UC10 đến UC13, UC16 đến UC20 | | | chỉ đặc tả trong tiểu luận |

Payment Provider được mô phỏng ngay trong ứng dụng (không có mạng thẻ thật): số thẻ kết thúc bằng `0002`
bị từ chối, mọi số hợp lệ khác được chấp nhận. Nhà cung cấp trả về một token; cửa hàng không bao giờ lưu đầy đủ
số thẻ (BR07).

## 2. Quy tắc nghiệp vụ

| Mã | Quy tắc | Thực thi tại |
|---|---|---|
| BR01 | Chỉ sản phẩm có trạng thái ACTIVE mới được thêm vào giỏ hàng hoặc đặt hàng. | model + controller |
| BR02 | Một giỏ hàng chỉ có tối đa một dòng cho mỗi sản phẩm; thêm lại sản phẩm đó thì tăng số lượng. Số lượng của một dòng nằm giữa 1 và tồn kho hiện tại. | model + DB UNIQUE(cart_id, product_id), CHECK |
| BR03 | Một dòng giỏ hàng giữ giá hiển thị lúc nó được thêm vào (giá trong giỏ). Khi đặt hàng, từng dòng được kiểm tra lại theo giá, trạng thái và tồn kho hiện tại (UC21). Nếu giá đã đổi, dòng đó lấy giá hiện tại và khách hàng phải xác nhận lại. | Cart validation |
| BR04 | Tổng đơn hàng = tạm tính − giảm giá VIP + phí vận chuyển. Tạm tính = Σ số lượng × đơn giá. Giảm giá VIP = round(tạm tính × tỷ lệ giảm giá). Phí vận chuyển = 30 000 VND, miễn phí khi tạm tính sau giảm giá từ 500 000 VND trở lên. Số tiền là số nguyên VND. | Order |
| BR05 | Tồn kho được giữ khi đơn hàng được tạo và không bao giờ âm; được trả lại khi đơn hàng bị hủy. | cập nhật có điều kiện trong DAO + DB CHECK |
| BR06 | Một đơn hàng cần có địa chỉ giao hàng thuộc về khách hàng. | controller + FK |
| BR07 | Một đơn hàng chỉ được đánh dấu PAID sau khi nhà cung cấp trả kết quả chấp nhận. Cửa hàng lưu tên chủ thẻ, bốn số cuối, ngày hết hạn và token của nhà cung cấp, không bao giờ lưu đầy đủ số thẻ. | Payment |
| BR08 | Khách hàng chỉ xem và thay đổi giỏ hàng và đơn hàng của chính mình. | controller (id khách hàng trong session) |
| BR09 | Trạng thái đơn hàng chỉ thay đổi theo các chuyển trạng thái ở mục 3, do tác nhân được nêu ở đó thực hiện. | bảng chuyển trạng thái của OrderStatus |
| BR10 | Mỗi đơn hàng có một lô vận chuyển, được tạo khi đơn hàng được giao đi (đơn vị vận chuyển, mã vận đơn, phí). | DB UNIQUE(order_id) |
| BR11 | Đơn hàng thanh toán khi nhận hàng (COD) có bản ghi thanh toán tiền mặt khi đơn được giao đến nơi. | vòng đời của Order |
| BR12 | Nhân viên kho có thể đặt tồn kho là bất kỳ số lượng ≥ 0 cho một sản phẩm đã có. | controller + DB CHECK |
| BR13 | Các chức năng của nhân viên đòi hỏi tài khoản nhân viên có đúng vai trò (SALES cho đơn hàng, WAREHOUSE cho tồn kho). | controller |

## 3. Máy trạng thái của đơn hàng (BR09)

| Từ | Đến | Tác nhân / điều kiện kích hoạt | Hệ quả |
|---|---|---|---|
| (mới) | PENDING_PAYMENT | Khách hàng xác nhận đặt hàng bằng thẻ | tạo đơn hàng + các dòng, giữ tồn kho, làm rỗng giỏ hàng |
| (mới) | PLACED | Khách hàng xác nhận đặt hàng thanh toán khi nhận hàng | như trên |
| PENDING_PAYMENT | PAID | Nhà cung cấp chấp nhận thanh toán bằng thẻ (UC08) | thanh toán APPROVED + một dòng pay_credit |
| PENDING_PAYMENT | PENDING_PAYMENT | Nhà cung cấp từ chối (UC08 A4) | một dòng thanh toán DECLINED; khách hàng có thể thử lại |
| PENDING_PAYMENT | CANCELLED | Khách hàng bỏ dở | trả lại tồn kho |
| PLACED | CANCELLED | Khách hàng hoặc nhân viên bán hàng | trả lại tồn kho |
| PLACED, PAID | PROCESSING | Nhân viên bán hàng | |
| PAID, PROCESSING | CANCELLED | Nhân viên bán hàng | trả lại tồn kho; khoản thanh toán đã chấp nhận chuyển thành REFUNDED |
| PROCESSING | SHIPPED | Nhân viên bán hàng nhập đơn vị vận chuyển và mã vận đơn | tạo một dòng vận chuyển |
| SHIPPED | DELIVERED | Nhân viên bán hàng (đơn vị vận chuyển xác nhận) | vận chuyển DELIVERED; COD: thanh toán COMPLETED + một dòng pay_cash |

Thay đổi so với nội dung UC07 trong tiểu luận: đơn hàng nay được tạo **trước** khi thanh toán (trạng thái PENDING_PAYMENT) vì
FR14 ghi kết quả của nhà cung cấp "vào đúng đơn hàng", điều này cần có sẵn một tham chiếu đến đơn hàng, và tồn kho
phải được giữ trong lúc khách hàng thanh toán. Đơn hàng vẫn chỉ chuyển sang PAID sau khi được chấp nhận (BR07), đúng như UC07 yêu cầu.

## 4. Đặc tả use case

### UC02 Login
Luồng chính: 1. Người dùng nhập email và mật khẩu. 2. Hệ thống kiểm tra tài khoản (khách hàng hoặc nhân viên) và mã băm
của mật khẩu. 3. Hệ thống tạo một session với id và vai trò của người dùng rồi mở trang bắt đầu của vai trò đó.
Luồng thay thế: A1 sai email hoặc mật khẩu: thông báo chung, không gợi ý cái nào sai.

### UC04 Browse / Search Products, UC05 View Product
Luồng chính: 1. Khách hàng mở danh mục sản phẩm, có thể chọn một danh mục (danh mục cha hiển thị sản phẩm của các danh mục con),
hoặc gõ nội dung tìm kiếm ở phần đầu trang. 2. Duyệt: Hệ thống liệt kê các sản phẩm ACTIVE của danh mục kèm
giá và tình trạng còn hàng, sắp xếp theo độ liên quan, giá hoặc mới nhất. Tìm kiếm: tìm kiếm AI ở mục 6 diễn giải
truy vấn, xếp hạng các sản phẩm ACTIVE và cho biết nó đã hiểu truy vấn ra sao và vì sao từng kết quả khớp. 3. Khách hàng
mở một sản phẩm. 4. Hệ thống hiển thị dữ liệu chung (tên, thương hiệu, giá, tình trạng tồn kho, mô tả) và các thuộc tính
của loại chi tiết của sản phẩm (book, laptop, phone, apparel).
Các kiểu tìm kiếm (biểu đồ AI1: use case trừu tượng Search Products (tìm kiếm sản phẩm) được chuyên biệt hóa bởi Search by Text (theo văn bản), Search by
Voice (bằng giọng nói) và Search by Photo (bằng ảnh); mọi kiểu đều include Rank and Explain Results (xếp hạng và giải thích kết quả), tìm bằng văn bản và giọng nói còn include Interpret
Query (diễn giải truy vấn)): bằng văn bản như ở bước 2; bằng giọng nói, trình duyệt chuyển giọng nói thành văn bản, khách hàng có thể sửa văn bản đó, rồi
việc tìm kiếm chạy như tìm bằng văn bản; bằng ảnh, khách hàng tải lên một ảnh và Hệ thống xếp hạng các sản phẩm có hình ảnh giống
nhất. Luồng thay thế: A1 không tìm thấy gì sau một truy vấn gõ hoặc nói (AI04, Fall Back to Keyword Search (quay về tìm theo từ khóa) extend
Search Products tại "không tìm thấy gì"): tìm theo từ khóa trên tên, thương hiệu và danh mục; nếu kết quả cũng rỗng thì hiện một
trạng thái rỗng kèm truy vấn và một liên kết quay về toàn bộ sản phẩm.

### UC06 Manage Shopping Cart
Luồng chính: 1. Khách hàng thêm một sản phẩm kèm số lượng. 2. Hệ thống kiểm tra BR01, BR02 và tồn kho, rồi thêm hoặc gộp dòng
với giá hiện tại làm giá trong giỏ. 3. Khách hàng đổi số lượng hoặc xóa một dòng. 4. Hệ thống tính lại
tạm tính.
Các luồng thay thế: A1 số lượng vượt tồn kho: bị từ chối kèm số lượng còn lại. A2 chưa đăng nhập: yêu cầu đăng nhập, rồi
đưa quay lại sản phẩm.

### UC07 Place Order / Checkout, UC21 Validate Cart
Luồng chính: 1. Khách hàng mở trang đặt hàng. 2. Hệ thống kiểm tra giỏ hàng (UC21, BR03). 3. Khách hàng chọn một địa chỉ
giao hàng và một phương thức thanh toán (thẻ hoặc thanh toán khi nhận hàng). 4. Hệ thống hiển thị tạm tính, giảm giá VIP, phí vận chuyển và
tổng cộng (BR04). 5. Khách hàng xác nhận. 6. Hệ thống, trong một giao dịch, kiểm tra lại giỏ hàng, tạo đơn hàng và các
dòng của nó với đơn giá, giữ tồn kho (BR05) và làm rỗng giỏ hàng. 7. Thanh toán khi nhận hàng: đơn hàng PLACED,
hiển thị xác nhận. Thẻ: UC08 chạy.
Các luồng thay thế: A1 sản phẩm không còn bán hoặc không đủ tồn kho: việc xác nhận bị chặn, dòng bị đánh dấu, giỏ hàng không đổi. A2 không có
địa chỉ hoặc địa chỉ của người khác: bị từ chối (BR06). A3 giá đã đổi kể từ khi vào giỏ: các dòng được cập nhật, khách hàng phải xác nhận tổng
mới.

### UC08 Make Payment
Luồng chính: 1. Khách hàng nhập tên chủ thẻ, số thẻ, ngày hết hạn và CVV cho một đơn hàng PENDING_PAYMENT của chính mình. 2. Hệ thống
gửi số tiền và tham chiếu đơn hàng cho nhà cung cấp. 3. Nhà cung cấp chấp nhận và trả về một token. 4. Hệ thống
ghi nhận thanh toán (APPROVED, bốn số cuối, token) và đặt đơn hàng thành PAID.
Các luồng thay thế: A1 bị từ chối: thanh toán được ghi là DECLINED, đơn hàng vẫn PENDING_PAYMENT, khách hàng có thể thử lại hoặc hủy.
A2 dữ liệu thẻ không hợp lệ (định dạng, hết hạn): bị từ chối trước khi gọi nhà cung cấp.

### UC09 Track Order
Luồng chính: 1. Khách hàng mở "My orders". 2. Hệ thống liệt kê các đơn hàng của khách hàng, mới nhất trước. 3. Khách hàng mở một đơn.
4. Hệ thống hiển thị các dòng, tổng tiền, các bản ghi thanh toán, lô vận chuyển (đơn vị vận chuyển, mã vận đơn) và lịch sử trạng thái.
Luồng thay thế: A1 đơn hàng thuộc về người khác: "not found" (BR08), giống như đơn hàng không tồn tại.

### UC14 Process Orders
Luồng chính: 1. Nhân viên bán hàng mở bảng đơn hàng được nhóm theo trạng thái. 2. Nhân viên chuyển một đơn hàng theo BR09 (xử lý,
giao đi kèm đơn vị vận chuyển và mã vận đơn, giao đến nơi, hủy). 3. Hệ thống áp dụng các hệ quả ở mục 3.
Luồng thay thế: A1 không được phép chuyển trạng thái từ trạng thái hiện tại: bị từ chối kèm các thao tác được phép.

### UC15 Manage Inventory
Luồng chính: 1. Nhân viên kho mở danh sách tồn kho (hàng sắp hết lên trước). 2. Nhân viên đặt một số lượng mới. 3. Hệ thống lưu số lượng đó
(BR12).
Luồng thay thế: A1 số lượng âm hoặc không phải số: bị từ chối.

## 5. Kiểm thử chấp nhận (hành vi)

| Mã | Cho trước | Khi | Thì | Quy tắc |
|---|---|---|---|---|
| AT01 | sản phẩm có tồn kho 2 | khách hàng thêm 3 | bị từ chối, giỏ hàng không đổi | BR02 |
| AT02 | dòng giỏ hàng được thêm với giá 1 000 000, giá hiện tại là 900 000 | kiểm tra khi đặt hàng | giá dòng 900 000, cờ "giá đã đổi" | BR03 |
| AT03 | VIP 5 %, tạm tính 1 000 000 | tính tổng | giảm giá 50 000, phí vận chuyển 0, tổng 950 000 | BR04 |
| AT04 | tồn kho 1, hai đơn hàng mỗi đơn 1 | lần đặt hàng thứ hai | bị từ chối, tồn kho vẫn là 0 | BR05 |
| AT05 | thẻ kết thúc bằng 0002 | thanh toán | DECLINED, đơn hàng vẫn PENDING_PAYMENT; thử lại với thẻ hợp lệ → PAID | BR07 |
| AT06 | đơn hàng của khách hàng B | khách hàng A yêu cầu xem | 404 | BR08 |
| AT07 | đơn hàng PLACED | nhân viên giao đi ngay | bị từ chối (phải đang PROCESSING) | BR09 |
| AT08 | đơn COD đang SHIPPED | nhân viên xác nhận đã giao | DELIVERED, ghi nhận thanh toán tiền mặt | BR11 |
| AT09 | đơn hàng PAID đã giữ tồn kho | nhân viên hủy | CANCELLED, trả lại tồn kho, thanh toán REFUNDED | BR05, BR09 |
| AT10 | session của khách hàng | gọi endpoint dành cho nhân viên | 403 | BR13 |
| AT11 | danh mục sản phẩm của dữ liệu demo | tìm "red sneakers" | Converse Chuck Taylor (giày vải đỏ) đứng đầu; "sneakers" được hiểu là giày | AI02 |
| AT12 | như trên | tìm "macbok air" | Apple MacBook Air đứng đầu; trang hiện phần sửa lỗi macbok → macbook | AI02 |
| AT13 | như trên | tìm "laptop under 10 million" | chỉ gồm laptop có giá tối đa 10 000 000 ₫ (ThinkPad T470, Latitude 5480) | AI03 |
| AT14 | như trên | tìm "book for a programmer" | Clean Code và The Pragmatic Programmer nằm trong ba kết quả đầu | AI02 |
| AT15 | ảnh một sản phẩm trong danh mục, đã cắt, tối hơn và trên nền khác | tìm bằng ảnh | sản phẩm đó đứng đầu | FR-S5 |
| AT16 | như trên | tìm "xyzzy" | tìm kiếm AI và tìm theo từ khóa đều không thấy gì; trạng thái rỗng nói rõ điều đó | AI04 |
| AT17 | một file văn bản gửi như ảnh | tìm bằng ảnh | 400 "not a JPEG or PNG image", không lưu gì | AI05, AI06 |

## 6. Tìm kiếm AI (chương 3): đặc tả thành phần AI

Xây dựng từ ghi chú của giảng viên "Integrating AI into E-Commerce Systems" (tích hợp AI vào hệ thống thương mại điện tử): vấn đề nghiệp vụ, yêu cầu, yêu cầu về AI và
dữ liệu, rồi đến thành phần, các tương tác, lỗi, rủi ro và đánh giá.

| Hạng mục | ABC Online Shop |
|---|---|
| Vấn đề nghiệp vụ | Khách hàng không gõ đúng tên sản phẩm thì không tìm thấy gì: tìm theo từ khóa chỉ khớp chuỗi con của tên, thương hiệu và danh mục. "red sneakers", "macbok", "laptop under 10 million" hay ảnh một chiếc giày đều không trả về sản phẩm nào, nên khách muốn mua lại bỏ đi. Chương 1 đòi hỏi nhiều hơn: nhu cầu của bên liên quan SN02 "duyệt và tìm kiếm danh mục sản phẩm một cách hiệu quả" và FR05 (Must) "cho phép khách hàng tìm kiếm danh mục sản phẩm". |
| Mục tiêu nghiệp vụ | Nhiều lượt tìm kiếm kết thúc ở trang sản phẩm hoặc trong giỏ hàng hơn (tỷ lệ tìm kiếm thành công), ít lượt tìm kiếm không có kết quả hơn. |
| Yêu cầu nghiệp vụ | Cửa hàng giúp khách hàng tìm đúng sản phẩm chỉ trong một lần tìm, dù khách gõ, nói hay đưa ảnh. |
| Yêu cầu chức năng | FR-S1 diễn giải truy vấn văn bản tự do: từ đồng nghĩa và từ liên quan, lỗi chính tả, giới hạn giá; FR-S2 xếp hạng các sản phẩm ACTIVE theo độ liên quan; FR-S3 hiển thị truy vấn đã được hiểu ra sao và vì sao từng kết quả khớp; FR-S4 nhận truy vấn bằng giọng nói (chuyển giọng nói thành văn bản ngay trong trình duyệt, cho sửa trước khi gửi); FR-S5 nhận một ảnh và trả về các sản phẩm có hình giống nhất; FR-S6 quay về tìm theo từ khóa khi tìm kiếm AI không thấy gì; FR-S7 giữ chỉ mục đồng bộ với danh mục sản phẩm (dựng từ cơ sở dữ liệu khi khởi động). |
| Chức năng AI | Xếp hạng: với truy vấn q và mỗi sản phẩm p, một điểm liên quan s(q, p); kết quả là k sản phẩm đứng đầu. Văn bản: mô hình không gian vector với trọng số từ (TF-IDF) học từ văn bản của danh mục sản phẩm, kèm mở rộng truy vấn. Ảnh: một vector đặc trưng về màu sắc và hình dạng cho mỗi ảnh, độ tương đồng cosine. |
| Đầu vào | văn bản tối đa 200 ký tự, hoặc một ảnh JPEG hoặc PNG tối đa 5 MB |
| Đầu ra | tối đa 12 sản phẩm, mỗi sản phẩm kèm điểm và lý do; truy vấn đã được hiểu (từ khóa, phần mở rộng, phần sửa lỗi, giới hạn giá); một cờ khi đã dùng phương án dự phòng |
| Nguồn dữ liệu | product (tên, thương hiệu, mô tả, giá, trạng thái), category (tên và danh mục cha), book_detail, laptop_detail, phone_detail, apparel_detail (mọi giá trị), ảnh sản phẩm trong thư mục ảnh của cửa hàng; không lưu thêm gì mới |
| Vị trí | Thành phần AI nằm ở tầng logic nghiệp vụ (package `ai`), được SearchService gọi; không dùng dịch vụ bên ngoài |
| Tương tác | SearchForm (view) → SearchController → SearchService → QueryInterpreter, ProductIndex, ImageIndex; SearchService đọc danh mục sản phẩm qua ProductDAO |
| Hiệu năng | tìm bằng văn bản dưới 300 ms, tìm bằng ảnh dưới 1 s trên máy demo; hit@1 và MRR tốt hơn tìm theo từ khóa trên các truy vấn đã gán nhãn (mục 6.2) |
| Cập nhật | chỉ mục được dựng từ cơ sở dữ liệu khi lần tìm kiếm đầu tiên chạy và được dựng lại sau khi danh mục sản phẩm thay đổi |
| Vai trò của con người | nhân viên bán hàng giữ danh sách từ liên quan (lexicon trong QueryInterpreter) và kiểm tra các truy vấn đã gán nhãn trước khi một thay đổi được đưa vào chạy thật |
| Rủi ro | kết quả sai hoặc thiếu; xếp hạng thiếu công bằng (một thương hiệu luôn đứng đầu); ảnh có người; đầu vào quá dài hoặc cố tình tạo ra; xem 6.3 |
| Đánh giá | kỹ thuật: hit@1, recall@5, MRR, tỷ lệ truy vấn không có kết quả, độ chính xác top-1 và top-3 của tìm bằng ảnh, độ trễ; nghiệp vụ: tỷ lệ tìm kiếm thành công và chuyển đổi sau tìm kiếm (cần lưu lượng thật, đã lên kế hoạch) |

### 6.1 Các quy tắc của tìm kiếm AI

| Mã | Quy tắc |
|---|---|
| AI01 | Chỉ các sản phẩm ACTIVE được lập chỉ mục và trả về (BR01). |
| AI02 | Trang kết quả cho biết truy vấn đã được hiểu ra sao (từ được mở rộng, phần sửa lỗi, giới hạn giá) và mỗi kết quả cho biết vì sao nó khớp (khả năng giải thích). |
| AI03 | Giới hạn giá trong truy vấn ("under 10 million", "below 500k") là bộ lọc cứng: không có kết quả nào vượt quá giới hạn đó. |
| AI04 | Khi tìm kiếm AI không thấy gì, tìm theo từ khóa sẽ chạy; trang cho biết kết quả do kiểu tìm kiếm nào tạo ra. |
| AI05 | Ảnh và giọng nói được xử lý trong bộ nhớ và không bao giờ được lưu; văn bản tìm kiếm không được ghi log kèm khách hàng. |
| AI06 | Giới hạn đầu vào: văn bản tối đa 200 ký tự, ảnh tối đa 5 MB, chỉ nhận JPEG hoặc PNG. |
| AI07 | Trong tìm kiếm bằng văn bản, sản phẩm hết hàng vẫn được hiển thị, kèm nhãn tồn kho, nhưng độ liên quan của nó bị tính ít đi 20 %: nó chỉ còn đứng trước khi rõ ràng liên quan hơn các sản phẩm đang có thể mua. Một ảnh chỉ thể hiện một sản phẩm, nên tìm bằng ảnh giữ nguyên vị trí của nó (khách hàng biết là sản phẩm đã hết hàng). |

### 6.2 Quy trình đánh giá

`tests/search_eval.py` chạy trên một máy chủ mới: 30 truy vấn đã gán nhãn (`tests/search/queries.json`, mỗi truy vấn kèm các
SKU mà một nhân viên bán hàng sẽ chỉ cho khách) qua tìm theo từ khóa và tìm kiếm AI, cùng 84 ảnh làm từ các ảnh trong
danh mục sản phẩm (cắt, xoay, đổi ánh sáng, đổi nền; `tests/search/make_photos.py`) qua tìm bằng
ảnh. Kết quả ở `docs/evidence/search_eval.txt`.

### 6.3 Phân tích lỗi và rủi ro

| Lỗi hoặc rủi ro | Hậu quả | Cách xử lý trong thiết kế |
|---|---|---|
| Truy vấn dùng những từ không có trong danh mục sản phẩm | không có kết quả | mở rộng bằng lexicon, sửa lỗi chính tả, rồi quay về tìm theo từ khóa (AI04) |
| Ảnh chất lượng thấp hoặc không liên quan | hiển thị những sản phẩm không liên quan | trang hiển thị điểm tương đồng; kết quả dưới ngưỡng không được hiển thị |
| Trình duyệt không có nhận dạng giọng nói (hoặc không có mạng cho việc đó) | nút giọng nói không nghe được | hộp thoại báo điều đó và giữ ô nhập văn bản; vẫn gõ được |
| Danh mục sản phẩm thay đổi | kết quả cũ | chỉ mục được dựng lại sau khi thay đổi; giá và tồn kho của kết quả được đọc mới từ cơ sở dữ liệu |
| Xếp hạng thiếu công bằng | một số sản phẩm không bao giờ được thấy | xếp hạng chỉ dùng các từ của truy vấn, không ưu tiên thương hiệu; các truy vấn đã gán nhãn kiểm tra những thương hiệu khác |
| Quyền riêng tư của ảnh | dữ liệu cá nhân trong ảnh | xử lý trong bộ nhớ, không lưu, không ghi log (AI05) |
| Đầu vào quá lớn hoặc cố tình tạo ra | tìm chậm, lỗi | các giới hạn của AI06, loại file được kiểm tra trước khi giải mã |
