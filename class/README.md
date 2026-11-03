# Ôn tập Khai phá dữ liệu Web

Bài tập xếp theo chương. Trong mỗi chương, thư mục đánh số từ cơ bản đến nâng cao.
`Web_Mining_Class/` là tài liệu riêng, không thuộc cách sắp xếp này.

## Thứ tự ôn gợi ý

1. **Làm quen khung bài:** `00_tong_hop/` → `GK_giua_ky/bai_mau/` → `GK_giua_ky/khung_tong_quat/`
2. **Đi theo chương:** C2 → C3 → C4 → C5
3. **Thi thử:** tự làm lại các đề trong `GK_giua_ky/de_thi/`, hoặc chạy bản `*_chu_thich` của C4

## Bản đồ thư mục

| Thư mục | Nội dung |
|---|---|
| `00_tong_hop/` | Bộ hàm dùng lại khi thi; cách viết nhận xét |
| `C2_thu_thap_du_lieu/01_crawl_phan_trang_vnexpress.py` | Lấy link phân trang bằng regex và theo quy tắc URL |
| `C2_thu_thap_du_lieu/02_crawl_agoda_khung_todo/` | Khung crawl Agoda, còn TODO selector để tự điền |
| `C2_thu_thap_du_lieu/03_crawl_agoda_hoan_chinh/` | Bản crawl Agoda hoàn chỉnh và dữ liệu thu được |
| `C3_tien_xu_ly_EDA/01_pipeline_co_ban/` | Quy trình tiền xử lý tiếng Việt, tần suất, word cloud |
| `C3_tien_xu_ly_EDA/02_ota_review_hue/` | Tiền xử lý và EDA review khách sạn Huế |
| `C4_dac_trung_van_ban/01_tinh_tay_tfidf/` | Đề hai câu d1, d2 và bảng tính TF-IDF |
| `C4_dac_trung_van_ban/02_bow_ngram_tfidf/` | BOW, N-grams, TF-IDF trên bộ 172 văn bản |
| `C5_phan_cum_tuong_dong/01_cosine_vnexpress/` | Crawl RSS VnExpress, độ tương đồng cosine |
| `C5_phan_cum_tuong_dong/02_kmeans_475_van_ban/` | Chọn K, K-Means, top cặp văn bản tương đồng |
| `GK_giua_ky/de_thi/` | Các đề giữa kỳ |
| `GK_giua_ky/de1_*`, `de2_*`, `de_vieclam_ktx_*` | Bài làm theo từng đề |
| `GK_giua_ky/ban_nop_zip/` | Bản zip gốc; nội dung một số file khác bản đang giải nén |
| `GK_giua_ky/tham_khao_DoHuuHau/` | Bài tham khảo; Câu 1 dùng dữ liệu Đề 1, Câu 2 dùng dữ liệu Đề 2 |

## Lưu ý

- Mở notebook từ đúng thư mục của nó, vì code dùng đường dẫn tương đối.
- Không đổi tên `Data`, `Data1`, `Data_Preprocessing`, `Cau1`, `Cau2`: code và cấu trúc đề đang dùng các tên này.
- Ở C4, bản `*_chu_thich` và bản đã chạy ghi ra cùng file kết quả, nên chỉ cần chạy một trong hai.
