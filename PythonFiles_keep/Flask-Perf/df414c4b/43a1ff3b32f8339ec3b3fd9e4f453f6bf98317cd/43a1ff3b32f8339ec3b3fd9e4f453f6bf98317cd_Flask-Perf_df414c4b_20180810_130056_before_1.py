import unittest
from unittest.mock import patch, MagicMock

from coverage import coverage

cov = coverage(branch=True)
cov.start()

from flask import Flask
from flask_perf import Profiler


class TestFlaskProfiler(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        cov.stop()
        cov.report(include='flask_perf/*', show_missing=True)

    def test_attach_app(self):
        app = Flask(__name__)
        profiler = Profiler(app)

        self.assertEqual(profiler.app, app)


    def test_config_defaults(self):
        app = Flask(__name__)
        profiler = Profiler()
        profiler.init_app(app)

        self.assertEqual(app.config["PROFILER_ENABLED"], False)
        self.assertEqual(app.config["PROFILER_RESTRICTIONS"], [])
        self.assertEqual(app.config["PROFILER_SQLALCHEMY_ENABLED"], False)
        self.assertEqual(app.config["PROFILER_SQLALCHEMY_THRESHOLD"], 0)
        self.assertEqual(app.config["PROFILER_SQLALCHEMY_FORMAT"], "statement: {query}\nparameters: {parameters}\nduration: {duration}s\ncontext: {context}\n")

    def test_attach_middleware(self):
        app = Flask(__name__)
        app.config["PROFILER_ENABLED"] = True
        profiler = Profiler()

        with patch("flask_perf.ProfilerMiddleware") as MockProfilerMiddleware:
            wsgi_app = app.wsgi_app
            profiler.init_app(app)
            MockProfilerMiddleware.assert_called_once_with(wsgi_app, restrictions=app.config["PROFILER_RESTRICTIONS"])

    def test_attach_sqlalchemy(self):
        app = Flask(__name__)
        app.config["PROFILER_SQLALCHEMY_ENABLED"] = True
        app.config["SQLALCHEMY_RECORD_QUERIES"] = True
        profiler = Profiler()
        profiler.init_app(app)

        print(app.after_request_funcs)
        self.assertTrue(profiler.__class__.log_queries in app.after_request_funcs[None])

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
                "PROFILER_SQLALCHEMY_FORMAT" : "",
                "PROFILER_SQLALCHEMY_THRESHOLD" : 0.5,
            }
            mockQuery = MagicMock()
            mockQuery.duration = 2
            mock_get_debug_queries.return_value = [mockQuery]
            Profiler.log_queries(None)
            mock_get_debug_queries.assert_called_once()


if __name__ == "__main__":
    unittest.main()
