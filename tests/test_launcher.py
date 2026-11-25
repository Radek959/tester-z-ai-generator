import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from web import launcher


class LauncherTests(unittest.TestCase):
    def test_binds_local_server_before_starting_browser_and_closes_on_ctrl_c(self):
        server = Mock()
        server.serve_forever.side_effect = KeyboardInterrupt
        events = []
        with (
            patch.object(launcher, "make_server", side_effect=lambda *a, **kw: (
                events.append("bind") or server
            )) as make_server,
            patch.object(launcher, "Thread") as thread,
            redirect_stdout(io.StringIO()) as output,
        ):
            thread.return_value.start.side_effect = lambda: events.append("browser")
            self.assertEqual(launcher.main(), 0)
        self.assertEqual(events, ["bind", "browser"])
        make_server.assert_called_once_with("127.0.0.1", 5000, launcher.app, threaded=True)
        thread.assert_called_once_with(target=launcher._otworz_przegladarke, daemon=True)
        server.serve_forever.assert_called_once_with()
        server.server_close.assert_called_once_with()
        self.assertIn("Ctrl+C", output.getvalue())
        self.assertIn("zatrzymany", output.getvalue())

    def test_bind_failure_does_not_open_browser(self):
        for error in (OSError("zajęty port"), SystemExit(1)):
            with (
                self.subTest(error=error),
                patch.object(launcher, "make_server", side_effect=error),
                patch.object(launcher, "Thread") as thread,
                redirect_stdout(io.StringIO()) as output,
            ):
                self.assertEqual(launcher.main(), 1)
                thread.assert_not_called()
                self.assertIn("Port 5000 może być zajęty", output.getvalue())
                self.assertNotIn("Traceback", output.getvalue())

    def test_serving_failure_closes_server_and_returns_error(self):
        server = Mock()
        server.serve_forever.side_effect = OSError("awaria")
        with (
            patch.object(launcher, "make_server", return_value=server),
            patch.object(launcher, "Thread"),
            redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(launcher.main(), 1)
        server.server_close.assert_called_once_with()
        self.assertIn("Uruchom start_web.bat ponownie", output.getvalue())

    def test_opens_default_browser(self):
        with patch.object(launcher.webbrowser, "open", return_value=True) as browser:
            launcher._otworz_przegladarke()
        browser.assert_called_once_with(launcher.URL)

    def test_browser_failure_shows_manual_address(self):
        for error in (None, OSError("brak przeglądarki"), launcher.webbrowser.Error()):
            with (
                self.subTest(error=error),
                patch.object(launcher.webbrowser, "open", return_value=False, side_effect=error),
                redirect_stdout(io.StringIO()) as output,
            ):
                launcher._otworz_przegladarke()
                self.assertIn(f"Otwórz samodzielnie: {launcher.URL}", output.getvalue())
