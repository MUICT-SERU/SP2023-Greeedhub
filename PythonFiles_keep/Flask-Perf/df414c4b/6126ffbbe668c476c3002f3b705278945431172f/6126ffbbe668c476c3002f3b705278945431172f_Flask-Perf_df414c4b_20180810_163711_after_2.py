import unittest
from mock import patch, MagicMock

from flask import Flask

from flask_perf import Profiler, \
                       PROFILER_DEFAULT_ENABLED, \
                       PROFILER_DEFAULT_RESTRICTIONS, \
                       PROFILER_DEFAULT_SQLALCHEMY_ENABLED, \
                       PROFILER_DEFAULT_SQLALCHEMY_THRESHOLD, \
                       PROFILER_DEFAULT_SQLALCHEMY_FORMAT


class TestFlaskProfiler(unittest.TestCase):
    def test_attach_app(self):
        app = Flask(__name__)
        profiler = Profiler(app)

        self.assertEqual(profiler.app, app)

    def test_config_defaults(self):
        app = Flask(__name__)
        profiler = Profiler()
        profiler.init_app(app)

        self.assertEqual(app.config["PROFILER_ENABLED"], PROFILER_DEFAULT_ENABLED)
        self.assertEqual(app.config["PROFILER_RESTRICTIONS"], PROFILER_DEFAULT_RESTRICTIONS)
        self.assertEqual(app.config["PROFILER_SQLALCHEMY_ENABLED"], PROFILER_DEFAULT_SQLALCHEMY_ENABLED)
        self.assertEqual(app.config["PROFILER_SQLALCHEMY_THRESHOLD"], PROFILER_DEFAULT_SQLALCHEMY_THRESHOLD)
        self.assertEqual(app.config["PROFILER_SQLALCHEMY_FORMAT"], PROFILER_DEFAULT_SQLALCHEMY_FORMAT)

    def test_attach_middleware(self):
        app = Flask(__name__)
        app.config["PROFILER_ENABLED"] = True
        profiler = Profiler()

        with patch("flask_perf.ProfilerMiddleware") as MockProfilerMiddleware:
            wsgi_app = app.wsgi_app
            profiler.init_app(app)
            MockProfilerMiddleware.assert_called_once_with(
                wsgi_app, restrictions=app.config["PROFILER_RESTRICTIONS"])

    def test_attach_sqlalchemy(self):
        app = Flask(__name__)
        app.config["PROFILER_SQLALCHEMY_ENABLED"] = True
        app.config["SQLALCHEMY_RECORD_QUERIES"] = True
        profiler = Profiler()
        profiler.init_app(app)

        print(app.after_request_funcs)
        self.assertTrue(
            profiler.__class__.log_queries in app.after_request_funcs[None])

    def test_check_for_sqlalchemy(self):
        app = Flask(__name__)
        app.config["PROFILER_SQLALCHEMY_ENABLED"] = True
        app.config["SQLALCHEMY_RECORD_QUERIES"] = True
        profiler = Profiler()

        with patch("flask_perf.flask_sqlalchemy_available", False), self.assertRaises(ImportError):
            profiler.init_app(app)

    def test_check_for_sqlalchemy_record_queries(self):
        app = Flask(__name__)
        app.config["PROFILER_SQLALCHEMY_ENABLED"] = True
        app.config["SQLALCHEMY_RECORD_QUERIES"] = False
        profiler = Profiler()

        with self.assertRaises(ValueError):
            profiler.init_app(app)

    def test_log_queries(self):
        with patch("flask_perf.get_debug_queries") as mock_get_debug_queries, patch("flask_perf.current_app") as mock_current_app:
            mock_current_app.config = {
                "PROFILER_SQLALCHEMY_FORMAT": "{statement}{duration}{parameters}{start_time}{end_time}{context}",
                "PROFILER_SQLALCHEMY_THRESHOLD": PROFILER_DEFAULT_SQLALCHEMY_THRESHOLD,
                "PROFILER_SQLALCHEMY_FORMAT": PROFILER_DEFAULT_SQLALCHEMY_FORMAT
            }
            mockQuery = MagicMock()
            mockQuery.duration = 2
            mock_get_debug_queries.return_value = [mockQuery]
            Profiler.log_queries(None)
            mock_get_debug_queries.assert_called_once()


if __name__ == "__main__":
    unittest.main()
