"""Scraper for ETSLink (Everport Terminal Services) - Multiple Locations."""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from src.scraper import SessionScraper
from src.parser import HTMLParser
from src.storage import JSONStorage

# Try to import playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# Available ETSLink locations
ETSLINK_LOCATIONS = {
    "LAX": {
        "name": "Los Angeles",
        "base_url": "https://www.etslink.com",
        "code": "LAX",
    },
    "OAK": {
        "name": "Oakland",
        "base_url": "https://www.etslink.com",
        "code": "OAK",
    },
    "TIW": {
        "name": "Tacoma",
        "base_url": "https://www.etslink.com",
        "code": "TIW",
    },
}

# Path to save browser session cookies
COOKIE_FILE = "data/etslink_cookies.json"


class ETSLinkScraper:
    """Scraper for ETSLink terminal sites with multi-location support using Playwright."""

    def __init__(self, username: str, password: str):
        """Initialize the ETSLink scraper.

        Args:
            username: ETSLink User ID.
            password: ETSLink password.
        """
        self.username = username
        self.password = password
        self.base_url = "https://www.etslink.com"
        self.parser = HTMLParser()
        self.logged_in = False
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def login(self) -> tuple[bool, str]:
        """Login to ETSLink using Playwright browser automation.

        Returns:
            Tuple of (success, error_message).
        """
        if not PLAYWRIGHT_AVAILABLE:
            return False, "Playwright not installed. Run: pip install playwright && playwright install chromium"

        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser in headed mode so user can solve CAPTCHA if needed
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # Go to login page
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Wait for ExtJS to load
            await self.page.wait_for_timeout(2000)
            
            # Fill in credentials - ExtJS uses specific input IDs
            # Try multiple selectors for the login fields
            username_selectors = [
                'input[name="PI_LOGIN_ID"]',
                'input[id="PI_LOGIN_ID"]', 
                '#PI_LOGIN_ID-inputEl',
                'input[id*="LOGIN"]',
            ]
            
            password_selectors = [
                'input[name="PI_PASSWORD"]',
                'input[id="PI_PASSWORD"]',
                '#PI_PASSWORD-inputEl',
                'input[type="password"]',
            ]
            
            # Find and fill username
            for selector in username_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem and await elem.is_visible():
                        await elem.fill(self.username)
                        break
                except:
                    continue
            
            # Find and fill password
            for selector in password_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem and await elem.is_visible():
                        await elem.fill(self.password)
                        break
                except:
                    continue
            
            # Click login button - ExtJS buttons have specific structure
            login_button_selectors = [
                'a:has-text("Login")',
                'span:has-text("Login")',
                '.x-btn:has-text("Login")',
                '[id*="login"] >> text=Login',
                'text=Login',
            ]
            
            clicked = False
            for selector in login_button_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem and await elem.is_visible():
                        await elem.click()
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                # Try pressing Enter as fallback
                await self.page.keyboard.press("Enter")
            
            # Wait for response
            await self.page.wait_for_timeout(3000)
            
            # Check if CAPTCHA appeared
            verify_visible = False
            try:
                verify_input = await self.page.query_selector('input[name="PI_VERIFY_CODE"], input[id*="VERIFY"]')
                if verify_input:
                    verify_visible = await verify_input.is_visible()
            except:
                pass
            
            if verify_visible:
                # CAPTCHA is required - wait for user to solve it
                print("CAPTCHA detected - please solve it in the browser window...")
                # Wait up to 120 seconds for login to complete
                try:
                    await self.page.wait_for_url("**/main**", timeout=120000)
                except:
                    pass
            
            # Check if login was successful
            await self.page.wait_for_timeout(2000)
            url = self.page.url
            
            # Save cookies for future use
            cookies = await self.context.cookies()
            os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
            with open(COOKIE_FILE, "w") as f:
                json.dump(cookies, f)
            
            if "main" in url.lower() or "home" in url.lower():
                self.logged_in = True
                return True, ""
            
            # Check for error message on page
            error_elem = await self.page.query_selector('.error, .alert-danger, [class*="error"]')
            if error_elem:
                error_text = await error_elem.inner_text()
                return False, error_text.strip() or "Login failed"
            
            # If password field is still visible, login likely failed
            pwd_field = await self.page.query_selector('input[type="password"]')
            if pwd_field and await pwd_field.is_visible():
                return False, "Login failed - invalid credentials or CAPTCHA required"
            
            self.logged_in = True
            return True, ""
            
        except Exception as e:
            return False, f"Browser error: {str(e)}"

    async def scrape_location(self, location_code: str) -> Dict[str, Any]:
        """Scrape data for a specific location.

        Args:
            location_code: Location code (LAX, OAK, TIW, etc.)

        Returns:
            Dictionary containing scraped data for the location.
        """
        if not self.logged_in or not self.page:
            raise RuntimeError("Not logged in. Call login() first.")

        location = ETSLINK_LOCATIONS.get(location_code.upper())
        if not location:
            return {"error": f"Unknown location: {location_code}"}

        result = {
            "location": location["name"],
            "code": location_code.upper(),
            "data": {},
            "tables": [],
            "links": [],
            "grids": [],
        }

        try:
            # ETSLink loads content in iframes inside #func_frames
            # The main page is just a shell with tabs
            # We need to access the iframe content
            
            # Wait for the page to fully load
            await self.page.wait_for_timeout(3000)
            
            # First, try to navigate to a data-rich page using the menu
            # Look for "Customer Export Information Inquiry" or similar in the menu
            print("Looking for data pages in the menu...")
            
            # Click on the ETSLink menu logo to open the menu
            menu_logo = await self.page.query_selector('img[src*="ETS-Link"]')
            if menu_logo:
                await menu_logo.click()
                await self.page.wait_for_timeout(1000)
                
                # Look for menu items with data
                data_menu_items = [
                    'Customer Export Information',
                    'Container Inquiry',
                    'Import Inquiry',
                    'Export Inquiry',
                    'Vessel Schedule',
                ]
                
                for item_text in data_menu_items:
                    menu_item = await self.page.query_selector(f'span:has-text("{item_text}")')
                    if menu_item and await menu_item.is_visible():
                        print(f"  Found menu item: {item_text}")
                        await menu_item.click()
                        await self.page.wait_for_timeout(3000)
                        break
                else:
                    # Close menu if no item found
                    await self.page.keyboard.press("Escape")
            
            # Also try clicking on existing tabs that might have data
            # Look for tabs with data-related names
            tab_keywords = ['Export', 'Import', 'Container', 'Inquiry', 'Vessel']
            tabs = await self.page.query_selector_all('.x-tab')
            for tab in tabs:
                tab_text = await tab.inner_text()
                if any(kw.lower() in tab_text.lower() for kw in tab_keywords):
                    print(f"  Clicking on tab: {tab_text.strip()}")
                    await tab.click()
                    await self.page.wait_for_timeout(3000)
                    break
            
            # Now find the iframes
            iframes = await self.page.query_selector_all('iframe')
            print(f"Found {len(iframes)} iframes on page")
            
            # Get iframe IDs for debugging
            for i, iframe in enumerate(iframes):
                iframe_id = await iframe.get_attribute('id')
                print(f"  iframe[{i}]: id={iframe_id}")
            
            # Try to get content from each visible iframe
            for iframe in iframes:
                try:
                    iframe_id = await iframe.get_attribute('id') or 'unknown'
                    
                    # Check if iframe is visible
                    is_visible = await iframe.is_visible()
                    if not is_visible:
                        print(f"  Skipping hidden iframe: {iframe_id}")
                        continue
                    
                    print(f"  Processing visible iframe: {iframe_id}")
                    
                    # Get the frame object
                    frame = await iframe.content_frame()
                    if not frame:
                        print(f"  Could not get content frame for {iframe_id}")
                        continue
                    
                    # Wait for frame content to load
                    await frame.wait_for_load_state("domcontentloaded")
                    await self.page.wait_for_timeout(2000)
                    
                    # Try to fill in search criteria and submit
                    # Look for terminal/location input fields
                    print(f"    Looking for search fields in iframe...")
                    
                    # Fill in Terminal ID if there's a field for it
                    terminal_fields = await frame.query_selector_all('input[type="text"]')
                    for field in terminal_fields:
                        placeholder = await field.get_attribute('placeholder') or ''
                        field_id = await field.get_attribute('id') or ''
                        field_name = await field.get_attribute('name') or ''
                        
                        # Check if this might be a terminal/location field
                        if any(kw in (placeholder + field_id + field_name).lower() for kw in ['terminal', 'loc', 'port', 'yard']):
                            print(f"    Found terminal field: {field_id or field_name}")
                            await field.fill(location_code.upper())
                            await self.page.wait_for_timeout(500)
                            break
                    
                    # Look for and click Search/Query button
                    search_clicked = False
                    search_selectors = [
                        'span:has-text("Search")',
                        'span:has-text("Query")',
                        'span:has-text("Find")',
                        'span:has-text("Go")',
                        'a:has-text("Search")',
                        'a:has-text("Query")',
                        '.x-btn:has-text("Search")',
                        '.x-btn:has-text("Query")',
                    ]
                    
                    for selector in search_selectors:
                        try:
                            btn = await frame.query_selector(selector)
                            if btn and await btn.is_visible():
                                print(f"    Clicking search button...")
                                await btn.click()
                                search_clicked = True
                                await self.page.wait_for_timeout(5000)  # Wait for data to load
                                break
                        except:
                            continue
                    
                    if not search_clicked:
                        # Try pressing Enter in the last field we interacted with
                        await frame.keyboard.press("Enter")
                        await self.page.wait_for_timeout(3000)
                    
                    # Wait longer for ExtJS to initialize and load data
                    print(f"    Waiting for ExtJS data to load...")
                    await self.page.wait_for_timeout(3000)
                    
                    # Debug: Get frame URL and basic info
                    frame_url = frame.url
                    print(f"    Frame URL: {frame_url}")
                    
                    # Debug: Check what's in the frame
                    debug_info = await frame.evaluate('''() => {
                        const gridInfo = [];
                        if (typeof Ext !== 'undefined') {
                            Ext.ComponentQuery.query('grid').forEach((grid, idx) => {
                                const store = grid.getStore();
                                gridInfo.push({
                                    idx: idx,
                                    title: grid.title || '',
                                    storeCount: store ? store.getCount() : -1,
                                    isVisible: grid.isVisible(),
                                });
                            });
                        }
                        return {
                            hasExt: typeof Ext !== 'undefined',
                            gridCount: typeof Ext !== 'undefined' ? Ext.ComponentQuery.query('grid').length : 0,
                            panelCount: typeof Ext !== 'undefined' ? Ext.ComponentQuery.query('panel').length : 0,
                            allTables: document.querySelectorAll('table').length,
                            xGridViews: document.querySelectorAll('.x-grid-view').length,
                            gridInfo: gridInfo,
                        };
                    }''')
                    print(f"    Debug info: Ext={debug_info.get('hasExt')}, grids={debug_info.get('gridCount')}, panels={debug_info.get('panelCount')}, tables={debug_info.get('allTables')}")
                    print(f"    Grid details: {debug_info.get('gridInfo')}")
                    
                    # Extract data from ExtJS grids inside the iframe
                    grid_data = await frame.evaluate('''() => {
                const grids = [];
                
                // Try to find ExtJS grid stores
                if (typeof Ext !== 'undefined') {
                    // ExtJS 4/5/6 style
                    Ext.ComponentQuery.query('grid').forEach((grid, idx) => {
                        const store = grid.getStore();
                        if (store) {
                            const records = [];
                            const columns = grid.columns ? grid.columns.map(c => c.text || c.dataIndex || '') : [];
                            
                            store.each(record => {
                                records.push(record.data);
                            });
                            
                            // Include grid even if no records - shows structure
                            grids.push({
                                id: idx,
                                title: grid.title || '',
                                columns: columns,
                                recordCount: records.length,
                                records: records
                            });
                        }
                    });
                }
                
                // Also try to extract visible table-like data from DOM
                const tables = [];
                document.querySelectorAll('.x-grid-view, .x-grid-item-container').forEach((view, idx) => {
                    const rows = [];
                    view.querySelectorAll('.x-grid-row, .x-grid-item').forEach(row => {
                        const cells = [];
                        row.querySelectorAll('.x-grid-cell, .x-grid-cell-inner, td').forEach(cell => {
                            cells.push(cell.innerText.trim());
                        });
                        if (cells.length > 0 && cells.some(c => c)) {
                            rows.push(cells);
                        }
                    });
                    if (rows.length > 0) {
                        tables.push({ id: idx, rows: rows });
                    }
                });
                
                // Also get any regular HTML tables
                    document.querySelectorAll('table').forEach((table, idx) => {
                        const rows = [];
                        const headers = [];
                        table.querySelectorAll('tr').forEach(tr => {
                            const cells = [];
                            const isHeader = tr.querySelectorAll('th').length > 0;
                            tr.querySelectorAll('td, th').forEach(cell => {
                                cells.push(cell.innerText.trim());
                            });
                            if (cells.length > 0 && cells.some(c => c)) {
                                if (isHeader && headers.length === 0) {
                                    headers.push(...cells);
                                } else {
                                    rows.push(cells);
                                }
                            }
                        });
                        if (rows.length > 0) {
                            tables.push({ id: 'table_' + idx, headers: headers, rows: rows });
                        }
                    });
                    
                    return { grids, tables };
                }''')
                    
                    if grid_data:
                        frame_grids = grid_data.get("grids", [])
                        frame_tables = grid_data.get("tables", [])
                        
                        # Add iframe source info to results
                        for g in frame_grids:
                            g["source_iframe"] = iframe_id
                        for t in frame_tables:
                            t["source_iframe"] = iframe_id
                        
                        result["grids"].extend(frame_grids)
                        result["tables"].extend(frame_tables)
                        
                        print(f"    Found {len(frame_grids)} grids, {len(frame_tables)} tables in iframe {iframe_id}")
                    
                except Exception as frame_error:
                    print(f"  Error processing iframe: {frame_error}")
                    continue
            
            # Get current URL and page info
            result["data"]["url"] = self.page.url
            result["data"]["title"] = await self.page.title()
            result["data"]["total_grids"] = len(result["grids"])
            result["data"]["total_tables"] = len(result["tables"])
            
            # Take a screenshot for debugging
            screenshot_path = f"data/etslink_{location_code.lower()}_screenshot.png"
            await self.page.screenshot(path=screenshot_path)
            result["data"]["screenshot"] = screenshot_path
            
            print(f"Scrape complete: {len(result['grids'])} grids, {len(result['tables'])} tables found")
        except Exception as e:
            result["error"] = str(e)

        return result

    async def scrape_all_locations(self, location_codes: List[str]) -> Dict[str, Any]:
        """Scrape data for multiple locations.

        Args:
            location_codes: List of location codes to scrape.

        Returns:
            Dictionary with results for each location.
        """
        results = {}
        for code in location_codes:
            try:
                results[code] = await self.scrape_location(code)
            except Exception as e:
                results[code] = {"error": str(e)}
        return results

    async def close(self):
        """Close the browser and cleanup."""
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None


async def scrape_etslink(
    username: str,
    password: str,
    locations: List[str] = None,
) -> Dict[str, Any]:
    """Scrape ETSLink for specified locations.

    Args:
        username: ETSLink User ID.
        password: ETSLink password.
        locations: List of location codes. Defaults to all locations.

    Returns:
        Dictionary containing scraped data.
    """
    if locations is None:
        locations = list(ETSLINK_LOCATIONS.keys())

    scraper = ETSLinkScraper(username, password)
    logs = []
    result = {
        "success": False,
        "logs": logs,
        "locations": {},
    }

    try:
        logs.append({"type": "info", "message": "Connecting to ETSLink..."})

        login_success, login_error = await scraper.login()
        if not login_success:
            error_msg = login_error or "Login failed. Check credentials."
            logs.append({"type": "error", "message": error_msg})
            return result

        logs.append({"type": "success", "message": "Login successful!"})
        logs.append({"type": "info", "message": f"Scraping {len(locations)} locations..."})

        for i, loc in enumerate(locations):
            logs.append({"type": "info", "message": f"Scraping {loc} ({i+1}/{len(locations)})..."})
            loc_data = await scraper.scrape_location(loc)
            result["locations"][loc] = loc_data

            if "error" not in loc_data:
                table_count = len(loc_data.get("tables", []))
                logs.append({"type": "success", "message": f"  {loc}: Found {table_count} tables"})
            else:
                logs.append({"type": "error", "message": f"  {loc}: {loc_data['error']}"})

        # Save results
        storage = JSONStorage("data/etslink_data.json")
        storage.save(result["locations"])
        logs.append({"type": "success", "message": "Data saved to data/etslink_data.json"})

        result["success"] = True
        logs.append({"type": "success", "message": "Scraping complete!"})

    except Exception as e:
        logs.append({"type": "error", "message": f"Error: {str(e)}"})
    finally:
        await scraper.close()

    return result


# CLI interface
if __name__ == "__main__":
    import os
    import getpass

    print("\n🚢 ETSLink Scraper")
    print("=" * 40)
    print("Available locations:", ", ".join(ETSLINK_LOCATIONS.keys()))
    print()

    username = os.environ.get("ETSLINK_USERNAME") or input("Enter ETSLink User ID: ")
    password = os.environ.get("ETSLINK_PASSWORD") or getpass.getpass("Enter Password: ")

    locations_input = input("Enter locations (comma-separated, or 'all'): ").strip()
    if locations_input.lower() == "all" or not locations_input:
        locations = list(ETSLINK_LOCATIONS.keys())
    else:
        locations = [loc.strip().upper() for loc in locations_input.split(",")]

    print(f"\nScraping locations: {', '.join(locations)}")

    result = asyncio.run(scrape_etslink(username, password, locations))

    for log in result["logs"]:
        prefix = "✓" if log["type"] == "success" else "✗" if log["type"] == "error" else "→"
        print(f"{prefix} {log['message']}")
