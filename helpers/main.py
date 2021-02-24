import sys

import helpers.argParser as ap
import helpers.patentDownloader as pd
import helpers.unpacker as up


def main():
    args = ap.parse_args(sys.argv[1:])

    if not ap.validate_args(args):
        return

    if args.startDownloader:
        pd.main(args)

    if args.startUnpacker:
        up.main(args)


if __name__ == '__main__':
    main()