from . import logger


def test_print_green_color(capsys):
    # arrange
    msg = 'Hi'
    expect_colored_msg = '\x1b[32m %s \x1b[0m\n' % msg

    # action
    logger.green(msg)

    # assert
    out, err = capsys.readouterr()
    assert out == expect_colored_msg

