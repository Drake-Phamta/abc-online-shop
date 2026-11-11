# ABC Online Shop: từ yêu cầu đến mã chạy được

Tiểu luận môn Phân tích và thiết kế hệ thống thông tin (PTIT, 2026): các mô hình phân tích và thiết kế của
ABC Online Shop trong Visual Paradigm, cơ sở dữ liệu và bộ khung mã được sinh ra từ các mô hình, cùng một bản cài đặt
bằng Java với tính năng tìm kiếm AI (văn bản, giọng nói, ảnh) bám sát thiết kế từng lớp một. Toàn bộ tiểu luận nằm trong thư mục này (cũng là kho git).
Bấm đúp **CHAY_DEMO.bat** để chạy cửa hàng; mở [showcase/index.html](showcase/index.html) để xem phần hướng dẫn
dùng khi bảo vệ.

## Mọi thứ nằm ở đâu

| Sản phẩm | Vị trí |
|---|---|
| Tiểu luận (báo cáo chính thức) | [Bai_nop/tieuluan_V4_04_10_phamtuananh_018.pdf](Bai_nop/tieuluan_V4_04_10_phamtuananh_018.pdf) và `.docx`; mã nguồn ở [Nguon](Nguon) (`Nguon/make.ps1` dựng lại cả hai vào `Bai_nop`); tiểu luận lấy hình từ `vp/png` và `docs/evidence` |
| Đề bài của giảng viên và tài liệu môn học | [De_bai](De_bai) (ảnh bảng, slide, tiểu luận mẫu, 50 câu hỏi vấn đáp); chỉ có trong bản trên máy, không có trong kho công khai |
| Đặc tả yêu cầu | chương 1 và 2 của tiểu luận; các quy tắc, máy trạng thái và kiểm thử chấp nhận trong [docs/SPEC.md](docs/SPEC.md) |
| Biểu đồ theo từng giai đoạn | Dự án Visual Paradigm [vp/ABC_Online_Shop_V4.vpp](vp/ABC_Online_Shop_V4.vpp) với 42 biểu đồ, hình ảnh trong [vp/png](vp/png) (B = nghiệp vụ, R = yêu cầu, A = phân tích, AI = tìm kiếm AI, D = dữ liệu, G = thiết kế); mọi hình đều có trong tiểu luận |
| Mô hình dữ liệu và lược đồ | D1 đến D4 trong VP; [db/schema.sql](db/schema.sql) = DDL xuất từ mô hình vật lý của VP ([db/vp/vp_ddl.sql](db/vp/vp_ddl.sql)); cơ sở dữ liệu do Generate Database của VP ghi ra là [db/vp/abc_shop_vp.db](db/vp/abc_shop_vp.db) cùng DDL của nó [db/vp/vp_generated.ddl](db/vp/vp_generated.ddl); [db/compare_schema.py](db/compare_schema.py) đối chiếu cả ba |
| Do Visual Paradigm sinh ra | ảnh chụp màn hình Generate Database và Instant Generator trong [docs/evidence/vp_generation](docs/evidence/vp_generation), bộ khung Java do VP sinh ra trong [docs/evidence/vp_codegen](docs/evidence/vp_codegen), được đối chiếu với mã bằng [tests/vpgen_vs_code.py](tests/vpgen_vs_code.py) |
| Tìm kiếm AI (chương 3 của tiểu luận) | đặc tả trong [docs/SPEC.md](docs/SPEC.md) mục 6, mã trong `app/src/main/java/vn/ptit/ecom/ai`, đánh giá bằng [tests/search_eval.py](tests/search_eval.py) với kết quả [docs/evidence/search_eval.txt](docs/evidence/search_eval.txt) |
| Ghi chú thiết kế | [docs/DESIGN.md](docs/DESIGN.md) |
| Mã nguồn | [app/](app) (Java 17, Spring Boot 3.2, JDBC, SQLite; các view trên trình duyệt ở `app/src/main/resources/static/js/view`) |
| Dữ liệu demo | [db/seed.sql](db/seed.sql), tạo bởi [db/make_seed.py](db/make_seed.py) từ `db/seed/products.json`: 10 danh mục, 28 sản phẩm, 3 khách hàng, 2 tài khoản nhân viên, 4 đơn hàng |
| Truy vết | [docs/TRACEABILITY.md](docs/TRACEABILITY.md) |
| Hướng dẫn bảo vệ (kịch bản, các quyết định, 50 câu hỏi) | [docs/DEFENSE.md](docs/DEFENSE.md); trên trang công khai chỉ có bản được bảo vệ bằng mật khẩu |
| Bằng chứng kiểm thử | JUnit trong `app/src/test`, [tests/smoke_api.py](tests/smoke_api.py), [tests/e2e/run_e2e.mjs](tests/e2e/run_e2e.mjs) kèm ảnh chụp màn hình trong [docs/evidence/e2e](docs/evidence/e2e), [tests/design_vs_code.py](tests/design_vs_code.py), [tests/vpgen_vs_code.py](tests/vpgen_vs_code.py), [tests/search_eval.py](tests/search_eval.py) |
| Phần trình bày bảo vệ kỹ thuật | [showcase/index.html](showcase/index.html) (tiếng Anh) và [showcase/index.vi.html](showcase/index.vi.html) (tiếng Việt); tài liệu, mã và thư mục mở ra thành các trang đọc được từ [showcase/pages](showcase/pages), do [showcase/build_pages.py](showcase/build_pages.py) tạo |
| Các phiên bản trước, file lưu trữ | [Luu_tru](Luu_tru) (không cần cho bài nộp; chỉ có trong bản trên máy) |

## Chạy

Bấm đúp [CHAY_DEMO.bat](CHAY_DEMO.bat): script tìm Java 17 (trên máy này `java` trong PATH là Java 8 cũ hơn,
nên script dùng `JAVA_HOME`), dựng file jar nếu chưa có, khởi động máy chủ với một cơ sở dữ liệu demo mới và
mở http://localhost:8080 khi máy chủ phản hồi. Đóng cửa sổ của nó để dừng máy chủ; `CHAY_DEMO.bat keep` giữ lại
dữ liệu của lần chạy trước.

Phần showcase có thể tự khởi động cửa hàng. Mỗi lần chạy, CHAY_DEMO.bat đăng ký kiểu liên kết `abcshop:` cho
người dùng Windows hiện tại ([showcase/abcshop.ps1](showcase/abcshop.ps1), không cần quyền admin). Khi showcase được mở
từ máy này, nút "Mở cửa hàng" (chấm xanh: đang chạy, chấm xám: đã dừng) chạy CHAY_DEMO.bat nếu máy chủ không
phản hồi, còn "Mở trong File Explorer" / "Mở bằng Visual Paradigm" mở một file của dự án; trình xử lý từ chối mọi
đường dẫn nằm ngoài thư mục dự án. Trình duyệt hỏi một lần cho mỗi lần bấm, hãy chọn Open. Để gỡ kiểu liên kết này:
`reg delete "HKCU\Software\Classes\abcshop" /f`. Sau khi một tài liệu thay đổi, dựng lại trang đọc được của nó bằng
`python showcase/build_pages.py`.

Bản công khai: https://drake-phamta.github.io/abc-online-shop/ (GitHub Pages; ở đó nút mở cửa hàng mở shop đang chạy khi
tunnel bên dưới đang bật, nếu không thì giải thích cách chạy cửa hàng; các nút File Explorer bị ẩn). Sau khi commit, `powershell -NoProfile -File
showcase/publish_pages.ps1` xuất bản trạng thái hiện tại thành một commit snapshot cùng với PDF tiểu luận; lịch sử cục bộ,
De_bai, Luu_tru và file docx chỉ nằm lại trên máy này.

Chính cửa hàng đang chạy cũng có thể truy cập từ Internet: bấm đúp [CHAY_TUNNEL.bat](CHAY_TUNNEL.bat). File này khởi động
cửa hàng nếu cần, mở một Cloudflare quick tunnel ([tools/quick_tunnel.ps1](tools/quick_tunnel.ps1), không cần tài khoản
Cloudflare; `cloudflared.exe` chính thức được tải một lần vào `%LOCALAPPDATA%\cloudflared` và được kiểm tra chữ ký), in
ra địa chỉ công khai `https://....trycloudflare.com`, chép vào clipboard và mở nó. Địa chỉ đổi sau mỗi lần chạy và chỉ
hoạt động khi cửa sổ đó còn mở (nếu cloudflared dừng, script tự mở lại); mỗi địa chỉ mới được ghi vào ô Website của repo
GitHub (và vào `live.txt` của nhánh `live`, phòng khi GitHub API hết lượt gọi trong giờ), nên nút mở shop trên showcase
bản công khai mở được shop đang chạy. Nếu cửa hàng không phản hồi trong 3 phút, script tự khởi động lại nó và giữ nguyên
dữ liệu. Ai có địa chỉ cũng dùng được các tài khoản
demo, nên hãy đóng cửa sổ sau buổi bảo vệ.

Chạy thủ công (JDK 17, Maven 3.9; Python 3.10+ và Node 18+ cùng Microsoft Edge cho các kiểm thử):

```
cd app
mvn -q package -DskipTests
"%JAVA_HOME%\bin\java" -jar target/abc-online-shop-1.0.0.jar --abc.db.reset=true
```

Tên thư mục có chữ tiếng Việt; `app/.mvn/jvm.config` khởi động Maven với UTF-8, nếu thiếu thì Maven dừng với lỗi
"Input length = 1". `--abc.db.reset=true` tạo lại file SQLite `app/data/abc_shop.db` từ DDL và
dữ liệu seed; nếu không có tùy chọn này thì file hiện có được giữ nguyên. Tài khoản (mật khẩu `demo1234`): `an.nguyen@example.com` (khách hàng
VIP), `lan.tran@example.com` (khách hàng mới), `sales@example.com` (bảng đơn hàng), `warehouse@example.com`
(tồn kho). Thẻ thử: `4242 4242 4242 4242` được chấp nhận, số kết thúc bằng `0002` bị từ chối. Alt+L hiện
design lens (view, endpoint, controller, service, DAO và các bảng của từng phần trên màn hình).

## Kiểm thử

```
cd app && mvn test                       # 24 JUnit tests (model rules, checkout flow, AI search on a real SQLite file)
python tests/smoke_api.py                # 36 checks over HTTP (server running)
cd tests/e2e && npm install && node run_e2e.mjs   # 30 checks in Edge on a fresh database, screenshots
python tests/design_vs_code.py           # VP design model against the compiled code (run mvn compile first)
python tests/vpgen_vs_code.py            # code generated by VP Instant Generator against the compiled code
python tests/search_eval.py              # AI search against keyword search: 30 queries, 84 photos (server running)
python db/compare_schema.py              # VP DDL and the VP-generated database against db/schema.sql
python tests/check_links.py              # every link of the documents and the showcase opens a file
```
