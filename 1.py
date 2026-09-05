from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re


# ==================================================
# 1. CHẠY CHROME NGẦM
# ==================================================

options = webdriver.ChromeOptions()

options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    options=options
)


# ==================================================
# 2. MỞ TRANG KHÁCH SẠN ĐÀ NẴNG
# ==================================================

city_url = "https://www.agoda.com/vi-vn/city/hue-vn.html?ds=zPYYl3dHlYYWweDD"

driver.get(city_url)

time.sleep(8)


# Cuộn xuống để khách sạn được load thêm
driver.execute_script(
    "window.scrollTo(0, document.body.scrollHeight)"
)

time.sleep(5)


html = driver.page_source

soup = BeautifulSoup(
    html,
    "html5lib"
)


# ==================================================
# 3. LẤY LINK 5 KHÁCH SẠN
# ==================================================

hotel_links = []


for a in soup.find_all(
    "a",
    href=True
):

    href = a["href"]

    # Chỉ lấy link khách sạn
    if "/hotel/" in href:

        # Nếu link chưa có domain
        if href.startswith("/"):
            href = (
                "https://www.agoda.com"
                + href
            )

        # Không lấy link bị trùng
        if href not in hotel_links:
            hotel_links.append(href)


# Chỉ lấy 5 khách sạn
hotel_links = hotel_links[:5]


print(
    "Số khách sạn lấy được:",
    len(hotel_links)
)


# ==================================================
# 4. CÀO TỪNG KHÁCH SẠN
# ==================================================

for stt, hotel_url in enumerate(
    hotel_links,
    start=1
):

    print("\n\n")
    print("==========================================")
    print("KHÁCH SẠN", stt)
    print("==========================================")


    driver.get(
        hotel_url
    )

    time.sleep(7)


    # Cuộn xuống để Agoda load review
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight)"
    )

    time.sleep(5)


    hotel_html = driver.page_source

    hotel_soup = BeautifulSoup(
        hotel_html,
        "html5lib"
    )


    # ==================================================
    # 5. TÊN KHÁCH SẠN
    # ==================================================

    ten = hotel_soup.select_one(
        '[data-selenium="hotel-header-name"]'
    )


    if ten != None:

        ten_co_so = ten.get_text(
            " ",
            strip=True
        )

    else:

        # Nếu Agoda đổi selector
        h1 = hotel_soup.find("h1")

        if h1 != None:
            ten_co_so = h1.get_text(
                " ",
                strip=True
            )
        else:
            ten_co_so = "Không tìm thấy"


    # ==================================================
    # 6. SỐ SAO
    # ==================================================

    star_box = hotel_soup.select_one(
        '[data-element-name="mosaic-hotel-rating-container"]'
    )


    so_sao = ""


    if star_box != None:

        star_text = star_box.get(
            "aria-label",
            ""
        )

        result = re.search(
            r"\d+(?:[.,]\d+)?",
            star_text
        )

        if result != None:
            so_sao = result.group()


    # # ==================================================
    # # 7. ĐIỂM ĐÁNH GIÁ TỔNG THỂ
    # # ==================================================

    # diem_co_so = hotel_soup.select_one(
    #     '[data-element-name="review-score"]'
    # )

    # if diem_co_so == None:

    #     diem_co_so = hotel_soup.select_one(
    #         '[data-selenium="review-score"]'
    # )


    # if diem_co_so != None:

    #     diem_tong = diem_co_so.get_text(
    #         " ",
    #         strip=True
    #     )

    # else:

    #     diem_tong = "Không tìm thấy"


    # ==================================================
    # IN THÔNG TIN CƠ SỞ
    # ==================================================

    print(
        "Tên cơ sở:",
        ten_co_so
    )

    print(
        "Số sao:",
        so_sao
    )
    # ==================================================
    # 7. ĐIỂM ĐÁNH GIÁ TỔNG THỂ
    # ==================================================

    diem_co_so = hotel_soup.select_one(
        '[data-testid="review-plate-redesign-score"] h1'
    )

    if diem_co_so != None:

        diem_tong = diem_co_so.get_text(
            strip=True
        )

    else:

        diem_tong = "Không tìm thấy"

    print(
        "Điểm tổng thể:",
        diem_tong
    )


    # ==================================================
    # 8. TÌM REVIEW
    # ==================================================

    reviews = hotel_soup.select(
        "div.Review-comment"
    )


    print(
        "Số review tìm thấy:",
        len(reviews)
    )


    # ==================================================
    # 9. LẤY 5 REVIEW ĐẦU TIÊN
    # ==================================================

    for i, review in enumerate(
        reviews[:5],
        start=1
    ):

        print("\n---------- REVIEW", i, "----------")


        # --------------------------
        # Điểm review
        # --------------------------

        diem = review.select_one(
            ".Review-comment-leftScore"
        )

        if diem != None:

            print(
                "Điểm review:",
                diem.get_text(
                    strip=True
                )
            )


        # --------------------------
        # Quốc tịch
        # --------------------------

        reviewer = review.select_one(
            ".Review-comment-reviewer"
        )


        if reviewer != None:

            text = reviewer.get_text(
                " ",
                strip=True
            )

            print(
                "Khách hàng:",
                text
            )


        # --------------------------
        # Đi theo
        # --------------------------

        di_theo = review.select_one(
            '[data-info-type="group-name"]'
        )


        if di_theo != None:

            print(
                "Đi theo:",
                di_theo.get_text(
                    " ",
                    strip=True
                )
            )


        # --------------------------
        # Loại phòng
        # --------------------------

        phong = review.select_one(
            '[data-info-type="room-type"]'
        )


        if phong != None:

            print(
                "Loại phòng:",
                phong.get_text(
                    " ",
                    strip=True
                )
            )


        # --------------------------
        # Thời điểm review
        # --------------------------

        ngay = review.select_one(
            ".Review-comment-bubble span"
        )


        if ngay != None:

            print(
                "Thời điểm review:",
                ngay.get_text(
                    " ",
                    strip=True
                )
            )


        # --------------------------
        # Nội dung review
        # --------------------------

        noi_dung = review.select_one(
            ".Review-comment-bodyText"
        )


        if noi_dung != None:

            print(
                "Nội dung:",
                noi_dung.get_text(
                    " ",
                    strip=True
                )
            )


# ==================================================
# 10. ĐÓNG SELENIUM
# ==================================================

driver.quit()