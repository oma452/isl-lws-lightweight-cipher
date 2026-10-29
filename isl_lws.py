# ISL-LWS Lightweight Cipher (64-bit block, 80-bit key, 16 rounds)
# Omar Shibl (ID: 231147), Ahmed Walid (ID: 220953)
#
# Usage:
#   python isl_lws.py            -> interactive: enter plaintext + key, see all 16 rounds
#   python isl_lws.py --tests    -> run the 4 built-in test cases
#
# Note: the key schedule is a simplified sliding-window variant (see report).

SBOX1 = [0x2, 0xE, 0xD, 0x6, 0x8, 0xA, 0xB, 0x1, 0x5, 0x3, 0x4, 0x9, 0x0, 0xF, 0x7, 0xC]
SBOX2 = [0xF, 0x5, 0xD, 0x8, 0xC, 0x2, 0x4, 0x7, 0x0, 0x9, 0x6, 0xA, 0x1, 0x3, 0xE, 0xB]
PBOX = [3, 2, 0, 1]


def xor(a, b):
    return a ^ b


# 3. Circular left rotation
def rotate_left(x, r, bits=16):
    return ((x << r) & (2**bits - 1)) | (x >> (bits - r))


# 4. S-box substitution layer
def sbox_layer(x):
    out = 0
    for i in range(4):
        nibble = (x >> (i * 4)) & 0xF
        val = SBOX1[nibble] if i % 2 == 0 else SBOX2[nibble]
        out |= (val << (i * 4))
    return out


# 5. P-box permutation layer
def pbox_layer(x):
    chunks = [(x >> (i * 4)) & 0xF for i in range(4)]
    out = 0
    out |= (chunks[0] << (PBOX[0] * 4))  # chunk 0 -> position 3
    out |= (chunks[1] << (PBOX[1] * 4))  # chunk 1 -> position 2
    out |= (chunks[2] << (PBOX[2] * 4))  # chunk 2 -> position 0
    out |= (chunks[3] << (PBOX[3] * 4))  # chunk 3 -> position 1
    return out


# 6. Combined SP layer
def sp_layer(x):
    return pbox_layer(sbox_layer(x))


# 7. Round function F
def F(a, b):
    temp = rotate_left(a, 5)
    temp = xor(temp, b)
    temp = sp_layer(temp)
    return temp


# 8. Key schedule (sliding window)
def generate_keys(key):
    keys = []
    for i in range(16):
        subkey = (key >> (64 - (i * 4))) & 0xFFFF
        keys.append(subkey)
    return keys


# 9. Main encryption function (with 10. intermediate output per round)
def encrypt(plaintext, key, verbose=False):
    keys = generate_keys(key)

    # 2. Splitting the plaintext
    L1 = (plaintext >> 48) & 0xFFFF  # most significant 16 bits
    L2 = (plaintext >> 32) & 0xFFFF
    R1 = (plaintext >> 16) & 0xFFFF
    R2 = plaintext & 0xFFFF          # least significant 16 bits

    if verbose:
        print("\n=== ENCRYPTION START ===")

    for i in range(16):
        L1 = xor(L1, keys[i])                      # Stage 1
        temp = F(L1, L2)                           # Stage 2
        R1 = xor(sbox_layer(R1), temp)             # Stage 3
        R2 = xor(sbox_layer(R2), temp)
        L1, R1 = R1, L1                            # Stage 4
        L2, R2 = R2, L2

        if verbose:
            current_state = (L1 << 48) | (L2 << 32) | (R1 << 16) | R2
            print(f'--- Round {i+1} ---')
            print(f'State: 0x{hex(current_state)[2:].zfill(16)}')

    if verbose:
        print("\n=== ENCRYPTION END ===\n")

    # Final key mixing (whitening) on R2 only
    final_key = (key >> (64 - 16 * 4)) & 0xFFFF
    return (L1 << 48) | (L2 << 32) | (R1 << 16) | (R2 ^ final_key)


# ---------------------------------------------------------------
# Interactive mode: user enters plaintext and key (brief items 1, 4, 5)
# ---------------------------------------------------------------
def interactive():
    print("--- ISL-LWS Lightweight Encryption ---")
    plaintext = int(input("Enter plaintext (64-bit hex): "), 16)
    key = int(input("Enter key (80-bit hex): "), 16)
    ciphertext = encrypt(plaintext, key, verbose=True)
    print(f"Ciphertext: 0x{hex(ciphertext)[2:].zfill(16)}")


# ---------------------------------------------------------------
# Test mode: several input cases (brief item 6)
# ---------------------------------------------------------------
def run_tests():
    tests = [
        ("Test Case 1 (All Zeros)",       0x0000000000000000, 0x00000000000000000000),
        ("Test Case 2 (PT 1-bit Flip)",   0x0000000000000001, 0xFFFFFFFFFFFFFFFFFFFF),
        ("Test Case 3A (Base Key)",       0xFFFFFFFFFFFFFFFF, 0x00000000000000000000),
        ("Test Case 3B (Key 1-bit Flip)", 0xFFFFFFFFFFFFFFFF, 0x00000000000000000001),
    ]
    print("--- ISL-LWS Test Cases ---\n")
    for name, pt, k in tests:
        res = encrypt(pt, k)
        print(f"--- {name} ---")
        print(f"Plaintext:  0x{pt:016X}")
        print(f"Key:        0x{k:020X}")
        print(f"Ciphertext: 0x{res:016X}\n")


if __name__ == "__main__":
    import sys
    if "--tests" in sys.argv:
        run_tests()
    else:
        interactive()
