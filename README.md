README.md (full contents)
# CDL CAN Simulator (`can_sim.py`)

Small, single-file CAN message simulator used for CDL (CAN Data Logger) development and testing.

It connects to a CAN interface (e.g. Intrepid neoVI) using `python-can` and periodically transmits a small set of J1939 / GNSS-related PGNs so the CDL can be exercised on the bench without a tractor/combine hooked up.

> Future Kurtis: this is the tool you used in November 2025 to fake a machine on the CAN bus when there was no iron running. 😄

---

## Features

- Connects to any `python-can` backend (tested with **Intrepid neoVI**).
- Periodically transmits a set of CDL-relevant PGNs, including GNSS data:
  - e.g. PGN 129029 (GNSS detailed) and related messages (see `can_sim.py` for exact list).
- Simple CLI to choose CAN interface and channel.
- Designed to be easy to hack:
  - Add/remove PGNs
  - Change update rates
  - Hard-code test positions / routes

---

## Requirements

- **Python** 3.11+ (tested with 3.14 on Windows)
- **python-can** installed:

```bash
pip install python-can


For neoVI:

Intrepid drivers + neoVI Explorer installed

A working python-can neovi config (this script uses the neovi interface directly)

Files

can_sim.py – the entire simulator in one file.

README.md – this document.

Usage

From the project folder (where can_sim.py lives):

Windows / neoVI example
py -3.14 can_sim.py --interface neovi --channel 1


You should see:

Connecting to CAN...
CDL CAN Simulator Running
Press CTRL+C to stop


Press CTRL+C to stop the simulator.
The script will try to shut the CAN interface down cleanly on exit.

General CLI options

Run:

python can_sim.py --help


Typical options (depending on how the script is currently written):

--interface – python-can interface name, e.g. neovi, socketcan, pcan, etc.

--channel – hardware channel (e.g. 1, 0, vcan0, etc.).

--bitrate – CAN bitrate if applicable (e.g. 250000 or 500000).

Check the top of can_sim.py for the exact arguments and defaults currently in use.

How it works (high level)

Parses CLI arguments.

Creates a python-can Bus using the chosen interface/channel.

In a loop (e.g. ~5 Hz for GNSS, slower for other PGNs):

Builds CAN frames for each configured PGN.

Sends them on the bus via bus.send(msg).

Handles CTRL+C (KeyboardInterrupt) and attempts to cleanly close the bus.

If you’re trying to remember where to tweak things:

Which PGNs are sent and how often – look near the main() function where the loop calls helpers like pgn_129029_gnss_detailed(...) and send_pgn(...).

GNSS position / test values – search for LAT_DEG, LON_DEG, ALT, HDOP, VDOP and edit them.

Extending the simulator

To add a new PGN:

Create a helper that returns a payload:

def pgn_XXXXXX_something(...):
    data = bytearray(8)  # or appropriate length
    # pack fields into data[…]
    return data


Add a call in the main loop:

send_pgn(bus, 123456, pgn_XXXXXX_something(...))


Adjust the loop timing if you want a different update rate.

Troubleshooting

ValueError: DLC was X but it should be <= 8
You’re trying to send more than 8 bytes on a normal CAN frame.

Ensure multi-frame / transport-layer messages are correctly handled, or

Trim/repack payloads to 8 bytes for simple bench testing.

No traffic seen on the bus

Check that the interface name and channel match the hardware.

Confirm bitrate matches the rest of the network.

Verify with a CAN tool (e.g. ValueCAN/neoVI software, PCAN View, CANalyzer, etc.).

License

TBD – personal utility project.
