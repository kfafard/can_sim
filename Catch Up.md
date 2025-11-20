Hahaha absolutely — let’s get you set up so “Vacation Kurtis” can return in December and actually understand what the hell “Past Kurtis” built.

Here’s a clean, readable **README.md** you can drop directly into your repo.

---

# 📘 CDL CAN Simulator

*A lightweight Python-based CAN message generator for testing the CDL logger (J1939 + NMEA2000 GNSS).*

This tool sends a curated set of CAN messages used by the CDL proof-of-concept, including:

* **NMEA2000 GNSS PGNs**

  * PGN **129025** – Position Rapid Update
  * PGN **129026** – COG/SOG Rapid Update
    *(129029 removed — requires multipacket TP)*

* **J1939 PGNs**

  * PGN **0xFEE5 (65253)** – Engine Hours
  * PGN **0xFEFC (65276)** – Fuel Level
  * PGN **0xFEEE (65262)** – Engine Coolant Temperature

Supports **neoVI / ValueCAN**, **Kvaser**, **PCAN**, and **SocketCAN**.

Perfect for CDL firmware testing when no tractor is available and Saskatchewan is frozen solid.

---

## 🚀 1. Requirements

### Install Python 3.14

Already done (based on your logs).

### Install python-can

```powershell
py -3.14 -m pip install python-can
```

---

## 📂 2. Files in This Folder

| File         | Description                   |
| ------------ | ----------------------------- |
| `can_sim.py` | Main CDL CAN simulator script |
| `README.md`  | This file                     |

No other dependencies required.

---

## ▶️ 3. Running the Simulator

The simulator runs continuously until you press **CTRL+C**.

### Example: neoVI / ValueCAN

```powershell
py -3.14 can_sim.py --interface neovi --channel 1
```

### Example: Kvaser Leaf

```powershell
py -3.14 can_sim.py --interface kvaser --channel 0
```

### Example: PCAN USB

```powershell
py -3.14 can_sim.py --interface pcan --channel PCAN_USBBUS1
```

### SocketCAN (Linux)

```bash
python3 can_sim.py --interface socketcan --channel can0
```

---

## 🛰 4. What It Actually Sends (Data Format)

### GNSS Position (PGN 129025)

* Latitude  → 1e-7 degrees
* Longitude → 1e-7 degrees
* Always 8 bytes → safe for classic CAN
* CDL uses this for quick GPS locks

### GNSS Motion (PGN 129026)

* Course over ground → 0.0001 rad
* Speed over ground  → 0.01 m/s
* Also safe 8-byte frame

### Engine Hours (PGN 65253)

* 0.05 h resolution
* Good for “tractor is alive” signal

### Fuel Level (PGN 65276)

* 0.4% resolution

### Coolant Temp (PGN 65262)

* SPN 110
* Offset: −40°C

---

## 🎛 5. Adjusting Test Values

At the top of the script:

```python
LAT_DEG = 46.810000
LON_DEG = -96.810000
SOG = 4.2
COG = 123.0
ALT = 299.0
HDOP = 0.9
VDOP = 1.1
```

Edit these to simulate movement or rough GNSS quality.

You can change these *during* testing and rerun instantly.

---

## ⛔ Why PGN 129029 Isn’t Sent

PGN 129029 (GNSS Detailed Position) is **26 bytes**, which requires:

* J1939 Transport Protocol (TP.CM + TP.DT), or
* NMEA2000 fast-packet mode

**neoVI in python-can = classic CAN only**, so DLC > 8 fails.

The simulator focuses on CDL-supported rapid GNSS messages.

If CDL later needs TP support, we can implement it.

---

## 🔚 Clean Shutdown

The program now catches **CTRL+C** and calls:

```python
bus.shutdown()
```

so you don’t get spammy:

```
NeoViBus was not properly shut down
```

messages anymore.

---

## 🧩 6. Future Extensions (easy add-ons)

If you want, you can easily bolt on:

* Tractor wheel speeds
* Steering angle
* Hitch position
* Hydraulic pressures
* A simulated “driving path”
* Yield & mass-flow messages for AGCO combines
* ISOBUS VT button events
* Engine RPM, torque, load

Just add:

```
“Add PGN XXXX”
```

and I’ll wire it in.

---

## 🎉 7. Summary (for Future-Kurtis Returning From Holidays)

This folder gives you a plug-and-play GNSS + tractor-data CAN generator.
Run it with your ValueCAN/neoVI → your CDL reads the activity.
It’s stable, safe, and doesn’t require real equipment.
