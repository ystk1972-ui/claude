import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math

_VERSION = "1.4.2"

# ============================================================
# ISO/JIS ねじ規格データベース（オフライン内蔵）
# ============================================================

# メートルねじ (M) — JIS B 0205-4 / ISO 724
# key: (呼び径, ピッチ)  value: (d2, d1, D1)
#   d2 = d - 0.649519P  基準有効径（JIS B 0205-4）
#   d1 = d - 1.226869P  外ねじ小径（JIS B 0205-4）
#   D1 = d - 1.082532P  内ねじ小径（JIS B 0205-4）
METRIC_THREAD = {
    ("M1",    0.25): (0.838,  0.693, 0.729),
    ("M1.2",  0.25): (1.038,  0.893, 0.929),
    ("M1.4",  0.3):  (1.205,  1.032, 1.075),
    ("M1.6",  0.35): (1.373,  1.171, 1.221),
    ("M2",    0.4):  (1.740,  1.509, 1.567),
    ("M2.5",  0.45): (2.208,  1.948, 2.013),
    ("M3",    0.5):  (2.675,  2.387, 2.459),
    ("M3.5",  0.6):  (3.110,  2.764, 2.850),
    ("M4",    0.7):  (3.545,  3.141, 3.242),
    ("M5",    0.8):  (4.480,  4.019, 4.134),
    ("M6",    1.0):  (5.350,  4.773, 4.917),
    ("M7",    1.0):  (6.350,  5.773, 5.917),
    ("M8",    1.25): (7.188,  6.466, 6.647),
    ("M10",   1.5):  (9.026,  8.160, 8.376),
    ("M12",   1.75): (10.863, 9.853, 10.106),
    ("M14",   2.0):  (12.701, 11.546, 11.835),
    ("M16",   2.0):  (14.701, 13.546, 13.835),
    ("M18",   2.5):  (16.376, 14.933, 15.294),
    ("M20",   2.5):  (18.376, 16.933, 17.294),
    ("M22",   2.5):  (20.376, 18.933, 19.294),
    ("M24",   3.0):  (22.051, 20.319, 20.752),
    ("M27",   3.0):  (25.051, 23.319, 23.752),
    ("M30",   3.5):  (27.727, 25.706, 26.211),
    ("M33",   3.5):  (30.727, 28.706, 29.211),
    ("M36",   4.0):  (33.402, 31.093, 31.670),
    ("M39",   4.0):  (36.402, 34.093, 34.670),
    ("M42",   4.5):  (39.077, 36.479, 37.129),
    ("M45",   4.5):  (42.077, 39.479, 40.129),
    ("M48",   5.0):  (44.752, 41.866, 42.587),
    ("M52",   5.0):  (48.752, 45.866, 46.587),
    ("M56",   5.5):  (52.428, 49.252, 50.046),
    ("M60",   5.5):  (56.428, 53.252, 54.046),
    ("M64",   6.0):  (60.103, 56.639, 57.505),
    ("M68",   6.0):  (64.103, 60.639, 61.505),
}

# メートルねじ細目 (MF) — JIS B 0205-4 / ISO 724
# value: (d2, d1, D1)  — 同上公式で算出
METRIC_FINE_THREAD = {
    ("M8x1",    1.0):  (7.350,  6.773, 6.917),
    ("M10x1",   1.0):  (9.350,  8.773, 8.917),
    ("M10x1.25",1.25): (9.188,  8.466, 8.647),
    ("M12x1",   1.0):  (11.350, 10.773, 10.917),
    ("M12x1.25",1.25): (11.188, 10.466, 10.647),
    ("M12x1.5", 1.5):  (11.026, 10.160, 10.376),
    ("M14x1.5", 1.5):  (13.026, 12.160, 12.376),
    ("M16x1.5", 1.5):  (15.026, 14.160, 14.376),
    ("M18x1.5", 1.5):  (17.026, 16.160, 16.376),
    ("M20x1.5", 1.5):  (19.026, 18.160, 18.376),
    ("M22x1.5", 1.5):  (21.026, 20.160, 20.376),
    ("M24x2",   2.0):  (22.701, 21.546, 21.835),
    ("M27x2",   2.0):  (25.701, 24.546, 24.835),
    ("M30x2",   2.0):  (28.701, 27.546, 27.835),
    ("M33x2",   2.0):  (31.701, 30.546, 30.835),
    ("M36x3",   3.0):  (34.051, 32.319, 32.752),
    ("M39x3",   3.0):  (37.051, 35.319, 35.752),
}

# ユニファイねじ (UN) — ASME B1.1
# TPI = threads per inch, P = 25.4/TPI
UNIFIED_THREAD = {
    ("#0-80 UNF",   0.3175): (0.0519*25.4, 0.0438*25.4),
    ("#1-64 UNC",   0.3969): (0.0629*25.4, 0.0538*25.4),
    ("#1-72 UNF",   0.3528): (0.0640*25.4, 0.0561*25.4),
    ("#2-56 UNC",   0.4536): (0.0744*25.4, 0.0641*25.4),
    ("#2-64 UNF",   0.3969): (0.0759*25.4, 0.0668*25.4),
    ("#3-48 UNC",   0.5292): (0.0855*25.4, 0.0734*25.4),
    ("#4-40 UNC",   0.6350): (0.0958*25.4, 0.0813*25.4),
    ("#4-48 UNF",   0.5292): (0.0985*25.4, 0.0864*25.4),
    ("#5-40 UNC",   0.6350): (0.1088*25.4, 0.0943*25.4),
    ("#6-32 UNC",   0.7938): (0.1177*25.4, 0.0997*25.4),
    ("#8-32 UNC",   0.7938): (0.1437*25.4, 0.1257*25.4),
    ("#10-24 UNC",  1.0583): (0.1629*25.4, 0.1389*25.4),
    ("#10-32 UNF",  0.7938): (0.1697*25.4, 0.1517*25.4),
    ("1/4-20 UNC",  1.2700): (0.2175*25.4, 0.1850*25.4),
    ("1/4-28 UNF",  0.9071): (0.2268*25.4, 0.2005*25.4),
    ("5/16-18 UNC", 1.4111): (0.2764*25.4, 0.2403*25.4),
    ("5/16-24 UNF", 1.0583): (0.2854*25.4, 0.2584*25.4),
    ("3/8-16 UNC",  1.5875): (0.3344*25.4, 0.2938*25.4),
    ("3/8-24 UNF",  1.0583): (0.3479*25.4, 0.3209*25.4),
    ("7/16-14 UNC", 1.8143): (0.3911*25.4, 0.3447*25.4),
    ("7/16-20 UNF", 1.2700): (0.4050*25.4, 0.3726*25.4),
    ("1/2-13 UNC",  1.9538): (0.4500*25.4, 0.4001*25.4),
    ("1/2-20 UNF",  1.2700): (0.4675*25.4, 0.4351*25.4),
    ("9/16-12 UNC", 2.1167): (0.5084*25.4, 0.4542*25.4),
    ("5/8-11 UNC",  2.3091): (0.5660*25.4, 0.5069*25.4),
    ("3/4-10 UNC",  2.5400): (0.6850*25.4, 0.6201*25.4),
    ("3/4-16 UNF",  1.5875): (0.7094*25.4, 0.6688*25.4),
    ("7/8-9 UNC",   2.8222): (0.8028*25.4, 0.7307*25.4),
    ("1-8 UNC",     3.1750): (0.9188*25.4, 0.8376*25.4),
    ("1-14 UNF",    1.8143): (0.9459*25.4, 0.9069*25.4),
    ("1.1/4-7 UNC", 3.6286): (1.1572*25.4, 1.0747*25.4),
    ("1.1/2-6 UNC", 4.2333): (1.3917*25.4, 1.2938*25.4),
}

# 管用平行ねじ (G / PF) — ISO 228-1 / JIS B 0202
# key: 呼び, P(mm), d2(mm), d1(mm), d(mm)
BSP_PARALLEL = {
    ("G1/16",  0.907): (7.142,  6.561,  7.723),
    ("G1/8",   0.907): (9.147,  8.566,  9.728),
    ("G1/4",   1.337): (12.301, 11.445, 13.157),
    ("G3/8",   1.337): (15.806, 14.950, 16.662),
    ("G1/2",   1.814): (19.793, 18.631, 20.955),
    ("G5/8",   1.814): (22.297, 21.135, 23.459),  # 追加
    ("G3/4",   1.814): (25.279, 24.117, 26.441),
    ("G7/8",   1.814): (28.783, 27.621, 29.945),  # 追加
    ("G1",     2.309): (31.770, 30.291, 33.249),
    ("G1.1/4", 2.309): (40.431, 38.953, 41.910),
    ("G1.1/2", 2.309): (46.324, 44.846, 47.803),
    ("G2",     2.309): (58.135, 56.657, 59.614),
    ("G2.1/2", 2.309): (73.705, 72.227, 75.184),
    ("G3",     2.309): (86.405, 84.927, 87.884),
    ("G4",     2.309): (111.551,110.073,113.030),
    ("G5",     2.309): (136.951,135.473,138.430),
    ("G6",     2.309): (162.351,160.873,163.830),
}

# 管用テーパーねじ (R/Rc/Rp) — ISO 7-1 / JIS B 0203
# テーパー1/16 (1:32 半角)
BSP_TAPER = {
    ("R1/16",  0.907): (7.142,  6.561,  7.723),
    ("R1/8",   0.907): (9.147,  8.566,  9.728),
    ("R1/4",   1.337): (12.301, 11.445, 13.157),
    ("R3/8",   1.337): (15.806, 14.950, 16.662),
    ("R1/2",   1.814): (19.793, 18.631, 20.955),
    ("R3/4",   1.814): (25.279, 24.117, 26.441),
    ("R1",     2.309): (31.770, 30.291, 33.249),
    ("R1.1/4", 2.309): (40.431, 38.953, 41.910),
    ("R1.1/2", 2.309): (46.324, 44.846, 47.803),
    ("R2",     2.309): (58.135, 56.657, 59.614),
    ("R2.1/2", 2.309): (73.705, 72.227, 75.184),
    ("R3",     2.309): (86.405, 84.927, 87.884),
}

# アメリカ管用テーパーねじ (NPT) — ASME B1.20.1
NPT_THREAD = {
    ('NPT1/16"',  0.941): (6.389,  5.786,  6.832),
    ('NPT1/8"',   0.941): (8.725,  8.122,  9.168),
    ('NPT1/4"',   1.411): (11.431, 10.452, 13.157),
    ('NPT3/8"',   1.411): (14.869, 13.890, 16.662),
    ('NPT1/2"',   1.814): (18.321, 17.159, 20.955),
    ('NPT3/4"',   1.814): (23.786, 22.624, 26.441),
    ('NPT1"',     2.209): (29.694, 28.118, 33.249),
    ('NPT1.1/4"', 2.209): (38.952, 37.376, 41.910),
    ('NPT1.1/2"', 2.209): (44.845, 43.269, 47.803),
    ('NPT2"',     2.209): (56.656, 55.080, 59.614),
    ('NPT2.1/2"', 3.175): (72.699, 70.613, 75.184),
    ('NPT3"',     3.175): (86.068, 83.982, 87.884),
    ('NPT4"',     3.175): (111.433,109.347,113.030),
}

# ウィットねじ (W / BSW) — BS 84
WHITWORTH_THREAD = {
    ('W1/16"',  0.635): (1.372,  1.143,  1.588),
    ('W3/32"',  0.794): (2.158,  1.854,  2.381),
    ('W1/8"',   0.794): (2.779,  2.475,  3.175),
    ('W5/32"',  0.794): (3.401,  3.097,  3.969),
    ('W3/16"',  1.058): (4.166,  3.734,  4.762),
    ('W1/4"',   1.270): (5.728,  5.182,  6.350),
    ('W5/16"',  1.411): (7.239,  6.576,  7.938),
    ('W3/8"',   1.588): (8.763,  7.998,  9.525),
    ('W7/16"',  1.814): (10.230, 9.340,  11.113),
    ('W1/2"',   2.117): (11.811, 10.724, 12.700),
    ('W9/16"',  2.117): (13.386, 12.299, 14.288),
    ('W5/8"',   2.309): (14.952, 13.735, 15.875),
    ('W3/4"',   2.540): (18.047, 16.661, 19.050),
    ('W7/8"',   2.822): (21.162, 19.589, 22.225),
    ('W1"',     3.175): (24.181, 22.390, 25.400),
    ('W1.1/8"', 3.629): (27.300, 25.257, 28.575),
    ('W1.1/4"', 3.629): (30.488, 28.445, 31.750),
    ('W1.3/8"', 4.233): (33.607, 31.134, 34.925),
    ('W1.1/2"', 4.233): (36.795, 34.322, 38.100),
    ('W1.5/8"', 4.233): (39.832, 37.359, 41.275),
    ('W1.3/4"', 5.080): (43.031, 40.000, 44.450),
    ('W2"',     5.644): (49.296, 45.925, 50.800),
    ('W2.1/4"', 5.644): (55.715, 52.344, 57.150),
    ('W2.1/2"', 5.644): (62.135, 58.764, 63.500),
    ('W2.3/4"', 5.644): (68.554, 65.183, 69.850),
    ('W3"',     6.350): (74.939, 71.121, 76.200),
}

# ねじ種類ごとのデータベースマッピング
THREAD_DB = {
    "メートルねじ (M)":           METRIC_THREAD,
    "メートル細目ねじ (MF)":       METRIC_FINE_THREAD,
    "ユニファイねじ (UN)":         UNIFIED_THREAD,
    "管用平行ねじ (G)":            BSP_PARALLEL,
    "管用テーパーねじ (R/Rc)":     BSP_TAPER,
    "アメリカ管用テーパーねじ (NPT)": NPT_THREAD,
    "ウィットねじ (W/BSW)":        WHITWORTH_THREAD,
}

# テーパーねじかどうかのフラグ
TAPER_TYPES = {"管用テーパーねじ (R/Rc)", "アメリカ管用テーパーねじ (NPT)"}

# ============================================================
# 有効径公差テーブル（ISO 965-1 / JIS B 0209-1）
# pitch (mm): (es, Td2, TD2)  単位 mm
#   es  : 外ねじ 6g 基本寸法からの上の寸法差（負値）
#   Td2 : 外ねじ 6g 有効径公差
#   TD2 : 内ねじ 6H 有効径公差（下の寸法差 EI=0）
# ============================================================
_PD_TOL_6HG = {
    0.20: (-0.017, 0.032, 0.045),
    0.25: (-0.017, 0.036, 0.050),
    0.30: (-0.017, 0.038, 0.053),
    0.35: (-0.017, 0.040, 0.056),
    0.40: (-0.017, 0.042, 0.060),
    0.45: (-0.017, 0.048, 0.067),
    0.50: (-0.020, 0.048, 0.071),
    0.60: (-0.020, 0.053, 0.080),
    0.70: (-0.020, 0.056, 0.085),
    0.75: (-0.020, 0.063, 0.095),
    0.80: (-0.020, 0.060, 0.090),
    0.90: (-0.020, 0.063, 0.095),
    1.00: (-0.026, 0.071, 0.106),
    1.25: (-0.026, 0.080, 0.118),
    1.50: (-0.032, 0.085, 0.125),
    1.75: (-0.032, 0.090, 0.132),
    2.00: (-0.032, 0.095, 0.140),
    2.50: (-0.032, 0.106, 0.160),
    3.00: (-0.038, 0.118, 0.170),
    3.50: (-0.038, 0.125, 0.180),
    4.00: (-0.038, 0.132, 0.190),
    4.50: (-0.038, 0.140, 0.200),
    5.00: (-0.038, 0.150, 0.212),
    5.50: (-0.038, 0.160, 0.224),
    6.00: (-0.038, 0.170, 0.236),
}


# 外ねじ 山径公差 (6g, Td) — JIS B0209-2 表2 の d_max-d_min 実測値（ピッチのみ依存）
# P=0.20/0.75/0.90 は表なしのため ISO 965-1 近似値を使用
_MAJOR_TOL_6G = {
    0.20: 0.062, 0.25: 0.067, 0.30: 0.075, 0.35: 0.085,
    0.40: 0.095, 0.45: 0.100, 0.50: 0.106, 0.60: 0.125,
    0.70: 0.140, 0.75: 0.149, 0.80: 0.150, 0.90: 0.168,
    1.00: 0.180, 1.25: 0.212, 1.50: 0.236, 1.75: 0.265,
    2.00: 0.280, 2.50: 0.335, 3.00: 0.375, 3.50: 0.425,
    4.00: 0.475, 4.50: 0.500, 5.00: 0.530, 5.50: 0.560, 6.00: 0.600,
}

# 内ねじ 谷径公差 (6H, TD1) — pitch: TD1 (mm)  ISO 965-1 Table 6
_MINOR_TOL_6H = {
    # JIS B0209-2 表1/3 の D1_max-D1_min を 1/2 した値（D1_mid = D1_basic + この値）
    0.20: 0.036, 0.25: 0.028, 0.30: 0.034, 0.35: 0.050,
    0.40: 0.056, 0.45: 0.063, 0.50: 0.071, 0.60: 0.080,
    0.70: 0.090, 0.75: 0.095, 0.80: 0.100, 0.90: 0.106,
    1.00: 0.118, 1.25: 0.132, 1.50: 0.150, 1.75: 0.168,
    2.00: 0.188, 2.50: 0.225, 3.00: 0.250, 3.50: 0.280,
    4.00: 0.300, 4.50: 0.335, 5.00: 0.355, 5.50: 0.375, 6.00: 0.400,
}


# JIS B0209-2 直接参照テーブル — (スレッド名, ピッチ) → (d2_avg_6g, d_avg_6g)
# 雄ねじ 6g 公差域中間値 = (d2_max+d2_min)/2, (d_max+d_min)/2
_METRIC_EXT_AVG_6G: dict = {
    # ── メートル並目 (JIS B0209-2 表2) ──
    ("M1",   0.25): (0.8115, 0.9665), ("M1.2", 0.25): (1.0115, 1.1665),
    ("M1.4", 0.30): (1.177,  1.3625), ("M1.6", 0.35): (1.3225, 1.5385),
    ("M2",   0.40): (1.6875, 1.9335), ("M2.5", 0.45): (2.1525, 2.430),
    ("M3",   0.50): (2.6175, 2.927),  ("M3.5", 0.60): (3.0465, 3.4165),
    ("M4",   0.70): (3.478,  3.908),  ("M5",   0.80): (4.4085, 4.901),
    ("M6",   1.00): (5.268,  5.884),  ("M7",   1.00): (6.268,  6.884),
    ("M8",   1.25): (7.101,  7.866),  ("M10",  1.50): (8.928,  9.850),
    ("M12",  1.75): (10.754, 11.8335),("M14",  2.00): (12.583, 13.822),
    ("M16",  2.00): (14.583, 15.822), ("M18",  2.50): (16.249, 17.7905),
    ("M20",  2.50): (18.249, 19.7905),("M22",  2.50): (20.249, 21.7905),
    ("M24",  3.00): (21.903, 23.7645),("M27",  3.00): (24.903, 26.7645),
    ("M30",  3.50): (27.568, 29.7345),("M33",  3.50): (30.568, 32.7345),
    ("M36",  4.00): (33.230, 35.7025),("M39",  4.00): (36.230, 38.7025),
    ("M42",  4.50): (38.896, 41.687), ("M45",  4.50): (41.896, 44.687),
    ("M48",  5.00): (44.556, 47.664), ("M52",  5.00): (48.556, 51.664),
    ("M56",  5.50): (52.2205,55.645), ("M60",  5.50): (56.2205,59.645),
    ("M64",  6.00): (59.883, 63.620),
    # ── メートル細目 (JIS B0209-2 表4) ──
    ("M8x1",    1.00): (7.268,  7.884),  ("M10x1",   1.00): (9.268,  9.884),
    ("M10x1.25",1.25): (9.101,  9.866),  ("M12x1",   1.00): (11.268, 11.884),
    ("M12x1.25",1.25): (11.094, 11.866), ("M12x1.5", 1.50): (10.924, 11.850),
    ("M14x1.5", 1.50): (12.924, 13.850), ("M16x1.5", 1.50): (14.924, 15.850),
    ("M18x1.5", 1.50): (16.924, 17.850), ("M20x1.5", 1.50): (18.924, 19.850),
    ("M22x1.5", 1.50): (20.924, 21.850), ("M24x2",   2.00): (22.578, 23.822),
    ("M27x2",   2.00): (25.578, 26.822), ("M30x2",   2.00): (28.578, 29.822),
    ("M33x2",   2.00): (31.578, 32.822), ("M36x3",   3.00): (33.903, 35.7645),
    ("M39x3",   3.00): (36.903, 38.7645),
}

# JIS B0209-2 直接参照テーブル — (スレッド名, ピッチ) → (D2_avg_6H, D1_avg_6H)
# 雌ねじ 6H 公差域中間値 = (D2_max+D2_min)/2, (D1_max+D1_min)/2
_METRIC_INT_AVG_6H: dict = {
    # ── メートル並目 (JIS B0209-2 表1) ──
    ("M1",   0.25): (0.866,   0.757),  ("M1.2", 0.25): (1.066,   0.957),
    ("M1.4", 0.30): (1.235,   1.1085), ("M1.6", 0.35): (1.4155,  1.271),
    ("M2",   0.40): (1.785,   1.623),  ("M2.5", 0.45): (2.2555,  2.0755),
    ("M3",   0.50): (2.725,   2.529),  ("M3.5", 0.60): (3.166,   2.930),
    ("M4",   0.70): (3.604,   3.332),  ("M5",   0.80): (4.5425,  4.234),
    ("M6",   1.00): (5.425,   5.035),  ("M7",   1.00): (6.425,   6.035),
    ("M8",   1.25): (7.268,   6.7795), ("M10",  1.50): (9.116,   8.526),
    ("M12",  1.75): (10.963,  10.2735),("M14",  2.00): (12.807,  12.0225),
    ("M16",  2.00): (14.807,  14.0225),("M18",  2.50): (16.488,  15.519),
    ("M20",  2.50): (18.488,  17.519), ("M22",  2.50): (20.488,  19.519),
    ("M24",  3.00): (22.1835, 21.002), ("M27",  3.00): (25.1785, 24.002),
    ("M30",  3.50): (27.867,  26.491), ("M33",  3.50): (30.867,  29.491),
    ("M36",  4.00): (33.552,  31.970), ("M39",  4.00): (36.552,  34.970),
    ("M42",  4.50): (39.2345, 37.464), ("M45",  4.50): (42.2345, 40.464),
    ("M48",  5.00): (44.9195, 42.942), ("M52",  5.00): (48.9195, 46.942),
    ("M56",  5.50): (52.6055, 50.421), ("M60",  5.50): (56.6055, 54.421),
    ("M64",  6.00): (60.2905, 57.905),
    # ── メートル細目 (JIS B0209-2 表3) ──
    ("M8x1",    1.00): (7.425,  7.035),  ("M10x1",   1.00): (9.425,  9.035),
    ("M10x1.25",1.25): (9.268,  8.7795), ("M12x1",   1.00): (11.425, 11.035),
    ("M12x1.25",1.25): (11.278, 10.7795),("M12x1.5", 1.50): (11.121, 10.526),
    ("M14x1.5", 1.50): (13.121, 12.526), ("M16x1.5", 1.50): (15.121, 14.526),
    ("M18x1.5", 1.50): (17.121, 16.526), ("M20x1.5", 1.50): (19.121, 18.526),
    ("M22x1.5", 1.50): (21.121, 20.526), ("M24x2",   2.00): (22.813, 22.0225),
    ("M27x2",   2.00): (25.813, 25.0225),("M30x2",   2.00): (28.813, 28.0225),
    ("M33x2",   2.00): (31.813, 31.0225),("M36x3",   3.00): (34.1835,33.002),
    ("M39x3",   3.00): (37.1835,36.002),
}


def _d_major_avg(d_basic: float, pitch: float, thread_name: str = None) -> float:
    """外ねじ 山径（外径）の公差域中間値 (6g)。"""
    if thread_name is not None:
        entry = _METRIC_EXT_AVG_6G.get((thread_name, pitch))
        if entry is not None:
            return entry[1]
    p  = min(_PD_TOL_6HG.keys(),   key=lambda x: abs(x - pitch))
    p2 = min(_MAJOR_TOL_6G.keys(), key=lambda x: abs(x - pitch))
    es = _PD_TOL_6HG[p][0]
    Td = _MAJOR_TOL_6G[p2]
    d_max = d_basic + es
    d_min = d_max - Td
    return round((d_max + d_min) / 2, 4)


def _D1_minor_avg(D1_basic: float, pitch: float, thread_name: str = None) -> float:
    """内ねじ 谷径ボーリング目標径（D1 公差域中間値, 6H）。"""
    if thread_name is not None:
        entry = _METRIC_INT_AVG_6H.get((thread_name, pitch))
        if entry is not None:
            return entry[1]
    p   = min(_MINOR_TOL_6H.keys(), key=lambda x: abs(x - pitch))
    TD1 = _MINOR_TOL_6H[p]
    return round(D1_basic + TD1, 4)


def _d_nominal_from_key(size_name: str, val: tuple):
    """データベース行から公称外径（山径）を返す。取得できない場合は None。

    メートルねじ (M): 名前から解析（val[2]=D1 なので名前優先）
    その他 (G/R/NPT/W): val=(d2,d1,d) の第3要素を使用
    """
    if size_name.startswith("M"):
        try:
            return float(size_name.lstrip("M").split("x")[0].strip())
        except ValueError:
            pass
    if len(val) >= 3:
        return val[2]   # BSP/NPT/Whitworth: val[2]=d（山径）
    return None


def _td2_6g(d: float, p: float) -> float:
    """外ねじ有効径公差 Td2 (6g) — JIS B 0209-2: 50×d^(1/3)×P^(1/2) μm"""
    return round(50 * d ** (1 / 3) * p ** 0.5) / 1000

def _TD2_6H(d: float, p: float) -> float:
    """内ねじ有効径公差 TD2 (6H) — JIS B 0209-2: 63×d^(1/3)×P^(1/2) μm"""
    return round(63 * d ** (1 / 3) * p ** 0.5) / 1000

def _d2_avg(d2_basic: float, pitch: float, is_external: bool,
            d_nominal: float = None, thread_name: str = None) -> float:
    """有効径の公差域中間値を返す（外ねじ 6g / 内ねじ 6H）。"""
    if thread_name is not None:
        if is_external:
            entry = _METRIC_EXT_AVG_6G.get((thread_name, pitch))
            if entry is not None:
                return entry[0]
        else:
            entry = _METRIC_INT_AVG_6H.get((thread_name, pitch))
            if entry is not None:
                return entry[0]
    p = min(_PD_TOL_6HG.keys(), key=lambda x: abs(x - pitch))
    es = _PD_TOL_6HG[p][0]
    if d_nominal is not None:
        Td2 = _td2_6g(d_nominal, pitch) if is_external else _TD2_6H(d_nominal, pitch)
    else:
        Td2 = _PD_TOL_6HG[p][1] if is_external else _PD_TOL_6HG[p][2]
    if is_external:
        d2_max = d2_basic + es
        d2_min = d2_max - Td2
    else:
        d2_max = d2_basic + Td2
        d2_min = d2_basic
    return round((d2_max + d2_min) / 2, 4)


# ============================================================
# ねじ切り計算
# ============================================================

def calc_thread_depth(pitch: float, nose_r: float, thread_type: str,
                      is_external: bool, d2_basic: float = None,
                      d_nominal: float = None, thread_name: str = None) -> dict:
    """
    ねじ切りX目標径と切り込み深さを計算する。

    雄ねじ X目標径:
        ((d2_avg/2) - (P/4)/tan(θ/2) + (nose_r/sin(θ/2)) - nose_r) * 2
    雌ねじ X目標径:
        ((d2_avg/2) + (P/4)/tan(θ/2) - (nose_r/sin(θ/2)) + nose_r) * 2

    d_nominal が与えられた場合のみ上式を使用。未指定時はピッチ基準のフォールバック。
    """
    is_55deg = ("テーパー" in thread_type or "NPT" in thread_type or
                "管用平行" in thread_type or "ウィット" in thread_type)
    theta_half = 27.5 if is_55deg else 30.0
    angle_deg  = 55   if is_55deg else 60

    tan_th = math.tan(math.radians(theta_half))
    sin_th = math.sin(math.radians(theta_half))

    d2_ext_avg = _d2_avg(d2_basic, pitch, True,  d_nominal, thread_name) if d2_basic is not None else None
    d2_int_avg = _d2_avg(d2_basic, pitch, False, d_nominal, thread_name) if d2_basic is not None else None
    d2_avg = (d2_ext_avg if is_external else d2_int_avg)

    if d2_avg is not None and d_nominal is not None:
        # ユーザー指定式で X目標径（直径値）を算出
        if is_external:
            x_target = ((d2_avg / 2) - (pitch / 4) / tan_th
                        + (nose_r / sin_th) - nose_r) * 2
            actual_depth = (d_nominal - x_target) / 2
        else:
            x_target = ((d2_avg / 2) + (pitch / 4) / tan_th
                        - (nose_r / sin_th) + nose_r) * 2
            actual_depth = (x_target - d_nominal) / 2
        x_target = round(x_target, 4)
        h_theory  = round(pitch / (2 * tan_th), 4)   # 有効径→谷径 片側
        nose_corr = round(nose_r / sin_th - nose_r, 4)
    else:
        # フォールバック（d2_basic / d_nominal 未入力時）
        h_theory  = round((0.9605 if is_55deg else 0.8660) * pitch, 4)
        nose_corr = round(nose_r * (1 - sin_th), 4)
        actual_depth = h_theory - nose_r * (1 - sin_th)
        if not is_external:
            actual_depth *= 1.08
        x_target = None

    actual_depth = round(abs(actual_depth), 4)

    # 等断面積法による漸減切り込みリスト
    first_cut = min(0.3 * pitch, actual_depth * 0.4)
    min_cut   = max(0.05, pitch * 0.02)

    cuts = []
    remaining = actual_depth
    cut_num = 1
    while remaining > 0.001:
        if cut_num == 1:
            c = first_cut
        else:
            c = (math.sqrt(cut_num) - math.sqrt(cut_num - 1)) * first_cut
            c = max(c, min_cut)
        c = min(c, remaining)
        cuts.append(round(c, 4))
        remaining -= c
        if remaining <= min_cut:
            cuts[-1] = round(cuts[-1] + remaining, 4)
            remaining = 0
        cut_num += 1

    return {
        "total_depth": actual_depth,
        "x_target":    x_target,
        "h_theory":    h_theory,
        "nose_correction": nose_corr,
        "cuts":        cuts,
        "angle_deg":   angle_deg,
        "d2_basic":    round(d2_basic, 4) if d2_basic is not None else None,
        "d2_ext_avg":  d2_ext_avg,
        "d2_int_avg":  d2_int_avg,
    }


_OKUMA_U        = 0.1  # 仕上代（直径値 mm）— G71 U パラメータ = この値
_MATERIAL_STOCK = 0.1  # 素材仕上代（直径値 mm）— ねじ切り前の外径/内径余裕

def _okuma_cuts(adj_depth: float, pitch: float) -> list:
    """
    Okuma G71 実機パスシーケンス（半径値）。実機検証に基づくアルゴリズム:
      1. 定量 D パス（cumul < H_rough - 2D の間）
      2. 遷移パス（H_rough - D の位置まで端数1パス）
      3. テーパー：D/2, D/4, D/8, D/8（合計 D）
      4. 仕上：U
    H_rough - D → H_rough - D + D = H_rough（テーパーで丁度到達）
    """
    U = _OKUMA_U / 2                        # 半径値
    H_rough = round(adj_depth - U, 6)
    if H_rough <= 1e-9:
        return [round(adj_depth, 4)]

    D_dia = round(min(0.3 * pitch, H_rough * 2 * 0.4), 4)
    D_dia = max(D_dia, 0.02)
    D = D_dia / 2                           # 半径値

    cuts = []
    cumul = 0.0

    # 定量 D パス
    threshold = H_rough - 2 * D
    while cumul < threshold - 1e-9:
        cuts.append(round(D, 4))
        cumul = round(cumul + D, 4)

    # 遷移パス（H_rough - D の位置まで）
    transition = round(H_rough - D - cumul, 4)
    if transition > 1e-9:
        cuts.append(transition)
        cumul = round(cumul + transition, 4)

    # テーパー：D/2, D/4, D/8, D/8
    for frac in (0.5, 0.25, 0.125, 0.125):
        cuts.append(round(D * frac, 4))
        cumul = round(cumul + D * frac, 4)

    # 仕上パス（丸め誤差吸収）
    finish = round(adj_depth - cumul, 4)
    if finish > 1e-9:
        cuts.append(finish)

    return cuts


def generate_okuma(params: dict) -> str:
    """オークマ OSP 形式 G71 長手ねじ切り複合サイクルプログラムを生成する。

    G71 フォーマット（OSP LB3000EX2）:
        G71 X(xe) Z(ze) [I(taper)] B(ang) D(d1) U(fin) H(depth) F(p) M(mode)
          X   : ねじ谷径（直径値 mm） ※雌ねじは山径
          Z   : 切り終わりZ座標
          I   : テーパー量（半径差 mm、テーパーねじのみ）
          B   : 切り込み角度（60.000° or 55.000°）
          D   : 初回切り込み量（直径値 mm）
          U   : 仕上代（直径値 mm）
          H   : ねじ外径と谷径の差（直径値 mm）
          F   : ピッチ（リード mm）
          M   : 切削モード（M32/M33/M34）
    """
    t = params
    depth_info = t["depth_info"]
    pitch      = t["pitch"]
    z_start    = t["z_start"]
    z_end      = t["z_end"]
    is_external = t["is_external"]
    is_taper   = t["is_taper"]
    d_nominal  = t["d_nominal"]
    total_depth = depth_info["total_depth"]
    cuts       = depth_info["cuts"]
    angle      = depth_info["angle_deg"]
    cut_mode   = t.get("cut_mode", "M33")

    # X アプローチ・ねじ谷径（直径値）
    # x_target が計算済みであればそれを使用、なければ total_depth から算出
    x_target = depth_info.get("x_target")
    if is_external:
        x_approach = round(d_nominal + 2.0, 3)
        x_root = round(x_target, 3) if x_target is not None else round(d_nominal - total_depth * 2, 3)
    else:
        x_approach = round(d_nominal - 2.0, 3)
        x_root = round(x_target, 3) if x_target is not None else round(d_nominal + total_depth * 2, 3)

    # G71 パラメータ（直径値）
    adj_depth = depth_info.get("adj_total_depth", total_depth)
    d1_dia = round(cuts[0] * 2, 4)          # 初回切り込み（直径値）
    u_dia  = _OKUMA_U                       # 仕上代（直径値）
    h_dia  = round(adj_depth * 2, 4)        # 素材仕上代込みの全切込み（直径値）

    # テーパー量 I：ねじ長さ ÷ 32（1/16テーパーの半径差）
    taper_i = round(abs(z_end - z_start) / 32.0, 3) if is_taper else None

    # アプローチZ（助走＝ピッチ×3）
    z_approach = round(z_start + pitch * 3, 3)

    lines = [
        f"( *** NC Thread Cutting Program ***)",
        f"( Thread : {t['thread_name']} )",
        f"( Type   : {'EXTERNAL THREAD' if is_external else 'INTERNAL THREAD'} )",
        f"( Pitch  : {pitch:.4f} mm )",
        f"( Depth  : {total_depth:.4f} mm  [{len(cuts)} passes] )",
        f"( Nose R : {t['nose_r']} mm )",
        f"( Cycle  : G71 COMBINED THREAD CUTTING CYCLE / {cut_mode} )",
        "",
        "N10 G00 X500.0 Z500.0",
        "N20 G50 S2000",
        "N30 G97 S500 M03",
        "N40 G00 T0101",
        f"N50 G00 X{x_approach:.3f} Z{z_approach:.3f}",
        "",
        "( G71 COMBINED THREAD CUTTING CYCLE )",
    ]

    if is_taper:
        lines.append(
            f"N60 G71 X{x_root:.3f} Z{z_end:.3f} I{taper_i:.3f} "
            f"B{angle:.3f} D{d1_dia:.3f} U{u_dia:.3f} H{h_dia:.3f} F{pitch:.3f} {cut_mode}"
        )
    else:
        lines.append(
            f"N60 G71 X{x_root:.3f} Z{z_end:.3f} "
            f"B{angle:.3f} D{d1_dia:.3f} U{u_dia:.3f} H{h_dia:.3f} F{pitch:.3f} {cut_mode}"
        )

    g33_line = (
        f"N80 G33 X{x_root:.3f} Z{z_end:.3f} I{taper_i:.3f} F{pitch:.3f}"
        if is_taper else
        f"N80 G33 X{x_root:.3f} Z{z_end:.3f} F{pitch:.3f}"
    )
    lines += [
        "( AIRCUTTING )",
        f"N70 G00 X{x_approach:.3f} Z{z_approach:.3f}",
        g33_line,
        f"N90 G00 X{x_approach:.3f}",
        "",
        "N100 G00 X500.0 Z500.0",
        "N110 M05",
        "N120 M30",
        "%",
    ]
    return "\n".join(lines)


def generate_fanuc(params: dict) -> str:
    """ファナック G76 複合サイクル形式のねじ切りプログラムを生成する。"""
    t = params
    depth_info = t["depth_info"]
    pitch = t["pitch"]
    z_start = t["z_start"]
    z_end = t["z_end"]
    is_external = t["is_external"]
    is_taper = t["is_taper"]

    d_nominal = t["d_nominal"]
    total_depth = depth_info["total_depth"]
    cuts = depth_info["cuts"]

    # G76 パラメータ
    # m=2(仕上げ回数), r=11(面取り), a=60or55(角度)
    angle = depth_info["angle_deg"]
    adj_depth    = depth_info.get("adj_total_depth", total_depth)
    first_cut_um = int(cuts[0] * 1000)   # μm 単位
    min_cut_um   = max(50, int(min(cuts) * 1000))
    depth_um     = int(adj_depth * 1000)  # 素材仕上代込みの全切込み（μm）

    x_target = depth_info.get("x_target")
    if is_external:
        x_end_dia  = round(x_target, 3) if x_target is not None else round(d_nominal - total_depth * 2, 3)
        x_approach = round(d_nominal + 2.0, 3)
    else:
        x_end_dia  = round(x_target, 3) if x_target is not None else round(d_nominal + total_depth * 2, 3)
        x_approach = round(d_nominal - 2.0, 3)

    taper_i = 0.0
    if is_taper:
        # I = テーパー端と基準端の半径差 (mm)
        thread_len = abs(z_end - z_start)
        taper_i = round(thread_len / 32.0, 3)
        if not is_external:
            taper_i = -taper_i

    lines = [
        f"( *** NC Thread Cutting Program ***)",
        f"( Thread : {t['thread_name']} )",
        f"( Type   : {'EXTERNAL THREAD' if is_external else 'INTERNAL THREAD'} )",
        f"( Pitch  : {pitch:.4f} mm )",
        f"( Depth  : {total_depth:.4f} mm  [{len(cuts) + 2} passes] )",
        f"( Nose R : {t['nose_r']} mm )",
        "",
        "O0001",
        "N10 G28 U0 W0",
        "N20 G50 S2000",
        "N30 G97 S500 M03",
        "N40 G00 T0101",
        f"N50 G00 X{x_approach:.3f} Z{z_start + pitch * 3:.3f}",
        "",
        f"( G76 COMBINED THREAD CUTTING CYCLE )",
        f"N60 G76 P0{2}1{1}{angle:02d} Q{min_cut_um} R0.05",
    ]

    if is_taper:
        lines.append(
            f"N70 G76 X{x_end_dia:.3f} Z{z_end:.3f} R{taper_i:.3f} "
            f"P{depth_um} Q{first_cut_um} F{pitch:.4f}"
        )
    else:
        lines.append(
            f"N70 G76 X{x_end_dia:.3f} Z{z_end:.3f} "
            f"P{depth_um} Q{first_cut_um} F{pitch:.4f}"
        )

    z_approach = round(z_start + pitch * 3, 3)
    # フランク送りによる仕上パスの助走Z補正
    # G76各パスはX切込みに対してZ方向もシフトするため、
    # 仕上パスの助走Zをそのシフト量だけ切削方向にずらす
    z_shift = total_depth * math.tan(math.radians(angle / 2))
    direction = math.copysign(1, z_end - z_start)
    z_approach_finish = round(z_approach + direction * z_shift, 3)
    lines += [
        "",
        "( AIRCUTTING )",
        f"N80 G00 X{x_end_dia:.3f} Z{z_approach_finish:.3f}",
        f"N90 G32 X{x_end_dia:.3f} Z{z_end:.3f} F{pitch:.3f}",
        f"N100 G00 X{x_approach:.3f}",
        "",
        "N110 G28 U0 W0",
        "N120 M05",
        "N130 M30",
        "%",
    ]
    return "\n".join(lines)


# ============================================================
# GUI
# ============================================================

class ThreadCuttingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"NC旋盤 ねじ切りプログラム生成  v{_VERSION}")
        self.resizable(True, True)
        self.configure(bg="#2b2b2b")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel",      background="#2b2b2b", foreground="#e0e0e0", font=("Yu Gothic UI", 10))
        style.configure("TFrame",      background="#2b2b2b")
        style.configure("TLabelframe", background="#2b2b2b", foreground="#aaaaaa")
        style.configure("TLabelframe.Label", background="#2b2b2b", foreground="#aaaaaa", font=("Yu Gothic UI", 9))
        style.configure("TButton",     font=("Yu Gothic UI", 10, "bold"), padding=6)
        style.configure("TCombobox",   font=("Yu Gothic UI", 10))
        style.configure("TEntry",      font=("Yu Gothic UI", 10))
        style.map("TButton", background=[("active", "#4a7fc1")], foreground=[("active", "white")])

        self._build_ui()
        self._on_type_change()

    # ----------------------------------------------------------
    def _build_ui(self):
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 12))

        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        # ---- 1. ねじ種類 ----
        grp1 = ttk.LabelFrame(left, text="1. ねじ種類", padding=8)
        grp1.pack(fill="x", pady=(0, 8))

        self.thread_type_var = tk.StringVar()
        types = list(THREAD_DB.keys())
        self.cb_type = ttk.Combobox(grp1, textvariable=self.thread_type_var,
                                    values=types, state="readonly", width=30)
        self.cb_type.current(0)
        self.cb_type.pack()
        self.cb_type.bind("<<ComboboxSelected>>", lambda e: self._on_type_change())

        # ---- 2. 雄/雌 ----
        grp2 = ttk.LabelFrame(left, text="2. 雄ねじ・雌ねじ", padding=8)
        grp2.pack(fill="x", pady=(0, 8))

        self.gender_var = tk.StringVar(value="外")
        fr2 = ttk.Frame(grp2)
        fr2.pack()
        ttk.Radiobutton(fr2, text="雄ねじ (外ねじ)", variable=self.gender_var, value="外",
                        command=self._set_default_diameter).pack(anchor="w")
        ttk.Radiobutton(fr2, text="雌ねじ (内ねじ)", variable=self.gender_var, value="内",
                        command=self._set_default_diameter).pack(anchor="w")

        # ---- 3. NCコントロール ----
        grp3 = ttk.LabelFrame(left, text="3. NCコントロール", padding=8)
        grp3.pack(fill="x", pady=(0, 8))

        self.nc_var = tk.StringVar(value="ファナック")
        fr3 = ttk.Frame(grp3)
        fr3.pack(fill="x")
        ttk.Radiobutton(fr3, text="ファナック (G76)", variable=self.nc_var,
                        value="ファナック", command=self._on_nc_change).pack(anchor="w")
        ttk.Radiobutton(fr3, text="オークマ (G71)", variable=self.nc_var,
                        value="オークマ",  command=self._on_nc_change).pack(anchor="w")

        # 切削モード（オークマ選択時のみ表示）
        self.mode_frame = ttk.Frame(grp3)
        ttk.Label(self.mode_frame, text="切削モード:").pack(anchor="w")
        self.cut_mode_var = tk.StringVar(value="M33")
        modes = [
            ("M32  片刃切削モード",   "M32"),
            ("M33  千鳥切削モード",   "M33"),
            ("M34  逆片刃切削モード", "M34"),
        ]
        for label, val in modes:
            ttk.Radiobutton(self.mode_frame, text=label,
                            variable=self.cut_mode_var, value=val).pack(anchor="w")

        # ---- 4. サイズ・ピッチ ----
        grp4 = ttk.LabelFrame(left, text="4. ねじサイズ / ピッチ", padding=8)
        grp4.pack(fill="x", pady=(0, 8))

        ttk.Label(grp4, text="呼び径:").grid(row=0, column=0, sticky="w")
        self.size_var = tk.StringVar()
        self.cb_size = ttk.Combobox(grp4, textvariable=self.size_var,
                                    state="readonly", width=18)
        self.cb_size.grid(row=0, column=1, padx=4, pady=2)
        self.cb_size.bind("<<ComboboxSelected>>", lambda e: self._on_size_change())

        ttk.Label(grp4, text="ピッチ (mm):").grid(row=1, column=0, sticky="w")
        self.pitch_var = tk.StringVar()
        self.cb_pitch = ttk.Combobox(grp4, textvariable=self.pitch_var,
                                     state="readonly", width=18)
        self.cb_pitch.grid(row=1, column=1, padx=4, pady=2)
        self.cb_pitch.bind("<<ComboboxSelected>>", lambda e: self._set_default_diameter())

        ttk.Label(grp4, text="外径/内径 (mm):").grid(row=2, column=0, sticky="w")
        self.diam_var = tk.StringVar()
        self.ent_diam = ttk.Entry(grp4, textvariable=self.diam_var, width=10)
        self.ent_diam.grid(row=2, column=1, padx=4, pady=2, sticky="w")

        # ---- 5. Z座標 ----
        grp5 = ttk.LabelFrame(left, text="5. Z座標 (mm)", padding=8)
        grp5.pack(fill="x", pady=(0, 8))

        ttk.Label(grp5, text="切り始め Z:").grid(row=0, column=0, sticky="w")
        self.zs_var = tk.StringVar(value="0.0")
        ttk.Entry(grp5, textvariable=self.zs_var, width=10).grid(row=0, column=1, padx=4, pady=2)

        ttk.Label(grp5, text="切り終わり Z:").grid(row=1, column=0, sticky="w")
        self.ze_var = tk.StringVar(value="-30.0")
        ttk.Entry(grp5, textvariable=self.ze_var, width=10).grid(row=1, column=1, padx=4, pady=2)

        # ---- 6. ノーズR ----
        grp6 = ttk.LabelFrame(left, text="6. インサートチップ ノーズR (mm)", padding=8)
        grp6.pack(fill="x", pady=(0, 8))

        self.noser_var = tk.StringVar(value="0.1")
        cb_nr = ttk.Combobox(grp6, textvariable=self.noser_var,
                              values=["0.06","0.07","0.08","0.09","0.1","0.11",
                                      "0.12","0.15","0.19","0.22","0.25","0.32"],
                              width=8)
        cb_nr.pack(anchor="w")

        # ---- 7. パス数 ----
        grp7 = ttk.LabelFrame(left, text="7. パス数 (空白=自動)", padding=8)
        grp7.pack(fill="x", pady=(0, 8))

        self.passes_var = tk.StringVar(value="")
        fr7 = ttk.Frame(grp7)
        fr7.pack(fill="x")
        ttk.Entry(fr7, textvariable=self.passes_var, width=6).pack(side="left")
        self.passes_label = ttk.Label(fr7, text="", foreground="#888888")
        self.passes_label.pack(side="left", padx=(8, 0))

        # ---- 生成ボタン ----
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=(4, 0))
        ttk.Button(btn_frame, text="プログラム生成", command=self._generate).pack(fill="x")
        ttk.Button(btn_frame, text="クリア",         command=self._clear).pack(fill="x", pady=(4, 0))

        # ---- 右側：計算結果 + プログラム出力 ----
        info_frame = ttk.LabelFrame(right, text="計算情報", padding=6)
        info_frame.pack(fill="x", pady=(0, 8))
        self.info_text = tk.Text(info_frame, height=7, bg="#1e1e1e", fg="#98c379",
                                  font=("Consolas", 10), relief="flat", state="disabled")
        self.info_text.pack(fill="x")

        prog_frame = ttk.LabelFrame(right, text="生成プログラム", padding=6)
        prog_frame.pack(fill="both", expand=True)

        self.prog_text = scrolledtext.ScrolledText(
            prog_frame, bg="#1e1e1e", fg="#abb2bf",
            font=("Consolas", 10), relief="flat", wrap="none"
        )
        self.prog_text.pack(fill="both", expand=True)

        copy_btn = ttk.Button(right, text="クリップボードにコピー", command=self._copy)
        copy_btn.pack(fill="x", pady=(4, 0))

    # ----------------------------------------------------------
    def _on_nc_change(self):
        if self.nc_var.get() == "オークマ":
            self.mode_frame.pack(fill="x", pady=(6, 0))
        else:
            self.mode_frame.pack_forget()

    def _on_type_change(self):
        ttype = self.thread_type_var.get()
        db = THREAD_DB[ttype]
        keys = list(db.keys())

        # 呼び径リスト
        names = [k[0] for k in keys]
        self.cb_size["values"] = names
        if names:
            self.cb_size.current(0)
        self._on_size_change()

    def _on_size_change(self):
        ttype = self.thread_type_var.get()
        db = THREAD_DB[ttype]
        size_name = self.size_var.get()

        # そのサイズに対するピッチ候補
        pitches = [str(k[1]) for k in db.keys() if k[0] == size_name]
        self.cb_pitch["values"] = pitches
        if pitches:
            self.cb_pitch.current(0)

        # 外径を自動セット
        self._set_default_diameter()

    def _set_default_diameter(self):
        ttype     = self.thread_type_var.get()
        db        = THREAD_DB[ttype]
        size_name = self.size_var.get()
        is_ext    = (self.gender_var.get() == "外")

        try:
            cur_pitch = float(self.pitch_var.get())
        except ValueError:
            cur_pitch = None

        for key, val in db.items():
            if key[0] != size_name:
                continue
            if cur_pitch is not None and abs(key[1] - cur_pitch) > 1e-6:
                continue
            pitch = key[1]

            is_55deg = any(k in ttype for k in ("テーパー", "NPT", "管用平行", "ウィット"))

            if is_ext:
                # 雄ねじ: 山径（外径）公差域中間値
                d_basic = _d_nominal_from_key(size_name, val) or val[0]
                try:
                    self.diam_var.set(f"{_d_major_avg(d_basic, pitch, size_name):.3f}")
                except Exception:
                    self.diam_var.set(f"{d_basic:.3f}")
            else:
                # 雌ねじ: 谷径（内径）公差域中間値
                # メートルねじ: val[2]=D1（JIS B 0205-4 内ねじ小径 d-1.082532P）
                # 55°ねじ    : val[1]が内外共通基準谷径
                # ユニファイ等: D1 = d - 1.0825P で算出
                if is_55deg:
                    D1_basic = val[1]
                elif size_name.startswith("M") and len(val) >= 3:
                    D1_basic = val[2]   # JIS B 0205-4 内ねじ小径
                else:
                    d_nomi = _d_nominal_from_key(size_name, val)
                    D1_basic = (d_nomi - 1.0825 * pitch) if d_nomi is not None else val[1]
                try:
                    self.diam_var.set(f"{_D1_minor_avg(D1_basic, pitch, size_name):.3f}")
                except Exception:
                    self.diam_var.set(f"{D1_basic:.3f}")
            break

    # ----------------------------------------------------------
    def _generate(self):
        try:
            ttype    = self.thread_type_var.get()
            is_ext   = (self.gender_var.get() == "外")
            nc       = self.nc_var.get()
            size_nm  = self.size_var.get()
            pitch    = float(self.pitch_var.get())
            diam     = float(self.diam_var.get())
            z_start  = float(self.zs_var.get())
            z_end    = float(self.ze_var.get())
            nose_r   = float(self.noser_var.get())

            if z_start == z_end:
                messagebox.showerror("エラー", "Z切り始めとZ切り終わりが同じです。")
                return

            db = THREAD_DB[ttype]
            key = (size_nm, pitch)
            if key not in db:
                messagebox.showerror("エラー", f"サイズ/ピッチの組み合わせ ({size_nm}, {pitch}) が見つかりません。")
                return

            d2_basic = db[key][0]   # 全DBで先頭値が基準有効径
            depth_info = calc_thread_depth(pitch, nose_r, ttype, is_ext, d2_basic, diam, size_nm)

            # 素材仕上代を加算した調整深さ（半径値）
            # 外径+0.1mm / 内径-0.1mm（直径値）= 0.05mm（半径値）を追加
            adj_depth = round(depth_info["total_depth"] + _MATERIAL_STOCK / 2, 4)
            depth_info["adj_total_depth"] = adj_depth

            # オークマ G71 固有の切り込みシーケンスに差し替え（adj_depth 基準）
            if nc == "オークマ":
                depth_info["cuts"] = _okuma_cuts(adj_depth, pitch)
            else:
                # ファナック：adj_depth で等断面積法を再計算
                fc  = min(0.3 * pitch, adj_depth * 0.4)
                mc  = max(0.05, pitch * 0.02)
                cuts_adj = []
                rem = adj_depth
                cn  = 0
                while rem > 0.001:
                    cn += 1
                    c = fc if cn == 1 else max((math.sqrt(cn) - math.sqrt(cn - 1)) * fc, mc)
                    c = min(c, rem)
                    cuts_adj.append(round(c, 4))
                    rem -= c
                    if rem <= mc:
                        cuts_adj[-1] = round(cuts_adj[-1] + rem, 4)
                        rem = 0
                depth_info["cuts"] = cuts_adj

            # パス数オーバーライド
            passes_str = self.passes_var.get().strip()
            _finish_passes = 0 if nc == "オークマ" else 2
            auto_passes = len(depth_info["cuts"]) + _finish_passes
            if passes_str:
                n = int(passes_str)
                if n < 1:
                    raise ValueError("パス数は1以上を指定してください。")
                first_cut = adj_depth / math.sqrt(n)
                min_cut = max(0.05, pitch * 0.02)
                cuts = []
                remaining = adj_depth
                for i in range(1, n + 1):
                    if i < n:
                        c = (math.sqrt(i) - math.sqrt(i - 1)) * first_cut
                        c = max(c, min_cut)
                        c = min(c, remaining)
                        cuts.append(round(c, 4))
                        remaining = round(adj_depth - sum(cuts), 4)
                    else:
                        cuts.append(round(remaining, 4))
                depth_info["cuts"] = cuts
                self.passes_label.config(text=f"(自動: {auto_passes} パス)")
            else:
                self.passes_label.config(text=f"→ 自動: {auto_passes} パス")

            params = {
                "thread_name": f"{size_nm}  P={pitch:.4f}mm",
                "depth_info":  depth_info,
                "pitch":       pitch,
                "z_start":     z_start,
                "z_end":       z_end,
                "is_external": is_ext,
                "is_taper":    ttype in TAPER_TYPES,
                "d_nominal":   diam,
                "nose_r":      nose_r,
                "cut_mode":    self.cut_mode_var.get(),
            }

            if nc == "オークマ":
                program = generate_okuma(params)
            else:
                program = generate_fanuc(params)

            # 計算情報表示
            d2e = depth_info["d2_ext_avg"]
            d2i = depth_info["d2_int_avg"]
            xt = depth_info["x_target"]
            info_lines = [
                f"ねじ山角度         : {depth_info['angle_deg']}°",
                f"基準有効径(d2基本)  : {depth_info['d2_basic']:.4f} mm"  if depth_info['d2_basic'] else "",
                f"雄ねじ有効径(6g平均): {d2e:.4f} mm"                     if d2e else "",
                f"雌ねじ有効径(6H平均): {d2i:.4f} mm"                     if d2i else "",
                f"X目標径(谷径/山径) : {xt:.4f} mm"                       if xt is not None else "",
                f"切り込み深さ(片側) : {depth_info['total_depth']:.4f} mm",
                f"パス数             : {len(depth_info['cuts']) + (2 if nc != 'オークマ' else 0)}",
                f"各パス切り込み     : {[f'{c:.4f}' for c in depth_info['cuts']]}",
            ]
            info_lines = [l for l in info_lines if l]
            self._set_text(self.info_text, "\n".join(info_lines))
            self._set_text(self.prog_text, program)

        except ValueError as e:
            messagebox.showerror("入力エラー", str(e))

    def _set_text(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        if isinstance(widget, tk.Text) and not isinstance(widget, scrolledtext.ScrolledText):
            widget.configure(state="disabled")

    def _clear(self):
        self._set_text(self.info_text, "")
        self._set_text(self.prog_text, "")

    def _copy(self):
        content = self.prog_text.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("コピー完了", "プログラムをクリップボードにコピーしました。")


# ============================================================
if __name__ == "__main__":
    app = ThreadCuttingApp()
    app.mainloop()
