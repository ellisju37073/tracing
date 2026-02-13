"""Common CSS selectors for web scraping."""


class Selectors:
    """Collection of common CSS selectors."""

    # Common content selectors
    MAIN_CONTENT = "main, article, .content, #content, .main"
    PARAGRAPHS = "p"
    IMAGES = "img[src]"
    
    # Navigation
    NAV_LINKS = "nav a, .nav a, .navigation a"
    MENU_ITEMS = ".menu li, .nav-menu li, ul.menu li"
    
    # Lists
    UNORDERED_LISTS = "ul"
    ORDERED_LISTS = "ol"
    LIST_ITEMS = "li"
    
    # Tables
    TABLES = "table"
    TABLE_ROWS = "tr"
    TABLE_HEADERS = "th"
    TABLE_CELLS = "td"
    
    # Forms
    FORM_INPUTS = "input, select, textarea"
    SUBMIT_BUTTONS = "button[type='submit'], input[type='submit']"
    
    # Social media
    SOCIAL_LINKS = "a[href*='twitter'], a[href*='facebook'], a[href*='linkedin'], a[href*='instagram']"
    
    # E-commerce common
    PRODUCT_TITLE = ".product-title, .product-name, h1.title"
    PRODUCT_PRICE = ".price, .product-price, .amount"
    PRODUCT_DESCRIPTION = ".description, .product-description"
    
    # Blog/Article common
    ARTICLE_TITLE = "article h1, .post-title, .article-title"
    ARTICLE_DATE = ".date, .post-date, time, .published"
    ARTICLE_AUTHOR = ".author, .byline, .post-author"
    ARTICLE_CONTENT = "article p, .post-content p, .article-body p"
