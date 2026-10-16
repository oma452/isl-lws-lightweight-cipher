# =========================================================
# ISL-LWS Lightweight Cipher (fixed)
# Omar Shibl (ID: 231147), Ahmed Walid (ID: 220953)
# =========================================================

SBOX1 = [0x2, 0xE, 0xD, 0x6, 0x8, 0xA, 0xB, 0x1,
         0x5, 0x3, 0x4, 0x9, 0x0, 0xF, 0x7, 0xC]

SBOX2 = [0xF, 0x5, 0xD, 0x8, 0xC, 0x2, 0x4, 0x7,
         0x0, 0x9, 0x6, 0xA, 0x1, 0x3, 0xE, 0xB]

INV_SBOX1 = [SBOX1.index(i) for i in range(16)]
INV_SBOX2 = [SBOX2.index(i) for i in range(16)]

PBOX = [3, 2, 0, 1]
INV_PBOX = [PBOX.index(i) for i in range(4)]

MASK16 = 0xFFFF
MASK80 = (1 << 80) - 1
ROUNDS = 16


def rotate_left(x, r, bits=16):
    r %= bits
    return ((x << r) & ((1 << bits) - 1)) | (x >> (bits - r))


def sbox_layer(x, inverse=False):
    s1, s2 = (INV_SBOX1, INV_SBOX2) if inverse else (SBOX1, SBOX2)
    out = 0
    for i in range(4):
        nibble = (x >> (i * 4)) & 0xF
        val = s1[nibble] if i % 2 == 0 else s2[nibble]
        out |= val << (i * 4)
    return out


def pbox_layer(x, inverse=False):
    p = INV_PBOX if inverse else PBOX
    out = 0
    for i in range(4):
        out |= ((x >> (i * 4)) & 0xF) << (p[i] * 4)
    return out


def sp_layer(x):
    return pbox_layer(sbox_layer(x))


def F(a, b):
    return sp_layer(rotate_left(a, 5) ^ b)


def generate_keys(key):
    """80-bit key -> 16 round keys + 1 final key.
    The key register is rotated every round so EVERY key bit
    influences the round keys (the old sliding window left
    bits 0-3 affecting only the final whitening key)."""
    reg = key & MASK80
    keys = []
    for i in range(ROUNDS + 1):
        keys.append((reg >> 64) & MASK16)
        reg = ((reg << 61) | (reg >> 19)) & MASK80   # rotate left 61
        reg ^= (i + 1) << 15                          # round-counter injection
    return keys[:ROUNDS], keys[ROUNDS]


def encrypt(plaintext, key):
    keys, final_key = generate_keys(key)

    L1 = (plaintext >> 48) & MASK16
    L2 = (plaintext >> 32) & MASK16
    R1 = (plaintext >> 16) & MASK16
    R2 = plaintext & MASK16

    for i in range(ROUNDS):
        L1 ^= keys[i]
        temp = F(L1, L2)
        R1 = sbox_layer(R1) ^ temp
        R2 = sbox_layer(R2) ^ temp
        L1, R1 = R1, L1
        L2, R2 = R2, L2

    # Final whitening applied to all four words
    L1 ^= final_key; L2 ^= final_key; R1 ^= final_key; R2 ^= final_key
    return (L1 << 48) | (L2 << 32) | (R1 << 16) | R2


def decrypt(ciphertext, key):
    keys, final_key = generate_keys(key)

    L1 = ((ciphertext >> 48) & MASK16) ^ final_key
    L2 = ((ciphertext >> 32) & MASK16) ^ final_key
    R1 = ((ciphertext >> 16) & MASK16) ^ final_key
    R2 = (ciphertext & MASK16) ^ final_key

    for i in reversed(range(ROUNDS)):
        L1, R1 = R1, L1          # undo swap
        L2, R2 = R2, L2
        temp = F(L1, L2)         # L1 here already holds (L1 ^ key)
        R1 = sbox_layer(R1 ^ temp, inverse=True)
        R2 = sbox_layer(R2 ^ temp, inverse=True)
        L1 ^= keys[i]
    return (L1 << 48) | (L2 << 32) | (R1 << 16) | R2


if __name__ == "__main__":
    tests = [
        ("Test Case 1 (All Zeros)",       0x0000000000000000, 0x00000000000000000000),
        ("Test Case 2 (PT 1-bit Flip)",   0x0000000000000001, 0xFFFFFFFFFFFFFFFFFFFF),
        ("Test Case 3A (Base Key)",       0xFFFFFFFFFFFFFFFF, 0x00000000000000000000),
        ("Test Case 3B (Key 1-bit Flip)", 0xFFFFFFFFFFFFFFFF, 0x00000000000000000001),
    ]

    print("--- ISL-LWS Test Cases for Report ---\n")
    results = {}
    for name, pt, k in tests:
        ct = encrypt(pt, k)
        results[name] = ct
        assert decrypt(ct, k) == pt, "decrypt mismatch!"
        print(f"--- {name} ---")
        print(f"Plaintext:  0x{pt:016X}")
        print(f"Key:        0x{k:020X}")
        print(f"Ciphertext: 0x{ct:016X}\n")

    a = results["Test Case 3A (Base Key)"]
    b = results["Test Case 3B (Key 1-bit Flip)"]
    print(f"Key avalanche (3A vs 3B): {bin(a ^ b).count('1')}/64 bits differ")
    z = results["Test Case 1 (All Zeros)"]
    p = encrypt(0x1, 0x0)
    print(f"Plaintext avalanche (0 vs 1, key 0): {bin(z ^ p).count('1')}/64 bits differ")
