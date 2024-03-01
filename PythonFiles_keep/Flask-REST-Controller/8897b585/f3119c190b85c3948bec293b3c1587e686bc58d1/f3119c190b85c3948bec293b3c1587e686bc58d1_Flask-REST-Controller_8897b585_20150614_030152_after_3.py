# coding: utf-8

ROUTING_VIEWS = [
    ("/", "app.IndexController", "foo"),
    ("/hoge/<id>", "hoge.HogeController", "hoge"),
    ("/fuga", "template.TemplateController", "fuga")
]
