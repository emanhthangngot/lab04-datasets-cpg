# Hướng Dẫn OpenSpec Cho Lab04

Thư mục này dùng format chuẩn của OpenSpec CLI với schema `spec-driven`.

## Cấu Trúc

```text
openspec/
├── config.yaml
├── specs/                  # Current accepted specs
└── changes/                # Change proposals theo từng stage
    ├── archive/
    ├── stage1-foundation/
    └── stage2-core-sample-pipeline/
```

## Cách Hiểu

- `openspec/specs/` là spec hiện tại đã được chấp nhận. Lệnh
  `openspec list --specs` đọc từ đây.
- `openspec/changes/<change-name>/` là change proposal hoặc stage work. Lệnh
  `openspec list` đọc các change đang nằm trực tiếp trong `changes/`.
- `openspec/changes/archive/` dành cho change đã archive theo workflow
  OpenSpec.

## Stage Hiện Có

- `stage1-foundation`: lưu lịch sử Stage 1, gồm schema/spec foundation và team
  handoff đã hoàn thành.
- `stage2-core-sample-pipeline`: Stage 2 hiện tại, gồm parser edge extraction,
  Kafka/Spark runtime, Neo4j/MongoDB sample ingestion, và evidence ban đầu.

## Lệnh Kiểm Tra

```bash
openspec doctor
openspec list
openspec list --specs
openspec validate --all --strict
```

## Quy Tắc Làm Việc

- Không sửa `schemas/cpg-events.schema.json` nếu chưa có approval của Tri.
- Nếu thay đổi requirement đã chấp nhận, tạo hoặc cập nhật change trong
  `openspec/changes/<change-name>/specs/<capability>/spec.md`.
- Khi change được chấp nhận, cập nhật current spec tương ứng trong
  `openspec/specs/`.
- Evidence phải là output thật từ command, query, notebook, hoặc screenshot.
  Không publish secret, token, thông tin máy cá nhân không liên quan, hoặc dữ
  liệu nhạy cảm.
