# 🛍️ Supreme Auto Buyer Bot

**Tự động săn hàng Supreme Nhật Bản chỉ với một cú click!**

## 📌 Mô tả dự án
Dự án này cung cấp công cụ tự động hóa việc tìm kiếm và mua sản phẩm từ trang web Supreme Nhật Bản (https://jp.supreme.com). Dự án được chia thành hai phần chính:

buy_product.py: Tập lệnh Python sử dụng Playwright và asyncio để thực hiện toàn bộ quy trình mua hàng tự động, từ bước tìm kiếm sản phẩm theo từ khóa, chọn màu sắc, size, thêm vào giỏ hàng, đến khi chuyển sang bước thanh toán.

ui.py: Cung cấp giao diện người dùng thân thiện với Gradio, cho phép người dùng nhập vào các thông số như từ khóa sản phẩm, màu sắc, và size mong muốn. Ngoài ra, script này còn tích hợp giải pháp tự động xử lý CAPTCHA sử dụng dịch vụ 2Captcha và tự động điền các thông tin thanh toán mẫu.

---

## 🧠 Công nghệ sử dụng

| Thành phần         | Mô tả                                                                 |
|--------------------|-----------------------------------------------------------------------|
| `Playwright`       | Điều khiển trình duyệt tự động, tương tác như người thật              |
| `asyncio`          | Xử lý bất đồng bộ các thao tác mạng và DOM                           |
| `Gradio`           | Giao diện người dùng nhanh gọn để nhập keyword, chọn size và màu     |
| `2Captcha`         | Giải CAPTCHA tự động bằng API key                                     |
| `Python 3.10+`     | Toàn bộ script viết bằng Python không đồng bộ (async/await)          |

---

## 📂 Cấu trúc dự án

```
frontend/
│
├── buy_product.py Script điều khiển mua hàng tự động từ A-Z
├── ui.py #Giao diện frontend Gradio + xử lý CAPTCHA
├── .venv/ #Môi trường ảo Python
├── image.png #Ảnh hiển thị giao diện Gradio
└── README.md #Tài liệu mô tả (file này)
```

---

## 🚀 Cài đặt & sử dụng

### 1. Tạo và kích hoạt môi trường ảo

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```
### Tải requirements.txt

```
pip install -r requirements.txt
```

## Các chức năng chính:

Tìm kiếm sản phẩm theo từ khóa người dùng nhập vào.

Chọn màu sắc và size phù hợp với sản phẩm.

Tự động thêm sản phẩm vào giỏ hàng.

Tự động giải CAPTCHA (nếu có) và điền thông tin giao hàng thanh toán mẫu.

Ghi log lại từng bước trong quá trình tự động hóa để theo dõi dễ dàng.


### Tác giả

✌️ bngoc

✉ Email: trbaongoc17@gmail.com

💼 AI Engineer
