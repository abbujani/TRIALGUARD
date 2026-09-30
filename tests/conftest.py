"""
tests/conftest.py — pytest bootstrap.

Keeps the developer's real ``.env`` out of the test run.

``app.py``, ``db.py`` and ``memory.py`` each call ``load_dotenv()`` at import
time, and the tests use ``importlib.reload()`` to re-import those modules with
a patched environment. Without this guard, the reload re-reads ``.env`` and
re-populates ``os.environ``, which silently defeats tests that assert a
missing-variable error is raised (e.g. ``test_missing_base_url_raises``).

This patch only applies while pytest is running — the app is unaffected.
"""

import dotenv

# Applied at conftest import time, i.e. before any test module is collected,
# so even module-level load_dotenv() calls in app code are neutralised.
dotenv.load_dotenv = lambda *args, **kwargs: False
