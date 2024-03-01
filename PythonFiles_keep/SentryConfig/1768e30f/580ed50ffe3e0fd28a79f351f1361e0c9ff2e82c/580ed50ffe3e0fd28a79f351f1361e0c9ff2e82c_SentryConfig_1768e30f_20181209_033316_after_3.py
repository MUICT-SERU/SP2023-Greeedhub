from example_config.config import ExampleConfig
from os import getcwd, path

ini_path = getcwd() + "/example.ini"  # Path to the ini to represent.

config_container = ExampleConfig(ini_path)  # Create the example config instance using the path to the ini to represent.

if not path.exists(ini_path):  # If the ini does not exist,
    config_container.flush_config()  # Create a new one with defaults

config_container.read_config()  # Read the values from the config. config_container will now have the attributes set.

# Print section one and two's first option values, loaded from the ini.
print(config_container.SectionOne.SO_OptionOne)  # prints 'Lorem Ipsum'
print(config_container.SectionTwo.ST_OptionOne)  # prints '1'
