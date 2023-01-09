import trio
from bs4 import BeautifulSoup

async def scrape(url):
    # Launch a headless Chrome browser
    browser = await launch()
    
    # Create a new page
    page = await browser.newPage()
    
    # Set the viewport to a specific size
    await page.setViewport({'width': 1920, 'height': 1080})
    
    # Navigate to the URL
    await page.goto(url)
    
    # Wait for the page to fully load
    await page.waitForSelector('body')
    
    # Retrieve the HTML of the page
    html = await page.content()
    
    # Close the browser
    await browser.close()
    
    return html

def parse_html(html):
    # Use Beautiful Soup to parse the HTML and extract the data that you are interested in
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('div', class_='data-item')
    
    return data

    trio.run(main)

def get_data(url):
    if __name__ == '__main__':
        async def main():
            html = await scrape(url)
            data = parse_html(html)
            print(data)

        trio.run(main)