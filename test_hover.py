import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("file:///Users/jonathanellis/apps/theoryinpractice/tip-animated10.html")
        await page.wait_for_timeout(2000)
        
        # Dispatch mouse move to LA
        await page.hover('.city-item:nth-child(4)')
        await page.wait_for_timeout(1000)

        # Get large elements
        script = """
        () => {
            const all = document.querySelectorAll('*');
            let res = [];
            all.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 200 && rect.width < 800 && rect.height > 200 && rect.height < 800) {
                    if (el.className && typeof el.className === 'string') {
                        res.push(el.className + ' | W:' + rect.width + ' | H:' + rect.height + ' | Tag: ' + el.tagName + ' | bg: ' + window.getComputedStyle(el).backgroundColor);
                    }
                }
            });
            return res;
        }
        """
        results = await page.evaluate(script)
        print("LARGE ELEMENTS:")
        for r in results:
            print(r)
            
        await browser.close()

asyncio.run(main())
