"""Binary decoding helpers for the covert timing channel demo."""

from __future__ import annotations

from encoder import xor_mask_bits


def binary_to_text(bits: str, *, strict: bool = False) -> str:
    """Convert a binary string back into UTF-8 text."""

    if any(bit not in {"0", "1"} for bit in bits):
        raise ValueError("bits must contain only '0' and '1'")

    remainder = len(bits) % 8
    if remainder and strict:
        raise ValueError("bit stream length must be a multiple of 8 in strict mode")

    usable_bits = bits[: len(bits) - remainder] if remainder else bits
    if not usable_bits:
        return ""

    raw_bytes = bytes(int(usable_bits[index : index + 8], 2) for index in range(0, len(usable_bits), 8))
    return raw_bytes.decode("utf-8")


def unmask_bits(masked_bits: str, key: str) -> str:
    """Reverse the repeating-key XOR masking."""

    return xor_mask_bits(masked_bits, key)


def decode_binary_message(masked_bits: str, key: str, *, strict: bool = False) -> str:
    """Unmask a bit stream and recover the original UTF-8 text."""

    plain_bits = unmask_bits(masked_bits, key)
    return binary_to_text(plain_bits, strict=strict)


__all__ = ["binary_to_text", "decode_binary_message", "unmask_bits"]