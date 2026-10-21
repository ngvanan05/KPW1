"""
Crawl review khách sạn Huế trên Agoda
Môn ELC3009 - Khai phá dữ liệu Web (Chương 2: Thu thập & trích xuất dữ liệu Web)

Mục tiêu: lấy top 10 khách sạn ở Huế, mỗi khách sạn gồm:
- Tên cơ sở, số sao, điểm đánh giá tổng thể
- ~15 review: nội dung, điểm, thời điểm, quốc tịch, loại phòng, hình thức đi cùng

Output: 1 file agoda_hue_reviews.txt duy nhất, các khách sạn nối tiếp nhau.

LƯU Ý QUAN TRỌNG: các dòng có "# TODO" là những chỗ cần bạn tự xác định selector
bằng cách bấm chuột phải > Inspect trên trang Agoda thật (đúng kỹ thuật Chapter 2 dạy),
vì Agoda dùng class CSS dạng hash ngẫu nhiên, có thể khác nhau tùy thời điểm/khu vực.
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ============ CẤU HÌNH ============
SO_KHACH_SAN = 10       # số lượng khách sạn muốn lấy (đổi thành 2 để test trước)
SO_REVIEW_MOI_KS = 15   # ~1 trang modal mặc định
OUTPUT_FILE = "agoda_hue_reviews.txt"

# URL search Huế (đã xác định cityId=3738 khi test thủ công)
SEARCH_URL = (
    "https://www.agoda.com/vi-vn/search?city=3738"
    "&checkIn=2026-09-14&checkOut=2026-09-15&rooms=1&adults=2&children=0"
)


# ============ BƯỚC 1: LẤY DANH SÁCH KHÁCH SẠN ============
def lay_danh_sach_khach_san(driver, wait, so_luong=10):
    """Tìm tất cả thẻ <a> có href chứa '/hotel/' (pattern URL khách sạn Agoda,
    đã xác nhận thực tế dạng '/vi-vn/ten-khach-san/hotel/hue-vn.html').
    Cách này bền hơn dò class vì URL pattern ít đổi hơn class CSS."""
    driver.get(SEARCH_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(5)  # đợi JS render danh sách khách sạn (trang dùng lazy-load)

    links = driver.find_elements(By.XPATH, "//a[contains(@href,'/hotel/')]")

    ds_khach_san = []
    da_them = set()
    for a in links:
        href = a.get_attribute("href")
        ten = a.text.strip()
        if not href or not ten:
            continue
        if href in da_them:
            continue
        da_them.add(href)
        ds_khach_san.append({"ten": ten, "url": href})
        if len(ds_khach_san) >= so_luong:
            break
    return ds_khach_san


# ============ BƯỚC 2: THÔNG TIN CƠ SỞ + REVIEW ============
def lay_thong_tin_co_so(driver):
    """Lấy số sao và điểm đánh giá tổng thể từ đầu trang khách sạn."""
    so_sao = None
    diem_tong = None
    try:
        # TODO: xác định selector chính xác cho khối sao (thường là 1 cụm icon sao
        # cạnh tên khách sạn). Gợi ý: Inspect ngay cạnh chữ tên KS, tìm phần tử lặp lại N lần.
        sao_elements = driver.find_elements(By.XPATH, "//*[contains(@aria-label,'sao')]")
        if sao_elements:
            m = re.search(r"(\d)\s*sao", sao_elements[0].get_attribute("aria-label") or "")
            if m:
                so_sao = m.group(1)
    except Exception:
        pass

    try:
        # Điểm tổng thể là số dạng "9,4" ngay phía trên chữ "Trên cả tuyệt vời"/tương tự
        # TODO: xác định selector chính xác. Tạm dùng regex trên toàn bộ text trang.
        body_text = driver.find_element(By.TAG_NAME, "body").text
        m = re.search(r"(\d,\d)\s*\n?\s*(Trên cả tuyệt vời|Tuyệt vời|Rất tốt|Tốt)", body_text)
        if m:
            diem_tong = m.group(1)
    except Exception:
        pass

    return so_sao, diem_tong


def mo_modal_danh_gia(driver, wait):
    tab_danh_gia = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[self::a or self::button][contains(text(),'Đánh giá')]"))
    )
    tab_danh_gia.click()
    time.sleep(3)  # đợi modal load review


def lay_review_trang_hien_tai(driver):
    """Lấy text thô của các review card đang hiển thị, rồi tách field bằng regex
    dựa trên các cụm từ cố định của Agoda (bền hơn class CSS vì đây là text tiếng Việt
    Agoda hiển thị, ít đổi hơn tên class nội bộ)."""
    # TODO: nếu review nằm trong 1 container modal riêng, thay body bằng container đó
    # để tránh lẫn text của các phần khác trên trang.
    modal_text = driver.find_element(By.TAG_NAME, "body").text

    # Tách theo mốc "Đã nhận xét vào" - mỗi review kết thúc bằng cụm này
    khoi_review = re.split(r"(?=Đã nhận xét vào)", modal_text)

    danh_sach_review = []
    for khoi in khoi_review:
        ngay = re.search(r"Đã nhận xét vào ([\d]{1,2} tháng [\d]{1,2} \d{4})", khoi)
        if not ngay:
            continue  # khối không chứa review hợp lệ, bỏ qua

        diem = re.search(r"^(\d{1,2},\d)", khoi.strip())
        # Danh sách quốc tịch phổ biến - mở rộng thêm nếu gặp quốc tịch khác
        quoc_tich = re.search(
            r"(Việt Nam|Hàn Quốc|Trung Quốc|Nhật Bản|Thái Lan|Hoa Kỳ|Úc|Anh|Pháp|Đức|Singapore|Malaysia)",
            khoi,
        )
        di_theo = re.search(r"(Cặp đôi|Gia đình|Một mình|Nhóm bạn|Doanh nhân)", khoi)
        loai_phong = re.search(r"(Phòng [^\n]+|Suite[^\n]*|Deluxe[^\n]*)", khoi)

        # Nội dung: đoạn văn dài nhất trong khối (heuristic đơn giản)
        dong = [d.strip() for d in khoi.split("\n") if len(d.strip()) > 30]
        noi_dung = dong[0] if dong else ""

        danh_sach_review.append({
            "noi_dung": noi_dung,
            "diem": diem.group(1) if diem else "",
            "ngay": ngay.group(1) if ngay else "",
            "quoc_tich": quoc_tich.group(1) if quoc_tich else "",
            "loai_phong": loai_phong.group(1) if loai_phong else "",
            "di_theo": di_theo.group(1) if di_theo else "",
        })
    return danh_sach_review


# ============ BƯỚC 3: CHẠY TOÀN BỘ ============
def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    print("Selenium sẵn sàng.")

    danh_sach_ks = lay_danh_sach_khach_san(driver, wait, SO_KHACH_SAN)
    for ks in danh_sach_ks:
        print(ks["ten"], "-", ks["url"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for idx, ks in enumerate(danh_sach_ks, start=1):
            print(f"Đang xử lý khách sạn {idx}/{len(danh_sach_ks)}: {ks['ten']}")
            try:
                driver.get(ks["url"])
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(3)

                so_sao, diem_tong = lay_thong_tin_co_so(driver)
                mo_modal_danh_gia(driver, wait)
                reviews = lay_review_trang_hien_tai(driver)[:SO_REVIEW_MOI_KS]

                f.write("===================================\n")
                f.write(f"KHÁCH SẠN {idx}: {ks['ten']}\n")
                f.write("===================================\n")
                f.write(f"Số sao: {so_sao or 'không xác định'}\n")
                f.write(f"Điểm đánh giá tổng thể: {diem_tong or 'không xác định'}\n\n")

                for r_idx, r in enumerate(reviews, start=1):
                    f.write(f"--- Review {r_idx} ---\n")
                    f.write(f"Nội dung: {r['noi_dung']}\n")
                    f.write(f"Điểm tổng thể: {r['diem']}\n")
                    f.write(f"Thời điểm review: {r['ngay']}\n")
                    f.write(f"Quốc tịch: {r['quoc_tich']}\n")
                    f.write(f"Loại phòng: {r['loai_phong']}\n")
                    f.write(f"Đi theo: {r['di_theo']}\n\n")

            except Exception as e:
                print(f"  Lỗi ở khách sạn {ks['ten']}: {e}")
                f.write(f"[LỖI khi crawl khách sạn {ks['ten']}: {e}]\n\n")
                continue

            time.sleep(2)  # delay giữa các khách sạn, tránh request quá nhanh

    driver.quit()
    print("Xong. Kết quả lưu ở:", OUTPUT_FILE)

    # Kiểm tra nhanh kết quả
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        noi_dung = f.read()
    print(noi_dung[:2000])  # xem thử 2000 ký tự đầu


if __name__ == "__main__":
    main()
