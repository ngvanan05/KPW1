# Chuong 3 - Tien xu ly du lieu van ban

`nlp.py` la bai tap tien xu ly tieng Viet theo cac buoc co ban cua Chương 3.
Code chi dung cac thu vien va ky thuat da hoc, viet theo tung buoc de de giai
thich khi bao cao.

## Cai dat thu vien

```powershell
py -m pip install underthesea emoji matplotlib wordcloud
```

## Chay chuong trinh

Tu thu muc `Baitap/chuong3`:

```powershell
py nlp.py --input data_raw.txt --output ket_qua --top 20
```

Neu khong truyen `--input`, chuong trinh doc `data_raw.txt` mac dinh.

Neu `py` bao khong tim thay Python tren may nay, dung lenh PowerShell sau:

```powershell
$python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
& $python nlp.py --input data_raw.txt --output ket_qua --top 20
```

## Quy trinh

```text
Doc file van ban
-> Chuyen chu thuong
-> Xoa URL
-> Xu ly emoji va emoticon
-> Chuan hoa tu viet tat
-> Sua loi chinh ta bang tu dien
-> Tach cau
-> Xoa dau cau
-> Xoa chu so
-> Tach tu voi underthesea
-> Xoa stop words
-> Chuan hoa token
-> Thong ke tan suat
-> Ve bieu do va tao Word Cloud
```

Xu ly emoji/emoticon duoc dat truoc xoa dau cau de emoticon nhu `:)` khong bi
mat. Tach cau cung dat truoc xoa dau cau de giu duoc dau `.`, `?`, `!` khi nhan
biet ranh gioi cau.

## Dau ra

Voi input `data_raw.txt`, chuong trinh tao trong `ket_qua/`:

```text
data_raw_txl.txt
data_raw_frequency.csv
data_raw_frequency.png
data_raw_wordcloud.png
```

`data_raw_txl.txt` la van ban sau tien xu ly. CSV chua top tu xuat hien nhieu
nhat; bieu do dung top N, con Word Cloud dung toan bo tan suat tu sau xu ly.

Truoc khi ghi ket qua moi, chuong trinh chi xoa cac output cu co cung prefix.
Vi du, chay `Cau1.txt` chi xoa `Cau1_*`, khong anh huong `data_raw_*`.

## Luu y

- Danh sach stop word doc tu `vietnamese-stopwords.txt`.
- Tu viet tat va loi chinh ta mau nam trong `ABBREVIATIONS` va
  `SPELLING_CORRECTIONS`; co the bo sung theo du lieu.
- Stemming va Lemmatization cua NLTK phu hop voi tieng Anh, khong ap dung cho
  bai tien xu ly tieng Viet nay.
