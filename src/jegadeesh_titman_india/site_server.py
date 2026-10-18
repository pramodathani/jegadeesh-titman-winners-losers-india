"""Serves the companion page on this computer and opens it in a browser.

The page is a static site shipped inside the package, with the study's results as data files. Browsers refuse to load a page's data files straight from disk, which is why a small local web server is used.

Typical usage example, after installing the package:

  jt-momentum-app
  jt-momentum-app --port 8123 --no-browser
"""

import argparse
import functools
import http.server
import pathlib
import socket
import webbrowser


class QuietRequestHandler(http.server.SimpleHTTPRequestHandler):
    """A static file handler that does not print a line for every request."""

    def log_message(self, format: str, *args: object) -> None:
        """Discards the per-request log line.

        Args:
            format: The format of the message.
            *args: The values for the format.

        Returns:
            None.

        Raises:
            None.
        """
        del format, args


class SiteServerApplication:
    """The command-line program that serves the companion page.

    Attributes:
        SITE_DIRECTORY: The folder holding index.html.
        DEFAULT_PORT: The port tried first.
    """

    SITE_DIRECTORY: pathlib.Path = (
        pathlib.Path(__file__).resolve().parent / 'site'
    )
    DEFAULT_PORT: int = 8000

    @staticmethod
    def launch() -> None:
        """Runs the application; this is the target of the console script.

        Args:
            None.

        Returns:
            None.

        Raises:
            OSError: When no port can be opened.
        """
        SiteServerApplication().run()

    def run(self) -> None:
        """Reads the command line, starts the server and waits.

        Args:
            None.

        Returns:
            None.

        Raises:
            OSError: When no port can be opened.
            FileNotFoundError: When the page is missing from the package.
        """
        parser = argparse.ArgumentParser(
            description='Serve the momentum study page on this computer.'
        )
        parser.add_argument('--port', type=int, default=self.DEFAULT_PORT)
        parser.add_argument('--no-browser', action='store_true')
        arguments = parser.parse_args()
        if not (self.SITE_DIRECTORY / 'index.html').exists():
            raise FileNotFoundError(
                f'The page is missing from the package: {self.SITE_DIRECTORY}'
            )
        port = self.free_port(arguments.port)
        handler = functools.partial(
            QuietRequestHandler,
            directory=str(self.SITE_DIRECTORY),
        )
        server = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
        address = f'http://127.0.0.1:{port}/'
        print(f'Serving the study at {address} (press Ctrl+C to stop)')
        if not arguments.no_browser:
            webbrowser.open(address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Stopped.')
        finally:
            server.server_close()

    def free_port(self, preferred: int) -> int:
        """Finds a free port, trying the preferred one and the next nineteen.

        Args:
            preferred: The port to try first.

        Returns:
            The first free port.

        Raises:
            OSError: When none of the twenty ports is free.
        """
        for port in range(preferred, preferred + 20):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                if probe.connect_ex(('127.0.0.1', port)) != 0:
                    return port
        raise OSError(f'No free port from {preferred} to {preferred + 19}')
