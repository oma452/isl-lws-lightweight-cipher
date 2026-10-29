# ISL-LWS Lightweight Block Cipher

A Python implementation of a lightweight block cipher, developed for the CSE461 Computer Security course at MSA University.

The project is based on the paper *Development of a New Lightweight Encryption Algorithm* (Khompysh et al., IJACSA, 2023). It implements the encryption process with a 64-bit block, an 80-bit key and 16 rounds, and prints the intermediate state after every round.

> **Educational use only.** This implementation has not been cryptanalysed and must not be used to protect real data.

## Project Files

| File | Description |
|---|---|
| `isl_lws.py` | Python implementation of the cipher (interactive mode and `--tests`) |
| `ISL-LWS_Documentation.docx` | Project report: algorithm description, implementation details, screenshots and test cases |
| `README.md` | This file |

## Authors

- Omar Shibl (ID: 231147)
- Ahmed Walid (ID: 220953)

## Specifications

| Property | Value |
|---|---|
| Block size | 64 bits |
| Key size | 80 bits |
| Rounds | 16 |
| Internal word size | 16 bits (four words: `L1`, `L2`, `R1`, `R2`) |
| S-boxes | Two 4-bit S-boxes (`SBOX1`, `SBOX2`), used alternately |
| P-box | `[3, 2, 0, 1]` (nibble permutation) |
| Language | Python 3, no external dependencies |

## How to Run

```
python isl_lws.py            # interactive mode
python isl_lws.py --tests    # run the built-in test cases
```

**Interactive mode** asks for a 64-bit plaintext and an 80-bit key as hex strings, prints the state after each of the 16 rounds, and then prints the ciphertext.

Example (plaintext `1234567890ABCDEF`, key `1234567890ABCDEF1234`):

```
=== ENCRYPTION START ===
--- Round 1 ---
State: 0xc54248c700005678
...
--- Round 16 ---
State: 0x467a24fcf43a7fe4

=== ENCRYPTION END ===

Ciphertext: 0x467a24fcf43a6dd0
```

## How It Works

The 64-bit plaintext is split into four 16-bit words `[L1 | L2 | R1 | R2]`. Each round (i = 0 to 15) does:

1. **Key mixing:** `L1 = L1 XOR K[i]`
2. **Round function:** `temp = F(L1, L2)`, where `F(a, b) = P-box(S-box(rotate_left(a, 5) XOR b))`
3. **Right-side substitution:** `R1 = S-box(R1) XOR temp` and `R2 = S-box(R2) XOR temp`
4. **Swap:** `L1 <-> R1` and `L2 <-> R2`

After round 16, a final 16-bit key is XORed into `R2`, and the four words are joined into the 64-bit ciphertext.

The S-box layer splits a 16-bit word into four nibbles. Nibbles at positions 0 and 2 use `SBOX1`, and nibbles at positions 1 and 3 use `SBOX2`. The P-box layer then moves nibble `i` to position `PBOX[i]`.

### Key Schedule

`generate_keys()` uses a simplified **sliding-window** schedule. For round `i`, the round key is

```
K[i] = (key >> (64 - 4*i)) & 0xFFFF
```

and the final key is `key & 0xFFFF`. This is a simplified variant. In the paper, the 80-bit key is split into five 16-bit sub-blocks, and the round keys are derived using a 4-bit S-box and addition modulo 2^16. This implementation does not do that.

## Test Cases

Run `python isl_lws.py --tests` to reproduce these results.

| Test | Plaintext | Key | Ciphertext |
|---|---|---|---|
| 1 (all zeros) | `0000000000000000` | `00000000000000000000` | `F7F1F7F140A640A6` |
| 2 (plaintext 1-bit flip) | `0000000000000001` | `FFFFFFFFFFFFFFFFFFFF` | `643EB8BBAF3B1C86` |
| 3A (base key) | `FFFFFFFFFFFFFFFF` | `00000000000000000000` | `69DD69DD84F484F4` |
| 3B (key 1-bit flip) | `FFFFFFFFFFFFFFFF` | `00000000000000000001` | `69DD69DD84F484F5` |

## Limitations

- **Weak key bit sensitivity.** Because of the simplified key schedule, the lowest key bits affect only the final key XOR on `R2`. In tests 3A and 3B, flipping key bit 0 changes just 1 of the 64 ciphertext bits. A stronger schedule would change about half of them.
- **Stage 1 differs from the paper's text.** The paper says the 64-bit plaintext block is XORed with the round key before it is split into four sub-blocks. This implementation instead XORs a 16-bit round key into `L1` only, at the start of each round.
- **Encryption only.** There is no decryption function.
- **Integers only.** Plaintext and key are handled as integers (hex input). There is no text encoding, padding, or support for messages longer than one block.
- **Not verified against official test vectors.** The implementation follows the paper's structure but has not been checked against reference vectors.

## Reference

A. Khompysh, N. Kapalova, O. Lizunov, D. Dyusenbayev, and K. Sakan, "Development of a New Lightweight Encryption Algorithm," *International Journal of Advanced Computer Science and Applications (IJACSA)*, vol. 14, no. 5, pp. 452-459, 2023.
