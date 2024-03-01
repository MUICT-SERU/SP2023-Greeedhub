# coding=utf-8
import os
import re

from jinja2 import Environment, FileSystemLoader

from pyecharts.commons.types import Any, Optional

from ..commons.utils import write_utf8_html_file
from ..consts import ONLINE_HOST
from ..datasets import FILENAMES

__HERE = os.path.abspath(os.path.dirname(__file__))

GLOBAL_ENV = Environment(
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(os.path.join(__HERE, "templates")),
)


class RenderEngine:
    def __init__(self, env: Optional[Environment] = None):
        self.env = env or GLOBAL_ENV

    @staticmethod
    def generate_js_link(chart: Any) -> Any:
        if not chart.js_host:
            chart.js_host = ONLINE_HOST
        links = []
        for dep in chart.js_dependencies.items:
            # TODO: if?
            links.append("{}{}.js".format(chart.js_host, FILENAMES[dep]))
        chart.dependencies = links
        return chart

    def render_chart_to_file(self, template_name: str, chart: Any, path: str):
        """
        Render a chart or page to local html files.

        :param chart: A Chart or Page object
        :param path: The destination file which the html code write to
        :param template_name: The name of template file.
        """
        tpl = self.env.get_template(template_name)
        html = tpl.render(chart=self.generate_js_link(chart))
        html = re.sub(r'\\n|\\t|"?__-o-__"?', "", html)
        write_utf8_html_file(path, html)

    def render_chart_to_notebook(self, template_name, **kwargs) -> str:
        """
        Return html string for rendering a chart/page to a notebook cell.

        :param template_name: file name of template.
        :param ctx: A dictionary containing data.
        """
        tpl = self.env.get_template(template_name)
        return tpl.render(**kwargs)
