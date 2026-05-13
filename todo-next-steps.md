# MetaMorph - Revised TODO

## 1. Current State Review
- [ ] Mark completed CLI parsing work
- [ ] Mark completed input file loading work
- [ ] Mark completed output file writing work
- [ ] Mark partial XOR encryption work
- [ ] Mark incomplete delay/execution behavior
- [ ] Mark incomplete output format design

## 2. Core Program Cleanup
- [x] Remove outdated `TODO` comment inside `encrypt_input_binary`
- [x] Move hardcoded XOR key into a defined header/metadata structure
- [x] Define a clear output file layout
- [ ] Add constants for metadata/header fields
- [ ] Add validation for malformed or truncated output files

## 3. Output Format
- [ ] Design a simple file header with magic bytes
- [ ] Store encryption key information in the file format
- [ ] Store original payload size in the file format
- [ ] Store padding size in the file format
- [ ] Store delay value in the file format
- [ ] Document the byte layout of the output format

## 4. Encryption Work
- [ ] Refactor XOR logic into a reusable function
- [ ] Add matching decryption logic for test verification
- [ ] Verify encrypted output differs from input
- [ ] Verify decrypted output matches original input
- [ ] Replace fixed key with generated per-build or per-file key

## 5. File Modification
- [ ] Keep optional padding behavior
- [ ] Verify output size increases by expected amount
- [ ] Confirm metadata is appended or stored exactly as designed
- [ ] Test edge cases for `--add-size 0`, minimum, and maximum values

## 6. Delay Handling
- [ ] Clarify whether delay is metadata-only or part of a future runner format
- [ ] Validate `--delay` bounds with tests
- [ ] Verify delay value is written and read correctly

## 7. Testing
- [ ] Create small sample binary fixtures for testing
- [ ] Add round-trip tests for read -> encrypt -> write
- [ ] Add tests for invalid CLI arguments
- [ ] Add tests for missing files
- [ ] Add tests for empty input files
- [ ] Add tests for padding size calculations
- [ ] Add tests for metadata parsing

## 8. Defensive Tooling
- [ ] Build a parser that inspects generated files
- [ ] Print header, key metadata, payload size, padding size, and delay
- [ ] Add a verification mode that checks file integrity
- [ ] Add a diff/report mode for comparing two generated outputs

## 9. Documentation
- [ ] Write a project overview
- [ ] Document supported CLI options
- [ ] Add usage examples
- [ ] Explain the file layout at a high level
- [ ] Explain the XOR routine at a high level
- [ ] Add a limitations section
- [ ] Add ethical and legal notes

## 10. Detection and Analysis
- [ ] Describe static indicators defenders could inspect
- [ ] Describe how padding and metadata can be detected
- [ ] Describe how repeated-key XOR can be recognized
- [ ] Add recommendations for safe lab-only analysis

## 11. Nice-to-Have Improvements
- [ ] Add structured logging
- [ ] Add a `--inspect` mode
- [ ] Add a `--verify` mode
- [ ] Improve naming and code organization
- [ ] Split `main.c` into smaller modules if the project grows
