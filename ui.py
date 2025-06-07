import asyncio 
import os
from twocaptcha import TwoCaptcha
import gradio as gr
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs

# Lấy API key từ biến môi trường CAPTCHA_API
api_key = os.getenv('CAPTCHA_API', 'YOUR_API_KEY')

# Khởi tạo 2Captcha solver
solver = TwoCaptcha(api_key)

# Hàm giải CAPTCHA
async def solve_captcha(site_key, page_url):
    try:
        result = solver.recaptcha(sitekey=site_key, url=page_url)
        return result['code']
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return None

# Tự động tìm sitekey từ iframe CAPTCHA (nếu có)
async def wait_for_sitekey(page):
    print("⏳ Đang chờ sitekey CAPTCHA...")
    for _ in range(30):  # Đợi tối đa ~30 giây
        try:
            frame = await page.frame_locator('iframe[src*="recaptcha"]').first
            src = await frame.get_attribute('src')
            if src:
                parsed = urlparse(src)
                sitekey = parse_qs(parsed.query)['k'][0]
                print(f"🔥 Tóm được sitekey: {sitekey}")
                return sitekey
        except:
            pass
        await asyncio.sleep(1)
    print("❌ Không tìm thấy sitekey trong thời gian cho phép.")
    return None

# Hàm stealth để giả vờ như trình duyệt không phải tự động
async def apply_stealth(page):
    await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.navigator.chrome = { runtime: {} };
    Object.defineProperty(navigator, 'languages', { get: () => ['ja-JP', 'en-US'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] });
    """)

# Tìm sản phẩm theo từ khóa
async def find_product(page, keyword):
    await page.goto("https://jp.supreme.com/pages/shop")
    await page.wait_for_selector("li[data-testid='image']")
    products = await page.locator("li[data-testid='image']").all()
    for product in products:
        title = await product.locator("a").get_attribute("title")
        if title and keyword.lower() in title.lower():
            link = await product.locator("a").get_attribute("href")
            return f"https://jp.supreme.com{link}", title
    return None, None

# Hàm xử lý toàn bộ quy trình mua hàng
async def bot_runner(keyword, color_index, size_label):
    logs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--start-maximized"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            geolocation={"longitude": 139.6917, "latitude": 35.6895},
            permissions=["geolocation"]
        )
        page = await context.new_page()
        await apply_stealth(page)

        link, title = await find_product(page, keyword)
        if not link:
            logs.append("❌ Không tìm thấy sản phẩm.")
            await browser.close()
            return "\n".join(logs)

        logs.append(f"✅ Tìm thấy sản phẩm: {title}")
        logs.append(f"👉 Link: {link}")
        await page.goto(link)
        await page.wait_for_selector("select[name='size']")

        color_buttons = await page.locator('button[data-testid^="thumbnail-button"]').all()
        if color_index < len(color_buttons):
            await color_buttons[color_index].click()
            logs.append(f"🎨 Đã chọn màu thứ {color_index}")
        else:
            logs.append("⚠️ Không có đủ màu.")
            await browser.close()
            return "\n".join(logs)

        available_sizes = await page.locator("select[name='size'] option").all_text_contents()
        logs.append(f"🧩 Size có sẵn: {available_sizes}")

        preferred_sizes = [size_label, "Large", "Medium", "Small"]
        chosen_size = next((s for s in preferred_sizes if s in available_sizes), None)
        if chosen_size:
            await page.select_option("select[name='size']", label=chosen_size)
            logs.append(f"📏 Đã chọn size: {chosen_size}")
        else:
            logs.append("❌ Không có size nào phù hợp.")
            await browser.close()
            return "\n".join(logs)

        await page.click('button[data-testid="add-to-cart-button"]')
        logs.append("🛒 Đã thêm vào giỏ")
        await page.click('a[data-testid="mini-cart-checkout-link"]')
        logs.append("🛒 Mở mini cart và chọn checkout")

        try:
            checkout_button = page.locator("text=ご注文手続きへ")
            await checkout_button.wait_for(timeout=10000)
            await checkout_button.click()
            logs.append("💳 Đã bấm nút 'Tiến hành đặt hàng'")
            await page.wait_for_url("**/checkout", timeout=10000)
        except Exception as e:
            logs.append("⚠️ Không tìm thấy nút checkout – tiếp tục luôn!")

        captcha_site_key = await wait_for_sitekey(page)
        if captcha_site_key:
            captcha_token = await solve_captcha(captcha_site_key, link)
            if captcha_token:
                await page.evaluate(f"""
                    document.getElementById("g-recaptcha-response").value = "{captcha_token}";
                    document.getElementById("g-recaptcha-response").dispatchEvent(new Event('input', {{ bubbles: true }}));
                """)
                logs.append("🔓 CAPTCHA đã được giải xong")
            else:
                logs.append("⚠️ Không giải được CAPTCHA")
        else:
            logs.append("⚠️ Không tìm được sitekey CAPTCHA")

        await page.fill('input[id="email"]', 'email')
        await page.fill('input[id="TextField0"]', 'bao')
        await page.fill('input[id="TextField1"]', 'ngoc')
        await page.fill('input[id="postalCode"]', '122111')
        await page.select_option('select[id="Select1"]', value='JP')
        await page.fill('input[id="TextField2"]', '122334')
        await page.fill('input[id="TextField3"]', '2-8-21')
        await page.fill('input[id="TextField4"]', 'アーバンコート十三5B')
        await page.fill('input[id="TextField5"]', '0963010737')
        await page.check('input[id="save_shipping_information"]')

        await page.wait_for_selector('input[id="number"]:visible', timeout=60000)
        await asyncio.Event().wait()

        await browser.close()
        return "\n".join(logs)

def launch_bot(keyword, color_index, size_label):
    return asyncio.run(bot_runner(keyword, color_index, size_label))

with gr.Blocks(title="🛍️ Supreme Bot Mua Hàng") as demo:
    gr.Image("image.png", label="", show_label=False, show_download_button=False)
    gr.Markdown("## 💥 Supreme Auto Buyer Bot")
    keyword = gr.Textbox(label="🔍 Nhập từ khoá sản phẩm", placeholder="box logo, hoodie, windstopper...")
    color = gr.Slider(0, 16, value=0, step=4, label="🎨 Chọn màu (theo thứ tự)")
    size = gr.Dropdown(choices=["Small", "Medium", "Large", "XLarge"], value="XLarge", label="📏 Chọn size")
    btn = gr.Button("🔥 Mua ngay!")
    output = gr.Textbox(label="📋 Log")

    btn.click(fn=launch_bot, inputs=[keyword, color, size], outputs=output)

demo.launch()
