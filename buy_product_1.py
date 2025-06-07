import asyncio
from playwright.async_api import async_playwright

PRODUCT_KEYWORD = "windstopper"
PRODUCT_COLOR_INDEX = 3
PRODUCT_SIZE_LABEL = "XLarge"

async def find_product(page, keyword):
    await page.goto("https://jp.supreme.com/pages/shop")
    await page.wait_for_selector("li[data-testid='image']")
    products = await page.locator("li[data-testid='image']").all()

    print(f"\n🔍 Tìm từ khoá: {keyword} (tổng {len(products)} sản phẩm)")
    for product in products:
        title = await product.locator("a").get_attribute("title")
        if title and keyword.lower() in title.lower():
            link = await product.locator("a").get_attribute("href")
            return f"https://jp.supreme.com{link}", title
    return None, None

async def apply_stealth(page):
    # 🚫 Tắt WebDriver + Fake Permissions
    await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.navigator.chrome = { runtime: {} };
    Object.defineProperty(navigator, 'languages', { get: () => ['ja-JP', 'en-US'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
    """)

async def main():
    async with async_playwright() as p:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

        browser = await p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized"
        ])

        context = await browser.new_context(
            user_agent=user_agent,
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            geolocation={"longitude": 139.6917, "latitude": 35.6895},  # Tokyo
            permissions=["geolocation"]
        )

        page = await context.new_page()
        await apply_stealth(page)

        # 🔍 Tìm sản phẩm
        link, title = await find_product(page, PRODUCT_KEYWORD)
        if not link:
            print("❌ Không tìm thấy sản phẩm phù hợp.")
            await browser.close()
            return

        print(f"\n✅ Mở sản phẩm: {title}\n👉 Link: {link}")
        await page.goto(link)
        await page.wait_for_selector("select[name='size']")

        # 🎨 Chọn màu
        color_buttons = await page.locator('button[data-testid^="thumbnail-button"]').all()
        if PRODUCT_COLOR_INDEX < len(color_buttons):
            await color_buttons[PRODUCT_COLOR_INDEX].click()
            print(f"🎨 Đã chọn màu thứ {PRODUCT_COLOR_INDEX}")
            await page.wait_for_timeout(1000)
        else:
            print("⚠️ Không có đủ màu để chọn.")
            await browser.close()
            return

        # 📏 Chọn size
        print(f"📏 Chọn size: {PRODUCT_SIZE_LABEL}")
        await page.select_option("select[name='size']", label=PRODUCT_SIZE_LABEL)

        # 🛒 Thêm vào giỏ
        await page.click('button[data-testid="add-to-cart-button"]')
        print("🛒 Đã thêm vào giỏ hàng")

        # 💳 Chuyển sang thanh toán
        await page.click('a[data-testid="mini-cart-checkout-link"]')
        print("💳 Đã chuyển sang trang thanh toán")

        await asyncio.sleep(20)
        await browser.close()

asyncio.run(main())
