from playwright.async_api import async_playwright

class FacebookMarketplaceScraper:
    def __init__(self, headless=True):
        self.headless = headless

    async def run(self, playwright, url):
        browser = await playwright.chromium.launch(headless=self.headless)
        page = await browser.new_page()

        await page.goto(url, wait_until='domcontentloaded')
        await page.goto(url, wait_until='networkidle', timeout=60000)  # Timeout in milliseconds
        item_elements = await page.query_selector_all('a[href*="/marketplace/item/"]')
        items = []

        for item_element in item_elements:
            item = {}
            item['page_url'] = await item_element.get_attribute('href')
            image_element = await item_element.query_selector('img[src*="scontent-sjc3"]')
            item['image_url'] = await image_element.get_attribute('src') if image_element else "Image URL not found"
            item['product_name'] = await image_element.get_attribute('alt') if image_element else "Product name not found"
            items.append(item)

        await browser.close()
        return items

    async def scrape(self, url):
        async with async_playwright() as playwright:
            return await self.run(playwright, url)