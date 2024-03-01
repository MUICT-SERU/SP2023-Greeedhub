TEST_ROUTING_DATA = [
    ("/test_template_controller", 'tests.test_controller.TemplateController', 'test_template_controller'),
    ("/test_json_controller/<id>", 'tests.test_controller.JsonController', 'test_json_controller'),
    ("/test_json_array_controller", 'tests.test_controller.JsonArrayController', 'test_json_array_controller'),
    ("/test_json_schema_invalid_controller",
        'tests.test_controller.JsonSchemaInvalidController', 'test_json_schema_invalid_controller'),
]
