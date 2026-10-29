# ISL-LWS Lightweight Block Cipher

A Python implementation of a lightweight block cipher developed as part of the CSE461 Computer Security course at MSA University.

The project is based on the research paper *Development of a New Lightweight Encryption Algorithm*. It implements encryption, decryption, a key schedule, and basic tests to examine the implementation's behavior.

> **Educational use only:** This implementation has not undergone comprehensive cryptanalysis and must not be used to protect sensitive real-world data.

## Overview

A block cipher encrypts a fixed-size block of data using a secret key.

This implementation processes 64-bit plaintext blocks with an 80-bit key and performs 16 rounds of transformations. It uses XOR operations, bit rotations, substitution boxes (S-boxes), a permutation box (P-box), and a four-word internal state.

The implementation includes encryption and decryption functions and tests whether decryption recovers the original plaintext.

**Important:** The implementation has not been independently verified as an exact reproduction of every step in the referenced research paper.

## Specifications

| Property | Value |
|---|---|
| Block size | 64 bits |
| Key size | 80 bits |
| Number of rounds | 16 |
| Internal word size | 16 bits |
| Internal state | Four 16-bit words |
| Language | Python 3 |
| External dependencies | None |

## How It Works

### 1. Block Representation

The plaintext is divided into four 16-bit words:

- `L1`
- `L2`
- `R1`
- `R2`

These words form the internal state that is transformed during encryption.

The implementation accepts plaintext and key values as integers. It does not directly encrypt text strings or implement arbitrary-length message processing, text encoding, or padding.

### 2. Encryption Operations

The implementation uses the following operations:

- **XOR:** Combines two bit patterns using exclusive OR.
- **Bit rotation:** Rotates the bits of a 16-bit word.
- **S-box substitution:** Replaces each 4-bit nibble using a lookup table.
- **P-box permutation:** Rearranges nibble positions.
- **Round transformations:** Update and swap the internal state over 16 rounds.

The round function is implemented as:

```python
F(a, b) = PBOX(SBOX(rotate_left(a, 5) ^ b))
```

The code alternates between two S-box lookup tables when processing the nibbles of a 16-bit word.

The P-box uses the mapping:

```python
PBOX = [3, 2, 0, 1]
```

### 3. Key Schedule

The `generate_keys()` function takes an integer key and derives 16 round keys and one final key.

The current implementation:

1. Masks the key to 80 bits.
2. Extracts the top 16 bits of the key register.
3. Rotates the 80-bit register left by 61 bits.
4. Injects a round counter using XOR.
5. Repeats the process to generate the round keys and final key.

The final key is XORed with all four 16-bit state words after the 16 rounds. This is the final whitening step in the current implementation.

**Implementation note:** The key schedule, round-key usage, and final whitening have not been verified as equivalent to the corresponding steps in the original research paper.

## Requirements

- Python 3
- No external Python packages required

## Usage

Import `encrypt` and `decrypt` from `isl_lws.py`:

```python
from isl_lws import encrypt, decrypt

# 64-bit plaintext block
plaintext = 0x0123456789ABCDEF

# 80-bit key
key = 0x00112233445566778899

# Encrypt
ciphertext = encrypt(plaintext, key)

# Decrypt
recovered = decrypt(ciphertext, key)

print(f"Ciphertext: 0x{ciphertext:016X}")
print(f"Recovered:  0x{recovered:016X}")

assert recovered == plaintext
```

For the intended input sizes, plaintext values should fit within 64 bits and key values within 80 bits. The current implementation does not explicitly reject out-of-range inputs.

## Running the Tests

Run the built-in test cases from the repository directory:

```bash
python isl_lws.py
```

The script tests four plaintext/key combinations:

1. All-zero plaintext and key.
2. A plaintext with one bit set and an all-ones key.
3. An all-ones plaintext and an all-zero key.
4. An all-ones plaintext and a key with one bit set.

Each test checks that decrypting the generated ciphertext recovers the original plaintext.

The script also compares ciphertexts to measure the effect of changing one plaintext bit or one key bit.

## Test Results and Avalanche Measurements

The recorded measurements are:

| Measurement | Changed input | Different ciphertext bits |
|---|---|---|
| Key avalanche | One key bit changed | 43 out of 64 |
| Plaintext avalanche | One plaintext bit changed | 35 out of 64 |

For an idealized block cipher, changing one input bit is expected to change approximately half of the ciphertext bits on average.

These results are observations from selected inputs, not proof of security. They do not establish resistance to brute-force attacks, differential cryptanalysis, linear cryptanalysis, or other cryptographic attacks.

Run `python isl_lws.py` to execute the current tests and obtain the ciphertext outputs and measurements directly from the implementation.

## Limitations

- The implementation operates on fixed-size numerical blocks, not arbitrary-length messages.
- Text encoding, padding, and message framing are not implemented.
- Input sizes are not explicitly validated by the encryption and decryption functions.
- The built-in tests cover selected examples rather than exhaustive correctness testing.
- Avalanche measurements alone cannot establish cryptographic security.
- The implementation has not undergone comprehensive cryptanalysis.
- Exact equivalence to the original research paper has not been established.
- The implementation should not be used for real-world data protection.

## Project Structure

```text
isl-lws-lightweight-cipher/
├── isl_lws.py
└── README.md
```

## References

Khompysh, A., Kapalova, N., Lizunov, O., Dyusenbayev, D., & Sakan, K. (2023). *Development of a New Lightweight Encryption Algorithm*. **International Journal of Advanced Computer Science and Applications, 14**(5).

- **DOI:** https://doi.org/10.14569/IJACSA.2023.0140548
- **Publisher page:** https://thesai.org/Publications/ViewPaper?Code=IJACSA&Issue=5&SerialNo=48&Volume=14

The paper is the research reference identified by the CSE461 course specification. The implementation's exact equivalence to the paper has not been independently established.

## Authors

- Omar Shibl
- Ahmed Walid

## License

Add a valid `LICENSE` file before claiming that the project is distributed under the MIT License. If the repository does not contain a license file, the licensing terms have not been established by this README.
