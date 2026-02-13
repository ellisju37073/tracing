"""Scraper for T18 Tideworks terminal site."""

import asyncio
import os
from src.scraper import SessionScraper
from src.parser import HTMLParser
from src.storage import JSONStorage


async def scrape_t18(username: str, password: str):
    """Scrape T18 Tideworks terminal site.

    Args:
        username: Your T18 account username.
        password: Your T18 account password.
    """
    base_url = "https://t18.tideworks.com/fc-T18"
    
    scraper = SessionScraper(base_url=base_url)
    parser = HTMLParser()
    storage = JSONStorage("data/t18_data.json")

    try:
        # First, get the login page to see the form structure
        print("Fetching login page...")
        form_info = await scraper.get_login_form_fields("default.do")
        print(f"Form action: {form_info.get('action', 'N/A')}")
        print(f"Form fields: {list(form_info.get('fields', {}).keys())}")
        print(f"Hidden fields: {list(form_info.get('hidden_fields', {}).keys())}")

        # Attempt login
        print(f"\nLogging in as {username}...")
        
        # Build login data with hidden fields
        extra_fields = form_info.get("hidden_fields", {})
        
        login_success = await scraper.login(
            login_path=form_info.get("action", "default.do"),
            username=username,
            password=password,
            username_field="j_username",  # Common Tideworks field name
            password_field="j_password",  # Common Tideworks field name
            extra_fields=extra_fields,
        )

        if login_success:
            print("✓ Login successful!")
            
            # Now scrape the dashboard/main page
            print("\nFetching dashboard...")
            dashboard_html = await scraper.get("default.do")
            
            if dashboard_html:
                # Parse the dashboard
                data = parser.parse(dashboard_html)
                print(f"Page title: {data.get('title', 'N/A')}")
                
                # Look for navigation/menu items
                soup = parser.get_soup(dashboard_html)
                
                # Find main navigation links
                nav_links = []
                for link in soup.select("a[href]"):
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    if text and href and not href.startswith(("javascript:", "#", "mailto:")):
                        nav_links.append({"text": text, "href": href})
                
                # Find tables with data
                tables = soup.find_all("table")
                print(f"Found {len(tables)} tables on page")
                
                # Extract table data
                table_data = []
                for i, table in enumerate(tables):
                    rows = []
                    for tr in table.find_all("tr"):
                        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                        if cells:
                            rows.append(cells)
                    if rows:
                        table_data.append({"table_index": i, "rows": rows})
                
                # Save scraped data
                result = {
                    "title": data.get("title"),
                    "navigation_links": nav_links[:20],  # First 20 links
                    "tables": table_data,
                    "headings": data.get("headings", {}),
                }
                
                storage.save(result)
                print(f"\n✓ Data saved to {storage.filepath}")
                print(f"  - {len(nav_links)} navigation links found")
                print(f"  - {len(table_data)} tables with data")
                
        else:
            print("✗ Login failed. Please check your credentials.")

    finally:
        await scraper.close()


if __name__ == "__main__":
    # Get credentials from environment variables or prompt
    username = os.environ.get("T18_USERNAME")
    password = os.environ.get("T18_PASSWORD")
    
    if not username:
        username = input("Enter T18 username: ")
    if not password:
        import getpass
        password = getpass.getpass("Enter T18 password: ")
    
    asyncio.run(scrape_t18(username, password))
