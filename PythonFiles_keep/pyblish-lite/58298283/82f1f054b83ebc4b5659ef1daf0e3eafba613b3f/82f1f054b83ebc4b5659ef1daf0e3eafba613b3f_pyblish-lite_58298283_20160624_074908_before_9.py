import sys
import nose

if __name__ == '__main__':
    argv = sys.argv[:]
    argv.extend(['-c', '.noserc'])
    nose.main(argv=argv)
