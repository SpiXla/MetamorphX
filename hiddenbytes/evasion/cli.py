"""
Command-line interface for the Evasion Program (Windows).

Usage:
    evasion --encrypt <target> --output <file> [options]
    evasion --encrypt <target> --output <exe> --standalone
"""

import argparse
import os
import sys
import tempfile

from hiddenbytes.evasion.core import encrypt_binary

BANNER = r"""
 __   __  _                   _   ____                               
|  | |  |(_)                 | | |  _ \                              
|  |_|  | _  ___  _ __   ___ | |_| |_) |  ___  ___  ___  _ __   __ _ 
|  _   _|| |/ _ \| '_ \ / _ \| __|  _ <  / _ \/ _ \/ _ \| '_ \ / _` |
| | | |  | | (_) | | | | (_) | |_| |_) ||  __/  __/  __/| |_) | (_| |
|_| |_|  |_|\___/|_| |_|\___/ \__|____/  \___|\___|\___|| .__/ \__, |
                                                          | |     __/ |
                                                          |_|    |___/
                E V A S I O N   P R O G R A M
"""


def parse_args(argv=None):
    """Parse command-line arguments for the Evasion Program."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='evasion',
        description='HiddenBytes Evasion Program - Encrypt and modify '
                    'binaries with stealth techniques.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  evasion --encrypt target.py --output stealth.py --add-size 101 --delay 101
  evasion --encrypt target.py --output stealth.exe --delay 10 --standalone
  evasion --encrypt payload.exe --output stealth.exe --standalone
        """
    )

    parser.add_argument(
        '--encrypt',
        metavar='<target-binary>',
        required=True,
        help='Path to the target binary file to encrypt.'
    )
    parser.add_argument(
        '--output',
        metavar='<output-file>',
        required=True,
        help='Path where the encrypted/obfuscated binary will be saved.'
    )
    parser.add_argument(
        '--add-size',
        metavar='<size-in-mb>',
        type=int,
        default=0,
        help='Increase the output file size (in MB). Example: 101'
    )
    parser.add_argument(
        '--delay',
        metavar='<seconds>',
        type=int,
        default=101,
        help='Execution delay in seconds before the binary runs (default: 101).'
    )

    # Only show --standalone when not running inside a PyInstaller bundle
    is_frozen = getattr(sys, 'frozen', False)

    if not is_frozen:
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
        # Remove --standalone examples from help text when frozen
        parser.epilog = """Examples:
  evasion --encrypt target.py --output stealth.py --add-size 101 --delay 101
  evasion --encrypt target.py --output stealth.py --delay 10
        """

    return parser.parse_args(argv)


def main(argv=None):
    """Entry point for the Evasion Program."""
    print(BANNER)

    args = parse_args(argv)

    # Validate inputs
    if args.add_size < 0:
        print("[ERROR] --add-size must be a non-negative integer.")
        sys.exit(1)
    if args.delay < 0:
        print("[ERROR] --delay must be a non-negative integer.")
        sys.exit(1)
    if not os.path.isfile(args.encrypt):
        print("[ERROR] Target binary '" + args.encrypt + "' not found.")
        sys.exit(1)

    print("[*] Target binary: " + args.encrypt)
    print("[*] Output file: " + args.output)
    print("[*] File size increase: " + str(args.add_size) + " MB")
    print("[*] Execution delay: " + str(args.delay) + " seconds")
    print("[*] Standalone executable: " + ("Yes" if args.standalone else "No"))
    print()

    # If standalone, generate the Python script to a temp location first,
    # then bundle it via PyInstaller
    if args.standalone:
        # Check if running inside a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            print("[ERROR] --standalone is not available inside this pre-built binary.")
            print("[INFO] Use --standalone when running the tool from source with PyInstaller installed.")
            print("[INFO] To build the stealth payload as a script instead, omit --standalone:")
            print("       " + os.path.basename(sys.argv[0]) + " --encrypt " + args.encrypt + " --output " + args.output + " [options]")
            sys.exit(1)

        fd, tmp_script = tempfile.mkstemp(suffix=".py", prefix="hb_evasion_")
        os.close(fd)

        encrypt_binary(
            target_binary=args.encrypt,
            output_file=tmp_script,
            add_size_mb=args.add_size,
            delay_seconds=args.delay,
        )

        print()
        print("[*] Building standalone executable via PyInstaller...")

        try:
            from hiddenbytes.common.builder import build_standalone
        except ImportError:
            print("[ERROR] PyInstaller is required for --standalone mode.")
            print("[INFO] Install it with: pip install pyinstaller")
            print("       or: pip install 'hiddenbytes[standalone]'")
            sys.exit(1)
        final_path = build_standalone(tmp_script, args.output)

        # Clean up temp script
        os.remove(tmp_script)

        final_size = os.path.getsize(final_path)
        print("[SUCCESS] Standalone executable created: '" + final_path + "'")
        print("[INFO] File size: " + str(final_size) + " bytes ("
              + str(final_size / (1024 * 1024)) + " MB)")
        print()
        print("[*] To execute the stealth payload, run:")
        print("    " + final_path)
        print()
    else:
        result = encrypt_binary(
            target_binary=args.encrypt,
            output_file=args.output,
            add_size_mb=args.add_size,
            delay_seconds=args.delay,
        )

        print("[+] Read " + str(result['original_size']) + " bytes from target")
        print("[+] Encryption complete. Encrypted size: " + str(result['encrypted_size']) + " bytes")
        print("\n[SUCCESS] Encryption successful! Encrypted binary saved as '" + result['output_path'] + "'")
        print("[INFO] Final file size: " + str(result['final_size']) + " bytes ("
              + str(result['final_size'] / (1024 * 1024)) + " MB)")

        if args.delay > 0:
            print("[INFO] The payload will delay execution by " + str(args.delay) + " seconds before running.")
        print()
        print("[*] To execute the stealth payload, run:")
        print("    python " + args.output)
        print()


if __name__ == "__main__":
    main()
