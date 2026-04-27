"""Bit-level encoding helpers for the covert timing channel demo.

This module keeps the text-to-bits and XOR masking steps pure so they can be
tested independently from the networking layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EncodedMessage:
    """Container for the intermediate encoding stages."""

    text: str
    plain_bits: str
    masked_bits: str
    key_bits: str


def text_to_binary(text: str) -> str:
    """Convert UTF-8 text into a binary string."""

    utf8_bytes = text.encode("utf-8")
    return "".join(f"{byte:08b}" for byte in utf8_bytes)


def _key_to_bits(key: str) -> str:
    if not key:
        raise ValueError("key must not be empty")

    return text_to_binary(key)


def xor_mask_bits(bits: str, key: str) -> str:
    """XOR each bit with a repeating key bit pattern."""

    if any(bit not in {"0", "1"} for bit in bits):
        raise ValueError("bits must contain only '0' and '1'")

    key_bits = _key_to_bits(key)
    masked_bits = []

    for index, bit in enumerate(bits):
        key_bit = key_bits[index % len(key_bits)]
        masked_bits.append("1" if bit != key_bit else "0")

    return "".join(masked_bits)


def encode_text(text: str, key: str) -> EncodedMessage:
    """Encode text into plain bits and key-masked bits."""

    plain_bits = text_to_binary(text)
    key_bits = _key_to_bits(key)
    masked_bits = xor_mask_bits(plain_bits, key)
    return EncodedMessage(
        text=text,
        plain_bits=plain_bits,
        masked_bits=masked_bits,
        key_bits=key_bits,
    )


__all__ = [
    "EncodedMessage",
    "encode_text",
    "text_to_binary",
    "xor_mask_bits",
]