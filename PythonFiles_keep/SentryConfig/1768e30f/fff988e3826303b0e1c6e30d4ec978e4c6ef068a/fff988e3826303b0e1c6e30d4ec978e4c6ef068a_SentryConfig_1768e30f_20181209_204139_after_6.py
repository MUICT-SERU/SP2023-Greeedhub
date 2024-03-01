from sentry_config.config import *
from sentry_config.validators import *
from config_validators import MustNotBeFive


class TestConfig(SentryConfig):
    class TestSection(SentrySection):
        IntOption = SentryOption(
            default=5,
            criteria=IntRequired,
            description="Int option. must be an int."
        )
        StringOption = SentryOption(
            default="String Option",
            criteria=StringRequired,
            description="String option. must be a string."
        )
        BoolOption = SentryOption(
            default=True,
            criteria=BoolRequired,
            description="Bool option. must be a boolean."
        )
        ListOption = SentryOption(
            default=[1, 2, 3, 4, 5],
            criteria=ListRequired,
            description="List option. Must be a list."
        )
        DictOption = SentryOption(
            default={'one': 1, 'two': 2, 'three': 3},
            criteria=DictRequired,
            description="Dictionary option. Must be a dictionary."
        )
        NotFive = SentryOption(
            default=4,
            criteria=[IntRequired, MustNotBeFive],
            description="Int option. Must not be 5."
        )


class TestConfigErroneous(SentryConfig):
    class ErroneousOptions(SentrySection):
        ErroneousOptionOne = SentryOption(
            default=5,
            criteria=[IntRequired, MustNotBeFive],
            description="This option is an int, and since it must not be 5 and the default is 5. This should fail."
        )
        ErroneousOptionTwo = SentryOption(
            default=None,
            criteria=[IntRequired],
            description="This option has no default value, and requires an int. This should fail."
        )
