import argparse
import pystems as ps


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
    )
    args = parser.parse_args()

    # read stems
    S, sr = ps.read_stems(args.input)

    # write back
    ps.write_stems(S, "out.mp4", sr)
