import time
import argparse
import can
from math import radians, sin, cos

#
# -----------------------------
#  GNSS Test Values (Edit these)
# -----------------------------
#
LAT_DEG = 46.810000      # Fargo-ish
LON_DEG = -96.810000
SOG = 4.2                # speed over ground (m/s)
COG = 123.0              # course / heading (degrees)
ALT = 299.0              # altitude (m)
HDOP = 0.9
VDOP = 1.1

#
# -----------------------------
#    Utility encoders
# -----------------------------
#

def encode_lat_lon(deg):
    """
    NMEA2000 & J1939 use 1e-7 degrees.
    """
    return int(deg * 1e7)

def encode_double(value, resolution):
    """
    Encodes a float using a simple resolution (e.g., 0.01, 0.1, etc).
    """
    return int(value / resolution)

def pack_u32(value):
    return [
        (value >> 0) & 0xFF,
        (value >> 8) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 24) & 0xFF,
    ]

def pack_u16(value):
    return [(value >> 0) & 0xFF, (value >> 8) & 0xFF]

def pack_u8(value):
    return [value & 0xFF]


#
# -----------------------------------------------------------------------------------
#   Build PGNs
# -----------------------------------------------------------------------------------
#

def pgn_129025_position_rapid(lat_deg, lon_deg):
    """
    NMEA2000 PGN 129025 Position Rapid Update
    Fields:
    - Latitude (1e-7)
    - Longitude (1e-7)
    """
    lat = encode_lat_lon(lat_deg)
    lon = encode_lat_lon(lon_deg)

    return pack_u32(lat) + pack_u32(lon)


def pgn_129026_cog_sog(cog_deg, sog_ms):
    """
    NMEA2000 PGN 129026 - COG/SOG Rapid Update
    COG: resolution 0.0001 rad
    SOG: resolution 0.01 m/s
    """
    cog_rad = radians(cog_deg)
    cog_raw = int(cog_rad / 1e-4)
    sog_raw = int(sog_ms / 0.01)

    return pack_u16(cog_raw) + pack_u16(sog_raw) + [0xFF, 0xFF, 0xFF, 0xFF]


def pgn_129029_gnss_detailed(lat_deg, lon_deg, alt_m, hdop, vdop):
    """
    NMEA2000 PGN 129029 - GNSS Detailed Position
    Extremely simplified for CDL needs.
    """
    lat = encode_lat_lon(lat_deg)
    lon = encode_lat_lon(lon_deg)
    alt = int(alt_m * 100)  # resolution 0.01m

    return (
        pack_u32(lat)
        + pack_u32(lon)
        + pack_u32(alt)
        + pack_u16(int(hdop * 100))
        + pack_u16(int(vdop * 100))
        + [0] * 10  # padding / unused fields
    )[:32]  # enforce 32 bytes (NMEA2k fast-packet)


def pgn_65253_engine_hours(hours=123.4):
    """
    J1939 PGN 65253 (0xFEE5) - Engine Hours
    SPN 247 / 248
    Resolution = 0.05 h
    """
    raw = int(hours / 0.05)
    return pack_u32(raw) + [0xFF] * 4


def pgn_65276_fuel_level(percent=45.0):
    """
    J1939 PGN 65276 (0xFEFC) - Fuel Level
    SPN 96: Fuel Level (0.4%)
    """
    raw = int(percent / 0.4)
    return [raw & 0xFF] + [0xFF] * 7


def pgn_65262_engine_temp(temp_c=82.5):
    """
    J1939 PGN 65262 (0xFEEE) - Engine Temperature
    SPN 110: Engine coolant temp (1°C)
    """
    raw = int(temp_c + 40)  # offset -40C
    return [raw & 0xFF] + [0xFF] * 7


#
# -----------------------------------------------------------------------------------
#   Send CAN frames
# -----------------------------------------------------------------------------------
#

def send_pgn(bus, pgn, data, priority=3, sa=0x23):
    can_id = (priority << 26) | (pgn << 8) | sa
    msg = can.Message(arbitration_id=can_id, data=bytearray(data), is_extended_id=True)
    bus.send(msg)


#
# -----------------------------------------------------------------------------------
#   Main Simulator Loop
# -----------------------------------------------------------------------------------
#

def main():
    parser = argparse.ArgumentParser(description="CDL CAN Simulator")
    parser.add_argument("--interface", required=True, help="kvaser|neovi|pcan|socketcan")
    parser.add_argument("--channel", default="0", help="CAN channel")
    parser.add_argument("--bitrate", type=int, default=250000)
    args = parser.parse_args()

    print("Connecting to CAN...")

    bus = can.Bus(
        interface=args.interface,
        channel=args.channel,
        bitrate=args.bitrate,
    )

    print("CDL CAN Simulator Running")
    print("Press CTRL+C to stop")

    t = 0

    try:
        while True:
            # GNSS
            send_pgn(bus, 129025, pgn_129025_position_rapid(LAT_DEG, LON_DEG))
            send_pgn(bus, 129026, pgn_129026_cog_sog(COG, SOG))

            # J1939 Engine Hours
            if t % 10 == 0:
                send_pgn(bus, 0xFEE5, pgn_65253_engine_hours(123.4))

            # J1939 Fuel Level
            send_pgn(bus, 0xFEFC, pgn_65276_fuel_level(45.0))

            # J1939 Engine Temp
            send_pgn(bus, 0xFEEE, pgn_65262_engine_temp(82.0))

            t += 1
            time.sleep(0.20)

    except KeyboardInterrupt:
        print("\nStopping simulator...")

    finally:
        try:
            bus.shutdown()
        except Exception:
            pass
        print("CAN device closed cleanly.")



if __name__ == "__main__":
    main()
