"""Session-based scraper with login support."""

import httpx
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup


class SessionScraper:
    """Scraper that maintains a session for authenticated requests."""

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """Initialize the session scraper.

        Args:
            base_url: Base URL for the site.
            headers: Custom headers to send with requests.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self.logged_in = False

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client with cookie persistence."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                cookies=httpx.Cookies(),
            )
        return self._client

    async def get(self, path: str = "") -> Optional[str]:
        """Make a GET request.

        Args:
            path: URL path (will be joined with base_url).

        Returns:
            Response HTML content.
        """
        client = await self._get_client()
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None

    async def post(
        self, path: str, data: Dict[str, Any], follow_redirects: bool = True
    ) -> Optional[str]:
        """Make a POST request.

        Args:
            path: URL path.
            data: Form data to post.
            follow_redirects: Whether to follow redirects.

        Returns:
            Response HTML content.
        """
        client = await self._get_client()
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = await client.post(url, data=data, follow_redirects=follow_redirects)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None

    async def json_post(
        self, path: str, json_data: Dict[str, Any], follow_redirects: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Make a POST request with JSON data.

        Args:
            path: URL path.
            json_data: JSON data to post.
            follow_redirects: Whether to follow redirects.

        Returns:
            Response JSON data.
        """
        client = await self._get_client()
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = await client.post(url, json=json_data, follow_redirects=follow_redirects)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"JSON parse error: {e}")
            return None

    async def form_post_json(
        self, path: str, data: Dict[str, Any], follow_redirects: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Make a POST request with form data, expecting JSON response.

        Args:
            path: URL path.
            data: Form data to post.
            follow_redirects: Whether to follow redirects.

        Returns:
            Response JSON data.
        """
        client = await self._get_client()
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = await client.post(url, data=data, follow_redirects=follow_redirects)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"JSON parse error: {e}")
            return None

    async def login(
        self,
        login_path: str,
        username: str,
        password: str,
        username_field: str = "username",
        password_field: str = "password",
        extra_fields: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Login to the site.

        Args:
            login_path: Path to the login endpoint.
            username: Username/email.
            password: Password.
            username_field: Name of the username form field.
            password_field: Name of the password form field.
            extra_fields: Additional form fields (CSRF tokens, etc.).

        Returns:
            True if login successful, False otherwise.
        """
        form_data = {
            username_field: username,
            password_field: password,
        }
        if extra_fields:
            form_data.update(extra_fields)

        result = await self.post(login_path, form_data)
        
        if result:
            # Check if we're still on login page (login failed) or redirected
            soup = BeautifulSoup(result, "lxml")
            # Look for common login failure indicators
            login_form = soup.find("form", {"id": "loginForm"}) or soup.find("input", {"type": "password"})
            error_msg = soup.find(class_=lambda x: x and "error" in x.lower()) if soup else None
            
            if login_form is None and error_msg is None:
                self.logged_in = True
                return True
            elif error_msg:
                print(f"Login error: {error_msg.get_text(strip=True)}")
        
        return False

    async def login_with_details(
        self,
        login_path: str,
        username: str,
        password: str,
        username_field: str = "username",
        password_field: str = "password",
        extra_fields: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Login to the site and return detailed result.

        Args:
            login_path: Path to the login endpoint.
            username: Username/email.
            password: Password.
            username_field: Name of the username form field.
            password_field: Name of the password form field.
            extra_fields: Additional form fields (CSRF tokens, etc.).

        Returns:
            Dictionary with success status and error details.
        """
        form_data = {
            username_field: username,
            password_field: password,
        }
        if extra_fields:
            form_data.update(extra_fields)

        result = await self.post(login_path, form_data)
        
        if result:
            soup = BeautifulSoup(result, "lxml")
            
            # Look for error messages - check multiple patterns
            error_msg = None
            error_selectors = [
                soup.find(class_=lambda x: x and "error" in x.lower()),
                soup.find(id=lambda x: x and "error" in x.lower()),
                soup.find("div", class_="alert"),
                soup.find("span", class_="error"),
                soup.find("p", class_="error"),
            ]
            
            for elem in error_selectors:
                if elem:
                    error_msg = elem.get_text(strip=True)
                    break
            
            # Check if login form is still present
            login_form = soup.find("form", {"id": "loginForm"}) or soup.find("input", {"type": "password"})
            
            if login_form is None and error_msg is None:
                self.logged_in = True
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": error_msg or "Login failed - invalid credentials or session error"
                }
        
        return {"success": False, "error": "No response from server"}

    async def get_login_form_fields(self, login_page_path: str = "") -> Dict[str, Any]:
        """Get the login form fields from the login page.

        Args:
            login_page_path: Path to the login page.

        Returns:
            Dictionary with form details including hidden fields.
        """
        html = await self.get(login_page_path)
        if not html:
            return {}

        soup = BeautifulSoup(html, "lxml")
        
        # Find the login form
        form = soup.find("form")
        if not form:
            return {}

        fields = {
            "action": form.get("action", ""),
            "method": form.get("method", "POST"),
            "fields": {},
            "hidden_fields": {},
        }

        # Get all input fields
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            
            input_type = inp.get("type", "text")
            value = inp.get("value", "")

            if input_type == "hidden":
                fields["hidden_fields"][name] = value
            else:
                fields["fields"][name] = {
                    "type": input_type,
                    "value": value,
                }

        return fields

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
