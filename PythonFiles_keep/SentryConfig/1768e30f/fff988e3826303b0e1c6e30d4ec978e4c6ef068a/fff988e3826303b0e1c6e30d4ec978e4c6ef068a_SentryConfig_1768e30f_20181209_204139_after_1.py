""" Make a class which will represent the configuration ini file """

from sentry_config.config import *
from sentry_config.validators import *
from example_config.option_validators import *


class ExampleConfig(SentryConfig):
    class SectionOne(SentrySection):
        SO_OptionOne = SentryOption(
            default="I am used when an option does not contain a value in the ini, or it doesn't load properly.",
            criteria=None,
            description="I represent option one of section one of example.ini"
        )
        SO_OptionTwo = SentryOption(
            default=None,  # Without a default this will throw a NoDefaultGivenError if it fails to load from the ini
            criteria=None,
            description="I represent option two of section one of example.ini"
        )

    class SectionTwo(SentrySection):
        ST_OptionOne = SentryOption(
            default=1,
            criteria=[IntRequired, MustBeOne],  # IntRequired will attempt to convert the value to an int.
            description='I represent option one of section two of example.ini; I must be an int which equals 1.'
        )

        ST_OptionTwo = SentryOption(
            default="hello",
            criteria=[StringRequired, LenMustBeFive],
            description="I represent option two of section two of example.ini; I must be a string with a len of 5."
        )
