# Dự đoán đề thực hành cuối kỳ

> Đây là suy luận từ tài liệu môn học, **thầy chưa xác nhận**. Mức khả năng và số bài luyện là đánh giá cá nhân.

**Đã biết:** thi lập trình trên máy, cuối kỳ chiếm 60%, không có mạng, được mở code cũ, đề random, thầy nói thi theo dạng `C5_phan_cum_tuong_dong/02_kmeans_475_van_ban/de_bai.pdf`.

**Dự đoán:** một bộ dữ liệu và 3–4 ý nối tiếp nhau, mỗi đề xoay quanh một dạng bài chính.

## Căn cứ

| Nguồn | Cấu trúc | Rút ra |
|---|---|---|
| `de_bai.pdf` (C5) | 1 bộ dữ liệu, 3 ý a, b, c | Ý sau dùng kết quả ý trước |
| Bài C4 | Câu 1 tiền xử lý, Câu 2 khám phá dữ liệu, Câu 3 gồm BoW, N-gram, TF-IDF | Có thể ra dạng 3 câu, nhiều ý nhỏ |
| `de_d1_d2.xlsx` (C4) | BoW và TF-IDF cho 2 câu, tính theo từng bước | TF-IDF có thể bám công thức trong slide |
| Đề giữa kỳ | 2–3 câu, tên file kết quả quy định rõ | Phải làm đúng tên và định dạng đầu ra |
| Slide Chương 6, 7 | 4 thuật toán phân lớp; gợi ý content-based, user-based, item-based | Các dạng có thể được random |

## Khả năng ra và số bài luyện

| Khối | Khả năng | Ý có thể gặp | Số bài | Bài luyện |
|---|---|---|---|---|
| Đọc và tiền xử lý | Cao, có thể là ý phụ | Đọc nhiều file, làm sạch, tách từ | 2 | 475 văn bản; `Data1` của C4 |
| Đặc trưng (C4) | Cao | BoW, N-gram, TF-IDF, từ nổi bật | 4 | 3 kỹ thuật trên `Data_Preprocessing`; 1 bài TF-IDF theo công thức |
| Phân cụm (C5) | Rất cao | Chọn K, K-Means, in theo mẫu | 2 | 475 văn bản; `Data_Preprocessing` của C4 |
| Tương đồng (C5) | Rất cao | Top 5 cặp bằng 1 trong 3 độ đo | 3 | Mỗi độ đo 1 bài |
| Phân lớp (C6) | Trung bình đến cao | Chia train/test, huấn luyện, so sánh mô hình | 2 | `spam.csv`; `Review.zip` với 4 thuật toán |
| Gợi ý (C7) | Trung bình | Dự đoán rating còn trống | 4 | 2 bài content-based; 1 user-based; 1 item-based |
| Crawl web (C2) | Thấp | Chỉ có thể là bóc tách HTML offline | 1 | Đề 1 giữa kỳ |

Tổng cộng khoảng 18 bài theo khối và 4 đề thử.

## 4 đề thử dự đoán

### Đề A: Phân cụm và tương đồng

- a. Dùng Elbow và Silhouette để xác định K.
- b. Chạy K-Means và in các cụm theo mẫu.
- c. In top 5 cặp tương đồng nhất bằng Jaccard hoặc Euclidean.

### Đề B: Đặc trưng và phân cụm

- a. Tiền xử lý thư mục văn bản và lưu mỗi file riêng.
- b. Xây dựng BoW và bigram, lưu ra CSV, in kích thước ma trận.
- c. Xây dựng TF-IDF và in 10 từ có điểm cao nhất của một văn bản.
- d. Phân cụm bằng TF-IDF, in từ nổi bật của từng cụm rồi đặt tên chủ đề.

### Đề C: Phân lớp

- a. Đọc thư mục `neg` và `pos`, tiền xử lý, chia 67% train và 33% test.
- b. Dùng BoW với Logistic Regression, in confusion matrix và accuracy.
- c. So sánh Naive Bayes, SVM, Random Forest, KNN theo precision, recall, F1.
- d. Dự đoán nhãn cho một câu mới và nêu mô hình tốt nhất.

### Đề D: Hệ gợi ý

- a. Tính ma trận tương đồng giữa các user từ bảng rating.
- b. Dự đoán các ô `?` bằng User-Based CF.
- c. Làm lại bằng Item-Based CF và so sánh kết quả.

## Bẫy dễ mất điểm

- **TF-IDF:** slide dùng `TF = số lần / tổng số từ` và `IDF = log10(N/df)`. `TfidfVectorizer` mặc định làm trơn IDF, dùng log tự nhiên và chuẩn hóa vector, nên ra số khác. Nếu đề bắt tính theo slide, dùng cách viết tay như `Exam44a`.
- **Phân lớp:** chỉ `fit` vectorizer trên tập train. Với dữ liệu tiếng Việt, bỏ regex `[^a-zA-Z]` của `Exam61`.
- **Gợi ý:** `Web_Mining_Class` không có code mẫu, và phải xử lý đúng ô rating trống.
- **Đề ghép:** in kích thước `X` sau mỗi bước, giữ `names` cùng thứ tự với `docs`.

## Thứ tự ôn

1. **Gợi ý:** viết khung trước vì chưa có code, rồi đối chiếu với bài giải trong slide.
2. **Phân lớp:** làm `spam.csv`, sau đó `Review.zip`.
3. **Đặc trưng:** tập trung vào phần TF-IDF theo công thức.
4. **Đề B và Đề C có bấm giờ:** đây là hai dạng chưa có bài hoàn chỉnh.
5. **Đề A trên `Data_Preprocessing` của C4:** kiểm tra khung K-Means với dữ liệu mới.
6. **Đề D lần cuối:** không xem bài giải.

Nếu ít thời gian, ưu tiên mỗi đề A, B, C, D làm một lần.

## Cần hỏi thầy

- Mỗi đề chỉ có một dạng bài, hay ghép nhiều chương?
- TF-IDF chấm theo công thức slide hay chấp nhận kết quả từ `sklearn`?
- Thời gian làm bài bao lâu, nộp một notebook hay mỗi câu một file?
