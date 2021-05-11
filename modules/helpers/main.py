import os
import sys
import modules.helpers.argParser as ap
import modules.helpers.patentDownloader as pd
import modules.helpers.unpacker as up
import modules.parsers.patentParser as pp


def main():
    args = ap.parse_args(sys.argv[1:])

    if not ap.validate_args(args):
        return

    if args.startDownloader:
        pd.main(args)

    if args.startUnpacker:
        up.main(args)

    if args.parsePatent:
        pp.main()


if __name__ == '__main__':
    main()