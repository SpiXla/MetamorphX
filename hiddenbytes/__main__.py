#!/usr/bin/env python3
"""
HiddenBytes — Binary Evasion & Polymorphic Toolkit

Usage:
    python -m hiddenbytes evasion   --encrypt <file> --output <file> [options]
    python -m hiddenbytes polymorph --generate <file> --payload <file> [options]
    python -m hiddenbytes --help
"""

import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    rest = sys.argv[2:]

    if command in ('--help', '-h'):
        print(__doc__)
        return

    if command == 'evasion':
        from hiddenbytes.evasion.cli import main as evasion_main
        evasion_main(rest)
    elif command == 'polymorph':
        from hiddenbytes.polymorph.cli import main as polymorph_main
        polymorph_main(rest)
    else:
        print("[ERROR] Unknown command: " + command)
        print("Available commands: evasion, polymorph")
        print("Run 'python -m hiddenbytes --help' for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
