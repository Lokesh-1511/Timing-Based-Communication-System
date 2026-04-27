# Timing-Based Communication System

A Python project that demonstrates covert communication by encoding data in packet timing intervals instead of packet payloads.

## Overview

This project sends hidden messages over TCP by controlling the delay between packets.

- `sender.py` encodes text into bits, applies XOR masking, maps bits to relative delays, and sends timed packets.
- `receiver.py` records packet arrival times, decodes relative timing changes back into bits, unmasks with the key, and reconstructs the text.
- `visualizer.py` plots sender and receiver timing sequences for analysis.

## Modules

- `encoder.py`: text-to-bits and XOR masking
- `decoder.py`: bit unmasking and text recovery
- `modulator.py`: bit-to-delay modulation with jitter
- `analyzer.py`: delay-delta classification and bitstream recovery
- `sender.py`: TCP sender for timed packet transmission
- `receiver.py`: TCP receiver for timing-based decoding
- `visualizer.py`: timing summaries and matplotlib plots

## How It Works

1. Convert plaintext to binary.
2. XOR mask bits using a repeating key.
3. Convert masked bits to relative timing delays.
4. Send one sync packet, then data packets at those delays.
5. Receiver computes arrival delays and classifies timing deltas.
6. Recovered masked bits are XOR-unmasked to get original text.

## Run

Open two terminals in the repository folder.

Terminal 1:

```bash
python receiver.py
```

Terminal 2:

```bash
python sender.py
```

Use the same masking key on both sides.

## Output

- Console logs for sent/received packets and decoded text
- Timing plots:
  - `sender_timing_plot.png`
  - `receiver_timing_plot.png`

## Requirements

- Python 3.10+
- `matplotlib` (for plotting)

Install plotting dependency:

```bash
pip install matplotlib
```
