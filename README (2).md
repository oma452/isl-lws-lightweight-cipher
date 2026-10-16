# ISL-LWS Lightweight Cipher

ISL-LWS is a 64-bit lightweight block cipher with an 80-bit key, implemented in pure Python. It uses a 4-branch Feistel-like structure with two 4-bit S-boxes, a nibble-level P-box, and a rotating key schedule over 16 rounds.

> **Disclaimer:** This project was built for educational and coursework purposes. It has not been cryptanalyzed and must not be used to protect real data.

## Specifications

| Property        | Value                          |
|-----------------|--------------------------------|
| Block size      | 64 bits                        |
| Key size        | 80 bits                        |
| Rounds          | 16                             |
| Word size       | 16 bits (four words per block) |
| Structure       | 4-branch Feistel-like network  |
| Language        | Python 3 (no dependencies)     |

## How it works

The 64-bit plaintext is split into four 16-bit words: `L1`, `L2`, `R1`, `R2`.

**Each round:**

1. XOR the round key into `L1`.
2. Compute `temp = F(L1, L2)`.
3. Update the right words: `R1 = S(R1) XOR temp` and `R2 = S(R2) XOR temp`.
4. Swap `L1 <-> R1` and `L2 <-> R2`.

After 16 rounds, a final key is XORed into all four words, and the words are concatenated into the 64-bit ciphertext.

**Round function `F(a, b)`:**

```
F(a, b) = PBOX( SBOX( rotl16(a, 5) XOR b ) )
```

**Components:**

- **S-box layer:** alternates `SBOX1` and `SBOX2` across the four nibbles of a 16-bit word. Both S-boxes are bijective.
- **P-box layer:** permutes nibble positions using `PBOX = [3, 2, 0, 1]`.
- **Key schedule:** the 80-bit key register is rotated left by 61 bits each round, and a round counter is XORed in. The top 16 bits of the register become the round key, so every key bit influences the round keys. 16 round keys and 1 final key are produced.

## Usage

```python
from isl_lws import encrypt, decrypt

plaintext = 0x0123456789ABCDEF           # 64-bit block
key       = 0x00112233445566778899       # 80-bit key

ciphertext = encrypt(plaintext, key)
recovered  = decrypt(ciphertext, key)

print(f"Ciphertext: 0x{ciphertext:016X}")
assert recovered == plaintext
```

Run the built-in test cases:

```bash
python isl_lws.py
```

## Test results

| Test case                    | Plaintext            | Key                      | Ciphertext           |
|------------------------------|----------------------|--------------------------|----------------------|
| 1: All zeros                 | `0000000000000000`   | `00000000000000000000`   | `A25CA253C62B5605`   |
| 2: Plaintext 1-bit flip      | `0000000000000001`   | `FFFFFFFFFFFFFFFFFFFF`   | `212FF5016197097A`   |
| 3A: Base key                 | `FFFFFFFFFFFFFFFF`   | `00000000000000000000`   | `7EE80EEA6D592D7E`   |
| 3B: Key 1-bit flip           | `FFFFFFFFFFFFFFFF`   | `00000000000000000001`   | `2151B15652F6E326`   |

**Avalanche behavior:**

- Flipping 1 key bit (3A vs 3B) changes 43 of 64 ciphertext bits.
- Flipping 1 plaintext bit (all zeros, key 0) changes 35 of 64 ciphertext bits.

An ideal cipher changes about 32 bits on average.

Every test case is also checked to decrypt back to its original plaintext.

## Project structure

```
.
├── isl_lws.py    # cipher implementation, decryption, and test cases
└── README.md
```

## Authors

- Omar Shibl (ID: 231147)
- Ahmed Walid (ID: 220953)

## License

MIT License. Replace this section if your course or instructor requires something different.
