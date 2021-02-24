import sys

import argParser
import patentDownloader
import unpacker


def main():
    args = argParser.parse_args(sys.argv[1:])

    if not argParser.validate_args(args):
        return

    if args.startDownloader:
        patentDownloader.main(args)

    if args.startUnpacker:
        unpacker.main(args)


if __name__ == '__main__':
    main()