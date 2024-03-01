from example_config.config import ExampleConfig
from os import getcwd, path

ini_path = getcwd() + "/example.ini"

config_container = ExampleConfig(ini_path)
if not path.exists(ini_path):
    config_container.flush_config()

config_container.read_config()

# Print section one and two's first option values, loaded from the ini.
print(config_container.SectionOne.SO_OptionOne)  # prints 'Lorem Ipsum'
print(config_container.SectionTwo.ST_OptionOne)  # prints '1'
