"""Bộ hàm gộp để ôn thi KPW. Khi thi: copy hàm cần dùng, đổi tên cột / đường dẫn theo đề."""
import os, re
from collections import Counter
import pandas as pd
from bs4 import BeautifulSoup


# ============ CHƯƠNG 2: SCRAPE ============
def scrape_cards(files, card_sel, fields, parser="html5lib"):
    """Duyệt nhiều file HTML, lấy các trường trong mỗi thẻ.
    fields = {"ten_sp": ".ten-sp", "gia_goc": ".gia-goc", ...}; thẻ thiếu -> ""."""
    rows = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            soup = BeautifulSoup(f, parser)
        for card in soup.select(card_sel):
            row = {}
            for name, sel in fields.items():
                tag = card.select_one(sel)
                row[name] = tag.get_text(strip=True) if tag else ""
            rows.append(row)
    return pd.DataFrame(rows, columns=list(fields))


def to_int(s):
    """'25.990.000đ' -> 25990000"""
    d = re.sub(r"\D", "", str(s))
    return int(d) if d else None


def clean_prices(df, goc="gia_goc", ban="gia_ban", km="khuyen_mai",
                 km_trong="Không có khuyến mại"):
    """Làm sạch giá + tính tỷ lệ giảm (Câu 1c)."""
    out = pd.DataFrame()
    out["ten_sp"] = df["ten_sp"]
    out["gia_goc_vnd"] = df[goc].map(to_int)
    out["gia_ban_vnd"] = df[ban].map(to_int)
    out["khuyen_mai"] = df[km].fillna("").replace("", km_trong)
    out["ty_le_giam"] = ((out.gia_goc_vnd - out.gia_ban_vnd) / out.gia_goc_vnd * 100).round(2)
    return out


# ============ CHƯƠNG 3: TIỀN XỬ LÝ ============
def load_stopwords(path):
    with open(path, encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip()}


def load_map(path, col_key, col_val):
    """emoji_map.csv / tu_dien_chuan_hoa.csv -> dict (khóa dài thay trước)."""
    df = pd.read_csv(path, encoding="utf-8")
    d = dict(zip(df[col_key].astype(str), df[col_val].astype(str)))
    return dict(sorted(d.items(), key=lambda kv: -len(kv[0])))


def clean_basic(t, lower=True, html=True, url=True, digit=True):
    """Ý a: lower + HTML + URL + số + khoảng trắng (GIỮ emoji, dấu câu)."""
    t = str(t)
    if html:
        t = BeautifulSoup(t, "html.parser").get_text(" ")
    if lower:
        t = t.lower()
    if url:
        t = re.sub(r"(https?://|www\.)\S+", " ", t)
    if digit:
        t = re.sub(r"\d+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def normalize(t, mapping=None, dash_join=False, punct=True):
    """Ý b: thay emoji/chuẩn hóa theo dict -> xóa dấu câu -> khoảng trắng.
    dash_join=True: 'check-in' -> 'checkin' (bỏ gạch nối TRƯỚC khi xóa dấu câu)."""
    if dash_join:
        t = re.sub(r"(?<=\w)-(?=\w)", "", t)
    for k, v in (mapping or {}).items():
        if k.isalnum():  # từ chữ: thay theo ranh giới từ
            t = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", f" {v} ", t)
        else:            # emoji / emoticon: thay thẳng
            t = t.replace(k, f" {v} ")
    if punct:
        t = re.sub(r"[^\w\s]|_", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def tokenize(t, stop=None, lang="vi"):
    """Ý c: tách từ + bỏ stopword -> chuỗi token cách nhau bằng dấu cách."""
    if lang == "vi":
        from underthesea import word_tokenize
        toks = word_tokenize(t, format="text").split()
    else:
        toks = t.split()
    if stop:
        toks = [w for w in toks if w not in stop]
    return " ".join(toks)


def preprocess_full(t, stop=None, mapping=None, lang="vi"):
    """Một phát xong tất cả (kiểu 10_Cau1/Cau2, GK a)."""
    return tokenize(normalize(clean_basic(t), mapping), stop, lang)


def preprocess_folder(in_dir, out_dir, func, prefix="STT_Pre"):
    """Xử lý hàng loạt *.txt -> <prefix>1.txt, <prefix>2.txt ..."""
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(f for f in os.listdir(in_dir) if f.endswith(".txt"))
    for i, fn in enumerate(files, 1):
        with open(os.path.join(in_dir, fn), encoding="utf-8") as f:
            res = func(f.read())
        with open(os.path.join(out_dir, f"{prefix}{i}.txt"), "w", encoding="utf-8") as o:
            o.write(res)


def apply_step(in_csv, out_csv, col_in, col_out, func, id_col="id"):
    """Đọc csv bước trước -> áp func -> lưu csv bước sau (buoc1/2/3)."""
    df = pd.read_csv(in_csv, encoding="utf-8")
    res = pd.DataFrame({id_col: df[id_col], col_out: df[col_in].fillna("").map(func)})
    res.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return res


# ============ THỐNG KÊ + TRỰC QUAN ============
def top_freq(series_or_list, n=10, out_csv=None):
    """Đếm unigram; sắp giảm theo tần suất, hòa thì tăng theo token."""
    toks = [w for s in series_or_list for w in str(s).split()]
    c = Counter(toks)
    top = sorted(c.items(), key=lambda x: (-x[1], x[0]))[:n]
    df = pd.DataFrame(top, columns=["token", "tan_suat"])
    if out_csv:
        df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return df, c


def plot_top(df, png, title="Top token"):
    import matplotlib.pyplot as plt
    d = df.iloc[::-1]
    plt.figure(figsize=(8, 5))
    plt.barh(d["token"], d["tan_suat"])
    plt.title(title)
    plt.tight_layout()
    plt.savefig(png, dpi=150)
    plt.close()


def make_wordcloud(counter, png, font_path=None):
    from wordcloud import WordCloud
    WordCloud(width=1000, height=500, background_color="white",
              font_path=font_path).generate_from_frequencies(counter).to_file(png)


def comment_top(df, ids=None):
    """Sinh sẵn 2 nhận xét theo khung note.txt (chỉ nói tần suất, không nói cảm xúc)."""
    t = df.iloc[0]
    s = f"Nhận xét 1: Token '{t.token}' đứng đầu với tần suất {t.tan_suat}"
    if len(df) > 1 and df.iloc[1].tan_suat:
        s += f", gấp {t.tan_suat / df.iloc[1].tan_suat:.1f} lần hạng 2"
    s += ". Chủ đề này được nhắc tới nhiều nhất trong tập đánh giá."
    same = df[df.tan_suat == df.iloc[1].tan_suat].token.tolist()
    s += (f"\nNhận xét 2: Các token {', '.join(same)} cùng tần suất {df.iloc[1].tan_suat}, "
          "lặp lại nhiều lần nhưng thấp hơn token đứng đầu.")
    return s


# ============ CHƯƠNG 4: ĐẶC TRƯNG ============
def features(docs, method="bow", ngram=(1, 1), names=None, xlsx=None):
    """method: onehot | bow | ngram | tfidf -> DataFrame (docs là list chuỗi)."""
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    v = {"onehot": CountVectorizer(binary=True),
         "bow": CountVectorizer(),
         "ngram": CountVectorizer(ngram_range=ngram if ngram != (1, 1) else (1, 2)),
         "tfidf": TfidfVectorizer()}[method]
    X = v.fit_transform(docs)
    df = pd.DataFrame(X.toarray(), columns=v.get_feature_names_out(),
                      index=names or [f"d{i+1}" for i in range(len(docs))])
    if xlsx:
        df.to_excel(xlsx, index_label="Document")
    return df


# ============ CHƯƠNG 5: TƯƠNG ĐỒNG + PHÂN CỤM ============
def jaccard(a, b):
    a, b = set(a.lower().split()), set(b.lower().split())
    return len(a & b) / len(a | b)


def cosine_matrix(docs):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity(TfidfVectorizer().fit_transform(docs))


def cluster(docs, k=None, k_max=6, show_elbow=True):
    """Tf-idf + (Elbow nếu k=None) + KMeans -> nhãn cụm."""
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    X = TfidfVectorizer().fit_transform(docs)
    if k is None and show_elbow:
        import matplotlib.pyplot as plt
        ks = range(2, min(k_max, X.shape[0]))
        w = [KMeans(n_clusters=i, n_init=10, random_state=0).fit(X).inertia_ for i in ks]
        plt.plot(list(ks), w); plt.xlabel("k"); plt.ylabel("WCSS"); plt.show()
        return None
    return KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).labels_


# ============ CHƯƠNG 6: PHÂN LỚP ============
def classify(texts, labels, vec="bow", model="lr", test_size=0.33, seed=123):
    """Split -> vectorize (fit trên train) -> fit -> đánh giá."""
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
    Xtr, Xte, ytr, yte = train_test_split(texts, labels, test_size=test_size, random_state=seed)
    v = CountVectorizer() if vec == "bow" else TfidfVectorizer()
    Xtr_v = v.fit_transform(Xtr)
    Xte_v = v.transform(Xte)
    m = LogisticRegression(max_iter=1000) if model == "lr" else MultinomialNB()
    m.fit(Xtr_v, ytr)
    pred = m.predict(Xte_v)
    print(confusion_matrix(yte, pred))
    print("accuracy:", accuracy_score(yte, pred))
    print(classification_report(yte, pred))
    return v, m
