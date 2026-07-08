# Hướng Dẫn Quy Trình Làm Việc Với OpenSpec (Lab0Project)

Tài liệu này hướng dẫn chi tiết quy trình làm việc chuẩn hóa theo phương pháp **Phát triển hướng Đặc tả (Spec-Driven Development)** sử dụng **OpenSpec CLI** cho Lab04 CPG Streaming.

---

## 1. Bản chất cấu trúc đặc tả OpenSpec

Hệ thống đặc tả được phân chia rõ ràng làm hai phần để tránh trùng lặp thông tin và dễ theo dõi lịch sử thay đổi:

1. **`openspec/specs/` (Base Specifications - Đặc tả gốc):**
   * Lưu trữ đặc tả hoàn chỉnh và chính thức của hệ thống đang hoạt động.
   * Đây là **nguồn sự thật (Source of Truth)**. Mỗi mảng chức năng (Parser, Kafka/Spark, DB Stores, Evidence Book) có duy nhất 1 tệp `spec.md` tại đây.
2. **`openspec/changes/<change-name>/specs/` (Delta Specifications - Đặc tả phần bù):**
   * Chỉ lưu trữ **các yêu cầu được thêm mới, sửa đổi hoặc xóa bỏ (Delta)** phục vụ riêng cho đợt triển khai (Stage) hiện tại.
   * Khi kết thúc Stage, các yêu cầu Delta này sẽ được tự động gộp (merge) vào Base Spec tương ứng ở thư mục `openspec/specs/` thông qua lệnh `openspec archive`.

---

## 2. Quy trình chi tiết cho Lập trình viên (Developer Workflow)

Khi nhận nhiệm vụ (ví dụ: Trực phụ trách Kafka/Spark, Thanh phụ trách Graph Stores, Tuấn phụ trách Jupyter Book), lập trình viên thực hiện nghiêm ngặt các bước sau:

### Bước 1: Nhận nhiệm vụ & Đồng bộ môi trường

1. Xem nhiệm vụ tổng quát của mình trong tệp kế hoạch dự án [workplan.md](../docs/team/workplan.md).
2. Đồng bộ mã nguồn mới nhất từ nhánh chung:
   ```bash
   git checkout dev
   git pull origin dev
   ```
3. Đảm bảo trạng thái OpenSpec cục bộ khỏe mạnh:
   ```bash
   openspec doctor
   ```
   *(Kết quả bắt buộc phải hiển thị: `OpenSpec root: ok`)*.

### Bước 2: Tạo nhánh tính năng (Feature Branch)
Tạo nhánh mới từ `dev` để thực hiện nhiệm vụ:
```bash
git checkout -b feature/<tên_thành_viên>/<tên_nhiệm_vụ>
# Ví dụ: git checkout -b feature/truc/spark-metadata-stream
```

### Bước 3: Đọc Đặc tả & Danh sách Task

1. Đọc tệp Base Spec tương ứng của mình tại `openspec/specs/<mảng_phụ_trách>/spec.md`.
2. Đọc đặc tả bổ sung (Delta Spec) và danh sách công việc chi tiết của Stage hiện tại ở tệp `openspec/changes/<stage-đang-chạy>/tasks.md`.

### Bước 4: Phát triển mã nguồn & Xác thực cục bộ

1. Triển khai viết code/cấu hình giải quyết bài toán.
2. Xác thực tính đúng đắn của tài liệu đặc tả:
   ```bash
   openspec validate --all --strict
   ```
3. Chạy bộ kiểm thử tự động toàn diện của dự án:
   ```bash
   bash scripts/run_checks.sh
   ```
   *(Đảm bảo toàn bộ unit tests vượt qua thành công và không xảy ra lỗi regression trên code cũ)*.

### Bước 5: Cập nhật Bằng chứng (Evidence) & Tracker cá nhân

1. Chụp ảnh minh chứng giao diện chạy thành công (lưu vào thư mục tương ứng trong `screenshots/`) và chạy các notebook demo (`notebooks/*.ipynb`).
2. Mở tệp tiến trình cá nhân tại thư mục [docs/team/](../docs/team/) (ví dụ: `docs/team/kafka-spark.md`) để cập nhật:
   * Đánh dấu `[x]` các task đã xong.
   * Điền bảng kê khai các lệnh đã chạy cục bộ (Commands run) và kết quả thực tế.
3. Commit và đẩy nhánh lên GitHub:
   ```bash
   git add -A
   git commit -m "feat: implement spark streaming job and update progress tracker"
   git push origin feature/<tên_thành_viên>/<tên_nhiệm_vụ>
   ```

### Bước 6: Tạo Pull Request

* Tạo Pull Request (PR) gửi từ nhánh tính năng của bạn về nhánh **`dev`**.
* Gắn link tệp tiến độ cá nhân đã cập nhật vào mô tả PR và thông báo cho Lead (Tri) duyệt.

---

## 3. Quy trình chi tiết cho Quản lý dự án (Lead Workflow - Tri)

Với vai trò Lead, Tri thực hiện quản lý vòng đời đặc tả dự án qua các bước:

### Bước 1: Khởi động một Stage mới (ví dụ Stage 3)

1. **Tạo thư mục Change Proposal:** Tạo gói thay đổi mới cho Stage 3 thông qua OpenSpec CLI:
   ```bash
   openspec change stage3-replay-hardening
   ```
2. **Khai báo yêu cầu Delta:** Soạn thảo các yêu cầu đặc tả thêm mới phục vụ riêng cho Stage 3 (ví dụ: logic replay, cleanup) vào thư mục mới `openspec/changes/stage3-replay-hardening/specs/`.
3. **Phân công nhiệm vụ:** Soạn thảo bảng phân công công việc chi tiết cho các thành viên tại `openspec/changes/stage3-replay-hardening/tasks.md`.
4. **Xác thực và Đẩy Git:** Chạy kiểm định đặc tả trước khi push lên nhánh chung:
   ```bash
   openspec validate --all --strict
   ```

### Bước 2: Kiểm duyệt và Hợp nhất PR của thành viên

1. Kiểm tra PR của thành viên, đảm bảo tệp theo dõi cá nhân tương ứng trong `docs/team/` đã cập nhật đầy đủ bằng chứng chạy thành công và hình ảnh.
2. Kiểm tra bộ test tự động của dự án báo xanh.
3. Merge PR của thành viên vào nhánh `dev`.

### Bước 3: Đóng Stage & Hợp nhất Đặc tả (Archive)

Khi tất cả các thành viên đã hoàn thành công việc của Stage, Tri chạy lệnh lưu trữ:
```bash
openspec archive <tên_stage>
# Ví dụ: openspec archive stage2-team-handoff
```
*Lệnh này sẽ tự động gộp (merge) các yêu cầu Delta của Stage đó vào tệp Base Spec gốc trong `openspec/specs/` và chuyển thư mục Stage cũ vào `openspec/changes/archive/` để lưu vết lịch sử thiết kế.*
