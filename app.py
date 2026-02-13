"""Flask REST API for T18 Tideworks and ETSLink Scrapers."""

import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.scraper import SessionScraper
from src.parser import HTMLParser
from src.storage import JSONStorage
from scrape_etslink import scrape_etslink, ETSLINK_LOCATIONS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


async def do_scrape(username: str, password: str):
    """Perform the actual scraping."""
    base_url = "https://t18.tideworks.com/fc-T18"
    scraper = SessionScraper(base_url=base_url)
    parser = HTMLParser()
    storage = JSONStorage("data/t18_data.json")
    
    logs = []
    result = {
        "success": False,
        "logs": logs,
        "data": {
            "title": None,
            "links": [],
            "tables": [],
            "headings": {},
        }
    }
    
    try:
        logs.append({"type": "info", "message": "Connecting to T18 Tideworks..."})
        form_info = await scraper.get_login_form_fields("default.do")
        logs.append({"type": "success", "message": "Found login form"})
        
        logs.append({"type": "info", "message": f"Logging in as {username}..."})
        extra_fields = form_info.get("hidden_fields", {})
        
        login_success = await scraper.login(
            login_path=form_info.get("action") or "j_security_check",
            username=username,
            password=password,
            username_field="j_username",
            password_field="j_password",
            extra_fields=extra_fields,
        )
        
        if not login_success:
            logs.append({"type": "error", "message": "Login failed. Check your credentials."})
            return result
        
        logs.append({"type": "success", "message": "Login successful!"})
        logs.append({"type": "info", "message": "Fetching dashboard..."})
        
        dashboard_html = await scraper.get("default.do")
        if not dashboard_html:
            logs.append({"type": "error", "message": "Failed to fetch dashboard."})
            return result
        
        logs.append({"type": "info", "message": "Parsing page content..."})
        data = parser.parse(dashboard_html)
        soup = parser.get_soup(dashboard_html)
        
        # Extract links
        nav_links = []
        for link in soup.select("a[href]"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if text and href and not href.startswith(("javascript:", "#", "mailto:")):
                if not href.startswith("http"):
                    href = f"{base_url}/{href.lstrip('/')}"
                nav_links.append({"text": text, "href": href})
        
        # Extract tables
        tables = soup.find_all("table")
        table_data = []
        for idx, table in enumerate(tables):
            rows = []
            headers = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells and any(c for c in cells):
                    if not headers and tr.find("th"):
                        headers = cells
                    else:
                        rows.append(cells)
            if rows or headers:
                table_data.append({
                    "id": idx,
                    "headers": headers,
                    "rows": rows,
                    "rowCount": len(rows),
                })
        
        # Save data
        save_data = {
            "title": data.get("title"),
            "navigation_links": nav_links,
            "tables": table_data,
            "headings": data.get("headings", {}),
        }
        storage.save(save_data)
        
        logs.append({"type": "success", "message": "Data saved to data/t18_data.json"})
        logs.append({"type": "info", "message": f"Found {len(nav_links)} links and {len(table_data)} tables"})
        logs.append({"type": "success", "message": "Scraping complete!"})
        
        result["success"] = True
        result["data"] = {
            "title": data.get("title"),
            "links": nav_links,
            "tables": table_data,
            "headings": data.get("headings", {}),
            "meta_description": data.get("meta_description"),
        }
        
    except Exception as e:
        logs.append({"type": "error", "message": f"Error: {str(e)}"})
    finally:
        await scraper.close()
    
    return result


# ============== API Routes ==============

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "t18-scraper"})


@app.route("/api/scrape", methods=["POST"])
def scrape():
    """
    Scrape T18 Tideworks site.
    
    Request body:
    {
        "username": "your_username",
        "password": "your_password"
    }
    
    Response:
    {
        "success": true/false,
        "logs": [...],
        "data": {
            "title": "...",
            "links": [...],
            "tables": [...],
            "headings": {...}
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body required",
            "logs": [],
            "data": {}
        }), 400
    
    username = data.get("username", "")
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password required",
            "logs": [],
            "data": {}
        }), 400
    
    result = asyncio.run(do_scrape(username, password))
    return jsonify(result)


@app.route("/api/data", methods=["GET"])
def get_saved_data():
    """
    Get previously scraped data from storage.
    
    Response:
    {
        "success": true/false,
        "data": {...} or null
    }
    """
    storage = JSONStorage("data/t18_data.json")
    data = storage.load()
    
    if data:
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "data": None, "message": "No data found"})


# ============== ETSLink API Routes ==============

@app.route("/api/etslink/locations", methods=["GET"])
def get_etslink_locations():
    """
    Get available ETSLink locations.
    
    Response:
    {
        "locations": [{"code": "LAX", "name": "Los Angeles"}, ...]
    }
    """
    locations = [
        {"code": code, "name": info["name"]}
        for code, info in ETSLINK_LOCATIONS.items()
    ]
    return jsonify({"locations": locations})


@app.route("/api/etslink/scrape", methods=["POST"])
def scrape_etslink_route():
    """
    Scrape ETSLink for specified locations.
    
    Request body:
    {
        "username": "your_user_id",
        "password": "your_password",
        "locations": ["LAX", "OAK", "TIW"]  // optional, defaults to all
    }
    
    Response:
    {
        "success": true/false,
        "logs": [...],
        "locations": {...}
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body required",
            "logs": [],
            "locations": {}
        }), 400
    
    username = data.get("username", "")
    password = data.get("password", "")
    locations = data.get("locations", list(ETSLINK_LOCATIONS.keys()))
    
    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password required",
            "logs": [],
            "locations": {}
        }), 400
    
    result = asyncio.run(scrape_etslink(username, password, locations))
    return jsonify(result)


@app.route("/api/etslink/data", methods=["GET"])
def get_etslink_data():
    """
    Get previously scraped ETSLink data.
    
    Response:
    {
        "success": true/false,
        "data": {...} or null
    }
    """
    storage = JSONStorage("data/etslink_data.json")
    data = storage.load()
    
    if data:
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "data": None, "message": "No data found"})


if __name__ == "__main__":
    print("\n🚢 Terminal Scraper API")
    print("=" * 50)
    print("API running at http://127.0.0.1:5000")
    print("")
    print("T18 Tideworks Endpoints:")
    print("  GET  /api/health       - Health check")
    print("  POST /api/scrape       - Scrape T18")
    print("  GET  /api/data         - Get T18 data")
    print("")
    print("ETSLink Endpoints:")
    print("  GET  /api/etslink/locations - Get locations")
    print("  POST /api/etslink/scrape    - Scrape ETSLink")
    print("  GET  /api/etslink/data      - Get ETSLink data")
    print("=" * 50 + "\n")
    app.run(debug=False, host="127.0.0.1", port=5000)
