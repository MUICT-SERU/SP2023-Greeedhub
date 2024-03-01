#!/usr/bin/python
import os
import sys
import unittest


def main(sdk_path):
    sys.path.append(sdk_path)
    sys.path.append('./lib/')
    sys.path.append('./datastoredict/')

    import dev_appserver
    dev_appserver.fix_sys_path()

    suite = unittest.loader.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main(os.environ['GAE_SDK_ROOT'])
