"""Chapter 3 Vietnamese text preprocessing exercise.

Run from Baitap/chuong3:
    py nlp.py --input data_raw.txt
"""

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import emoji
import matplotlib.pyplot as plt
from underthesea import word_tokenize
from wordcloud import WordCloud


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_FILE = SCRIPT_DIR / "data_raw.txt"
DEFAULT_STOPWORDS = {"và", "là", "của", "có", "cho", "với", "một", "những", "các"}

ABBREVIATIONS = {
    "nckh": "nghiên cứu khoa học",
    "nntn": "ngôn ngữ tự nhiên",
    "xhcn": "xã hội chủ nghĩa",
    "cntt": "công nghệ thông tin",
    "ai": "trí tuệ nhân tạo",
    "ml": "học máy",
    "nlp": "xử lý ngôn ngữ tự nhiên",
    "ko": "không",
    "dc": "được",
    "mik": "mình",
    "sp": "sản phẩm",
    "ib": "nhắn tin",
}

SPELLING_CORRECTIONS = {
    "sữ dụng": "sử dụng",
    "trãi nghiệm": "trải nghiệm",
    "sữ lý": "xử lý",
    "hiêu quả": "hiệu quả",
}

EMOTICONS = {
    ":-)": " vui ", ":)": " vui ", ":-d": " rất vui ", ":d": " rất vui ",
    ":-(": " buồn ", ":(": " buồn ", ";-)": " nháy mắt ", ";)": " nháy mắt ",
    ":-p": " trêu đùa ", ":p": " trêu đùa ",
}


def read_text(file_path: Path) -> str:
    """Read one non-empty UTF-8 text file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Khong tim thay file: {file_path}")

    text = file_path.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise ValueError("File dau vao dang rong.")
    return text


def load_stopwords(file_path: Path) -> set[str]:
    """Read one stop word per line; use a small default list when absent."""
    if not file_path.exists():
        return DEFAULT_STOPWORDS

    return {
        re.sub(r"\s+", "_", line.strip().lower())
        for line in file_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    }


def remove_urls(text: str) -> str:
    return re.sub(r"(?:https?://|www\.)\S+", " ", text, flags=re.IGNORECASE)


def replace_emoticons(text: str) -> str:
    pattern = re.compile("|".join(re.escape(item) for item in EMOTICONS), re.IGNORECASE)
    return pattern.sub(lambda match: EMOTICONS[match.group().lower()], text)


def replace_emojis(text: str) -> str:
    text = emoji.demojize(text, language="en")
    return text.replace(":", " ").replace("_", " ")


def expand_abbreviations(text: str) -> str:
    pattern = re.compile(r"\b(" + "|".join(ABBREVIATIONS) + r")\b", re.IGNORECASE)
    return pattern.sub(lambda match: ABBREVIATIONS[match.group().lower()], text)


def correct_spelling(text: str) -> str:
    for wrong, right in SPELLING_CORRECTIONS.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text, flags=re.IGNORECASE)
    return text


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+|\n+", text) if sentence.strip()]


def remove_punctuation(text: str) -> str:
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.replace("_", " ")


def remove_numbers(text: str) -> str:
    return re.sub(r"\d+", " ", text)


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_tokens(tokens: list[str]) -> list[str]:
    normalized = []
    for token in tokens:
        token = token.lower().strip()
        if len(token) > 1 and re.search(r"[a-zA-ZÀ-ỹ]", token):
            normalized.append(token)
    return normalized


def clear_old_outputs(output_dir: Path, prefix: str) -> None:
    """Remove only old files generated for the current input filename."""
    if output_dir.exists():
        for old_file in output_dir.glob(f"{prefix}_*"):
            if old_file.is_file():
                old_file.unlink()


def save_frequency_csv(frequencies: list[tuple[str, int]], file_path: Path) -> None:
    with file_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["word", "frequency"])
        writer.writerows(frequencies)


def save_frequency_chart(frequencies: list[tuple[str, int]], file_path: Path) -> None:
    words, counts = zip(*frequencies)
    plt.figure(figsize=(12, 6))
    plt.bar(words, counts)
    plt.title("Tan suat xuat hien cua cac tu")
    plt.xlabel("Tu")
    plt.ylabel("Tan suat")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()


def save_wordcloud(frequency_data: Counter, file_path: Path) -> None:
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        collocations=False,
        font_path=str(font_path) if font_path.exists() else None,
    ).generate_from_frequencies(frequency_data)
    plt.figure(figsize=(15, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chapter 3 Vietnamese text preprocessing")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_FILE)
    parser.add_argument("--output", type=Path, default=SCRIPT_DIR / "ket_qua")
    parser.add_argument("--top", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.top < 1:
        raise ValueError("--top phai lon hon 0.")

    raw_text = read_text(args.input)
    stopwords = load_stopwords(SCRIPT_DIR / "vietnamese-stopwords.txt")

    # Chuyen chu thuong va xoa URL.
    text = raw_text.lower()
    text = remove_urls(text)

    # Doi emoji/emoticon, chuan hoa viet tat va sua chinh ta.
    text = replace_emoticons(text)
    text = replace_emojis(text)
    text = expand_abbreviations(text)
    text = correct_spelling(text)

    # Tach cau truoc khi xoa dau cau de giu ranh gioi cau.
    sentences = split_sentences(text)

    # Xoa dau cau, chu so va chuan hoa khoang trang.
    text = remove_punctuation(text)
    text = remove_numbers(text)
    text = normalize_spaces(text)

    # Tach tu, xoa stop words va chuan hoa token.
    tokens = word_tokenize(text, format="text").split()
    tokens = [token for token in tokens if token.lower() not in stopwords]
    tokens = normalize_tokens(tokens)

    if not tokens:
        raise ValueError("Khong con token sau tien xu ly.")

    frequencies = Counter(tokens)
    top_frequencies = frequencies.most_common(args.top)

    args.output.mkdir(parents=True, exist_ok=True)
    clear_old_outputs(args.output, args.input.stem)
    prefix = args.input.stem
    (args.output / f"{prefix}_txl.txt").write_text(" ".join(tokens), encoding="utf-8")
    save_frequency_csv(top_frequencies, args.output / f"{prefix}_frequency.csv")
    save_frequency_chart(top_frequencies, args.output / f"{prefix}_frequency.png")
    save_wordcloud(frequencies, args.output / f"{prefix}_wordcloud.png")

    print("DA HOAN THANH TIEN XU LY")
    print(f"So cau: {len(sentences)}")
    print(f"So token sau xu ly: {len(tokens)}")
    print("Top tu xuat hien nhieu nhat:")
    for word, count in top_frequencies:
        print(f"- {word}: {count}")
    print(f"Da luu ket qua tai: {args.output.resolve()}")


if __name__ == "__main__":
    main()
