# MetaMorph - Project TODO

## 🧠 1. Preparation
- [ ] Learn basics of PE (Windows executable format)
- [ ] Understand how binaries are stored as raw bytes
- [ ] Learn file I/O in C (read/write binary files)
- [ ] Understand XOR encryption (simple byte-level encryption)

---

## ⚙️ 2. Evasion Program (Core Tool)

### 📦 Input/Output system
- [ ] Parse CLI arguments (`--encrypt`, `--output`, `--add-size`, `--delay`)
- [ ] Read target binary file into memory
- [ ] Write output binary file

### 🔐 Encryption
- [ ] Implement XOR encryption/decryption for binary data
- [ ] Store encryption key in metadata or header

### 📏 File modification
- [ ] Append junk bytes to increase file size (e.g. 101MB)
- [ ] Ensure original functionality is preserved

### ⏳ Execution control
- [ ] Add execution delay (sleep before running payload)
- [ ] Load encrypted payload after delay

### 🚀 Loader behavior
- [ ] Decrypt embedded binary at runtime
- [ ] Execute original program (via temp file or system call)

---

## 🧬 3. Polymorphic Program

### 🔁 Generator
- [ ] Create program that generates modified binaries
- [ ] Randomize encryption key per build
- [ ] Add random padding / junk data

### 🧠 Self-modification concept
- [ ] Ensure output binaries are structurally different each time
- [ ] Maintain same execution behavior

### 💥 Reverse shell payload (simulation)
- [ ] Understand socket-based reverse connection concept
- [ ] Embed payload logic (for controlled lab use only)

---

## 🧪 4. Testing Environment
- [ ] Set up Windows VM (isolated)
- [ ] Test execution safely inside VM only
- [ ] Verify delay, encryption, and execution flow
- [ ] Confirm file modification (size changes)

---

## 🛡️ 5. Detection & Analysis (README section)
- [ ] Document how encryption works
- [ ] Explain evasion techniques used (high-level)
- [ ] Explain polymorphism concept
- [ ] Describe how such techniques are detected (signatures, heuristics)
- [ ] Add ethical & legal considerations

---

## 📄 6. Documentation (README.md)
- [ ] Project overview
- [ ] Usage examples (CLI commands)
- [ ] Architecture explanation
- [ ] Technical breakdown
- [ ] Defensive recommendations

---

## ⭐ Bonus (Optional)
- [ ] Add logging system
- [ ] Add simple GUI
- [ ] Improve encryption method
- [ ] Build detection tool for your own binaries