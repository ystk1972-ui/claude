import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math

# ============================================================
# ISO/JIS ねじ規格データベース（オフライン内蔵）
# ============================================================

# メートルねじ (M) — ISO 724 / JIS B 0205
# key: (呼び径, ピッチ)  value: (有効径d2, 谷径d1, 外径d)
METRIC_THREAD = {
    # (D, P): (d2, d1)  ※外径=Dなので省略
    ("M1",    0.25): (0.838,  0.693),
    ("M1.2",  0.25): (1.038,  0.893),
    ("M1.4",  0.3):  (1.205,  1.032),
    ("M1.6",  0.35): (1.373,  1.171),
    ("M2",    0.4):  (1.740,  1.509),
    ("M2.5",  0.45): (2.208,  1.948),
    ("M3",    0.5):  (2.675,  2.387),
    ("M3.5",  0.6):  (3.110,  2.764),
    ("M4",    0.7):  (3.545,  3.141),
    ("M5",    0.8):  (4.480,  4.019),
    ("M6",    1.0):  (5.350,  4.773),
    ("M7",    1.0):  (6.350,  5.773),
    ("M8",    1.25): (7.188,  6.466),
    ("M10",   1.5):  (9.026,  8.160),
    ("M12",   1.75): (10.863, 9.853),
    ("M14",   2.0):  (12.701, 11.546),
    ("M16",   2.0):  (14.701, 13.546),
    ("M18",   2.5):  (16.376, 14.933),
    ("M20",   2.5):  (18.376, 16.933),
    ("M22",   2.5):  (20.376, 18.933),
    ("M24",   3.0):  (22.051, 20.319),
    ("M27",   3.0):  (25.051, 23.319),
    ("M30",   3.5):  (27.727, 25.706),
    ("M33",   3.5):  (30.727, 28.706),
    ("M36",   4.0):  (33.402, 31.093),
    ("M39",   4.0):  (36.402, 34.093),
    ("M42",   4.5):  (39.077, 36.479),
    ("M45",   4.5):  (42.077, 39.479),
    ("M48",   5.0):  (44.752, 41.866),
    ("M52",   5.0):  (48.752, 45.866),
    ("M56",   5.5):  (52.428, 49.252),
    ("M60",   5.5):  (56.428, 53.252),
    ("M64",   6.0):  (60.103, 56.639),
    ("M68",   6.0):  (64.103, 60.639),
}

# メートルねじ細目 (MF)
METRIC_FINE_THREAD = {
    ("M8x1",    1.0):  (7.350,  6.773),
    ("M10x1",   1.0):  (9.350,  8.773),
    ("M10x1.25",1.25): (9.188,  8.466),
    ("M12x1",   1.0):  (11.350, 10.773),
    ("M12x1.25",1.25): (11.188, 10.466),
    ("M12x1.5", 1.5):  (11.026, 10.160),
    ("M14x1.5", 1.5):  (13.026, 12.160),
    ("M16x1.5", 1.5):  (15.026, 14.160),
    ("M18x1.5", 1.5):  (17.026, 16.160),
    ("M20x1.5", 1.5):  (19.026, 18.160),
    ("M22x1.5", 1.5):  (21.026, 20.160),
    ("M24x2",   2.0):  (22.701, 21.546),
    ("M27x2",   2.0):  (25.701, 24.546),
    ("M30x2",   2.0):  (28.701, 27.546),
    ("M33x2",   2.0):  (31.701, 30.546),
    ("M36x3",   3.0):  (34.051, 32.319),
    ("M39x3",   3.0):  (37.051, 35.319),
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
    ("G1.1/4", 2.309): (41.910, 40.431, 41.910),
    ("G1.1/2", 2.309): (47.803, 46.324, 47.803),
    ("G2",     2.309): (59.614, 58.135, 59.614),
    ("G2.1/2", 2.309): (75.184, 73.705, 75.184),
    ("G3",     2.309): (87.884, 86.405, 87.884),
    ("G4",     2.309): (113.030,111.551,113.030),
    ("G5",     2.309): (138.430,136.951,138.430),
    ("G6",     2.309): (163.830,162.351,163.830),
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
    ("R1.1/4", 2.309): (41.910, 40.431, 41.910),
    ("R1.1/2", 2.309): (47.803, 46.324, 47.803),
    ("R2",     2.309): (59.614, 58.135, 59.614),
    ("R2.1/2", 2.309): (75.184, 73.705, 75.184),
    ("R3",     2.309): (87.884, 86.405, 87.884),
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
    ('NPT3"',     3.175): (87.884, 85.798, 87.884),
    ('NPT4"',     3.175): (113.030,110.944,113.030),
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
# ねじ切り計算
# ============================================================

def calc_thread_depth(pitch: float, nose_r: float, thread_type: str, is_external: bool) -> dict:
    """
    ねじ切り深さと切り込み回数を計算する。
    ISO/IEC ねじ山プロファイル（60°）ベース。
    管用テーパー・ウィットは55°。
    """
    is_55deg = ("テーパー" in thread_type or "NPT" in thread_type or
                "管用平行" in thread_type or "ウィット" in thread_type)

    if is_55deg:
        # 55° ねじ山 (Whitworth プロファイル)
        h = 0.9605 * pitch          # ねじ山高さ理論値
        r_adj = nose_r / math.sin(math.radians(27.5))
    else:
        # 60° ねじ山 (メートル/ユニファイ)
        h = 0.8660 * pitch          # ねじ山高さ理論値
        r_adj = nose_r / math.sin(math.radians(30))

    # 実切り込み深さ = 理論高さ - ノーズR分の補正
    # ISO 68-1: 雄ねじ有効切り込み = h - r_correction
    nose_correction = nose_r * (1.0 / math.tan(math.radians(30 if not is_55deg else 27.5)))
    actual_depth = h - nose_r * (1 - math.sin(math.radians(30 if not is_55deg else 27.5)))

    # 雌ねじは少し深めに (公差分)
    if not is_external:
        actual_depth *= 1.08

    # 切り込み回数（等分切り込み：各パスの切り込み量を一定）
    # 推奨：初回 0.3P 以下、最小 0.05mm
    first_cut = min(0.3 * pitch, actual_depth * 0.4)
    min_cut = max(0.05, pitch * 0.02)

    cuts = []
    remaining = actual_depth
    cut_num = 1
    while remaining > 0.001:
        if cut_num == 1:
            c = first_cut
        else:
            # 漸減切り込み（等切り込み断面積法）
            c = math.sqrt(cut_num) * first_cut - math.sqrt(cut_num - 1) * first_cut
            c = max(c, min_cut)
        c = min(c, remaining)
        cuts.append(round(c, 4))
        remaining -= c
        if remaining <= min_cut:
            if cuts:
                cuts[-1] += remaining
                cuts[-1] = round(cuts[-1], 4)
            remaining = 0
        cut_num += 1

    return {
        "total_depth": round(actual_depth, 4),
        "h_theory": round(h, 4),
        "nose_correction": round(nose_r * (1 - math.sin(math.radians(30 if not is_55deg else 27.5))), 4),
        "cuts": cuts,
        "angle_deg": 55 if is_55deg else 60,
    }


def generate_okuma(params: dict) -> str:
    """オークマ OSP 形式のねじ切りプログラムを生成する。"""
    t = params
    depth_info = t["depth_info"]
    pitch = t["pitch"]
    z_start = t["z_start"]
    z_end = t["z_end"]
    is_external = t["is_external"]
    is_taper = t["is_taper"]
    taper_angle = 1.7899  # 管用テーパー 1/16 rad→deg

    d_nominal = t["d_nominal"]   # 外径（雄）or 谷径（雌）
    total_depth = depth_info["total_depth"]

    lines = [
        f"( *** NC Thread Cutting Program ***)",
        f"( Thread : {t['thread_name']} )",
        f"( Type   : {'雄ねじ' if is_external else '雌ねじ'} )",
        f"( Pitch  : {pitch:.4f} mm )",
        f"( Depth  : {total_depth:.4f} mm  [{len(depth_info['cuts'])} passes] )",
        f"( Nose R : {t['nose_r']} mm )",
        "",
        "N10 G28 U0 W0",
        "N20 G50 S2000",
        "N30 G97 S500 M03",
        "N40 G00 T0101",
    ]

    if is_external:
        x_start = d_nominal + 2.0   # アプローチX
        x_base  = d_nominal
    else:
        x_start = d_nominal - 2.0
        x_base  = d_nominal

    lines.append(f"N50 G00 X{x_start:.3f} Z{z_start + pitch * 3:.3f}")
    lines.append("")

    seq = 60
    cumulative = 0.0
    for i, cut in enumerate(depth_info["cuts"]):
        cumulative += cut
        if is_external:
            x_cut = round(x_base - cumulative * 2, 3)
        else:
            x_cut = round(x_base + cumulative * 2, 3)

        lines.append(f"N{seq} ( Pass {i+1}: 切り込み {cut:.4f}mm / 累計 {cumulative:.4f}mm )")
        lines.append(f"N{seq+1} G00 X{x_cut:.3f}")

        if is_taper:
            taper_k = round((z_end - z_start) / 32.0, 3)  # 1/16 テーパー
            lines.append(f"N{seq+2} G32 X{x_cut:.3f} Z{z_end:.3f} F{pitch:.4f} K{taper_k:.3f}")
        else:
            lines.append(f"N{seq+2} G32 Z{z_end:.3f} F{pitch:.4f}")

        lines.append(f"N{seq+3} G00 X{x_start:.3f}")
        lines.append(f"N{seq+4} G00 Z{z_start + pitch * 3:.3f}")
        lines.append("")
        seq += 10

    lines += [
        f"N{seq} ( 仕上げパス )",
        f"N{seq+1} G32 Z{z_end:.3f} F{pitch:.4f}",
        f"N{seq+2} G00 X{x_start:.3f}",
        f"N{seq+3} G00 Z{z_start + pitch * 3:.3f}",
        "",
        f"N{seq+10} G28 U0 W0",
        f"N{seq+20} M05",
        f"N{seq+30} M30",
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
    first_cut_um = int(cuts[0] * 1000)   # μm 単位
    min_cut_um   = max(50, int(min(cuts) * 1000))
    depth_um     = int(total_depth * 1000)

    if is_external:
        x_end_dia = round(d_nominal - total_depth * 2, 3)
        x_approach = round(d_nominal + 2.0, 3)
    else:
        x_end_dia = round(d_nominal + total_depth * 2, 3)
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
        f"( Type   : {'雄ねじ' if is_external else '雌ねじ'} )",
        f"( Pitch  : {pitch:.4f} mm )",
        f"( Depth  : {total_depth:.4f} mm  [{len(cuts)} passes] )",
        f"( Nose R : {t['nose_r']} mm )",
        "",
        "O0001",
        "N10 G28 U0 W0",
        "N20 G50 S2000",
        "N30 G97 S500 M03",
        "N40 G00 T0101",
        f"N50 G00 X{x_approach:.3f} Z{z_start + pitch * 3:.3f}",
        "",
        f"( G76 複合ねじ切りサイクル )",
        f"N60 G76 P0{2}1{1}{angle:02d} Q{min_cut_um} R0.05",
    ]

    if is_taper:
        lines.append(
            f"N70 G76 X{x_end_dia:.3f} Z{z_end:.3f} I{taper_i:.3f} "
            f"K{depth_um} D{first_cut_um} F{pitch:.4f} A{angle}"
        )
    else:
        lines.append(
            f"N70 G76 X{x_end_dia:.3f} Z{z_end:.3f} "
            f"K{depth_um} D{first_cut_um} F{pitch:.4f} A{angle}"
        )

    lines += [
        "",
        "N80 G28 U0 W0",
        "N90 M05",
        "N100 M30",
        "%",
    ]
    return "\n".join(lines)


# ============================================================
# GUI
# ============================================================

class ThreadCuttingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NC旋盤 ねじ切りプログラム生成")
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
        grp2 = ttk.LabelFrame(left, text="2. ねじの性別", padding=8)
        grp2.pack(fill="x", pady=(0, 8))

        self.gender_var = tk.StringVar(value="外")
        fr2 = ttk.Frame(grp2)
        fr2.pack()
        ttk.Radiobutton(fr2, text="雄ねじ (外ねじ)", variable=self.gender_var, value="外").pack(anchor="w")
        ttk.Radiobutton(fr2, text="雌ねじ (内ねじ)", variable=self.gender_var, value="内").pack(anchor="w")

        # ---- 3. NCコントロール ----
        grp3 = ttk.LabelFrame(left, text="3. NCコントロール", padding=8)
        grp3.pack(fill="x", pady=(0, 8))

        self.nc_var = tk.StringVar(value="ファナック")
        fr3 = ttk.Frame(grp3)
        fr3.pack()
        ttk.Radiobutton(fr3, text="ファナック (G76)", variable=self.nc_var, value="ファナック").pack(anchor="w")
        ttk.Radiobutton(fr3, text="オークマ (G32)", variable=self.nc_var,  value="オークマ").pack(anchor="w")

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

        self.noser_var = tk.StringVar(value="0.2")
        cb_nr = ttk.Combobox(grp6, textvariable=self.noser_var,
                              values=["0.1", "0.2", "0.4", "0.8"], width=8)
        cb_nr.pack(anchor="w")

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
        ttype = self.thread_type_var.get()
        db = THREAD_DB[ttype]
        size_name = self.size_var.get()

        for key, val in db.items():
            if key[0] == size_name:
                # val は (d2, d1, d) or (d2, d1)
                if len(val) == 3:
                    d_outer = val[2]
                else:
                    # メートルねじ等: 呼び径から外径を推定
                    try:
                        num = float(size_name.lstrip("M").split("x")[0].split("W")[0]
                                    .replace('"','').replace("'","").strip())
                        d_outer = num
                    except:
                        d_outer = val[0]
                self.diam_var.set(f"{d_outer:.3f}")
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

            depth_info = calc_thread_depth(pitch, nose_r, ttype, is_ext)

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
            }

            if nc == "オークマ":
                program = generate_okuma(params)
            else:
                program = generate_fanuc(params)

            # 計算情報表示
            info_lines = [
                f"ねじ山角度   : {depth_info['angle_deg']}°",
                f"理論山高さ   : {depth_info['h_theory']:.4f} mm",
                f"ノーズR補正  : {depth_info['nose_correction']:.4f} mm",
                f"実切り込み深さ: {depth_info['total_depth']:.4f} mm",
                f"パス数       : {len(depth_info['cuts'])}",
                f"各パス切り込み: {[f'{c:.4f}' for c in depth_info['cuts']]}",
            ]
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
