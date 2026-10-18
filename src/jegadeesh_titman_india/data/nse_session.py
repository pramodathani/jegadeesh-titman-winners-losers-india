"""A polite HTTP session for NSE and NIFTY Indices downloads."""

import time

import requests


class NseSession:
    """Wraps requests with browser headers, a pause between calls and retries.

    Attributes:
        pause_seconds: Seconds to wait before every request.
        session: The underlying requests session.
    """

    BROWSER_AGENT: str = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'
    )

    def __init__(self, pause_seconds: float = 1.0) -> None:
        """Creates the session.

        Args:
            pause_seconds: Seconds to wait before every request.

        Returns:
            None.

        Raises:
            None.
        """
        self.pause_seconds = pause_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': self.BROWSER_AGENT,
                'Accept': '*/*',
                'Referer': 'https://www.nseindia.com/',
            }
        )

    def warm_up(self) -> None:
        """Loads the NSE home page so that cookies are set when offered.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        try:
            self.session.get('https://www.nseindia.com', timeout=30)
        except requests.RequestException:
            pass

    def get(self, url: str, params: dict | None = None) -> requests.Response:
        """Gets a URL after a pause, retrying on server errors.

        Args:
            url: The address to fetch.
            params: Optional query parameters.

        Returns:
            The last response received, which may be a 404.

        Raises:
            requests.RequestException: When every attempt fails to connect.
        """
        response = None
        for attempt in range(4):
            time.sleep(self.pause_seconds * (attempt + 1))
            try:
                response = self.session.get(url, params=params, timeout=90)
            except requests.RequestException:
                if attempt == 3:
                    raise
                continue
            if response.status_code < 500 and response.status_code != 429:
                return response
        return response

    def post_json(
        self, url: str, body: dict, extra_headers: dict
    ) -> requests.Response:
        """Posts a JSON body after a pause.

        Args:
            url: The address to post to.
            body: The JSON body.
            extra_headers: Headers to add for this request.

        Returns:
            The response.

        Raises:
            requests.RequestException: When the request fails.
        """
        time.sleep(self.pause_seconds)
        return self.session.post(
            url,
            json=body,
            headers=extra_headers,
            timeout=180,
        )
