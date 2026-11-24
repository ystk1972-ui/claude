# Free-Input Metric Fine Threads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the user type any metric fine thread (e.g. `M16x1`) into the size box and get a threading program, with dimensions and 6g/6H tolerance midpoints computed instead of looked up.

**Architecture:** Pure functions in `thread_cutting.py` parse the input, compute basic dimensions (JIS B 0205-4) and look up ISO 965-1 grade-6 tolerances from embedded tables (formula fallback for unlisted combinations). The three existing midpoint helpers route unlisted metric names through those functions. The GUI makes the size combobox editable for the MF type only and resolves sizes through one `_entries` helper.

**Tech Stack:** Python 3.14, tkinter, pytest 9.

**Spec:** `docs/superpowers/specs/2026-11-24-metric-fine-custom-design.md`

## Global Constraints

- Only `thread_cutting.py` and `tests/test_metric_fine_custom.py` change.
- Registered sizes that are in `_METRIC_EXT_AVG_6G` / `_METRIC_INT_AVG_6H` must give the same results as before.
- Diameter range 1.6–355 mm, pitch range 0.2–8 mm, pitch ≤ diameter / 4.
- Error messages are Japanese, exactly as in the spec.
- Every commit that changes `thread_cutting.py` runs `python bump_version.py <level>` first (Task 1: `minor`, Tasks 2–3: `patch`).
- Run tests with `python -m pytest tests/test_metric_fine_custom.py -q` from the repo root.

---

### Task 1: Parsing, basic dimensions and ISO 965-1 tolerances

**Files:**
- Modify: `thread_cutting.py` (imports at line 1–3; new block after `TAPER_TYPES`, line 210)
- Create: `tests/test_metric_fine_custom.py`

**Interfaces:**
- Produces:
  - `MF_TYPE: str` = `"メートル細目ねじ (MF)"`
  - `parse_metric_fine(text: str) -> tuple[str, float, float]` — `(normalised name, d, pitch)`, raises `ValueError`
  - `metric_basic_dims(d: float, pitch: float) -> tuple[float, float, float]` — `(d2, d1, D1)` rounded to 3 dp
  - `_iso965_tol(d: float, pitch: float) -> dict` — keys `es` (negative), `Td`, `Td2`, `TD2`, `TD1` in mm, `exact: bool`; raises `ValueError` outside 1.4 < d ≤ 355
  - `_metric_d_from_name(name: str | None) -> float | None`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_metric_fine_custom.py`:

```python
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import thread_cutting as tc

# JIS B 0209-2 表1〜4 (ねじ規格.pdf)。6H めねじ / 6g おねじ の許容限界寸法。
# (d, P, D2max, D2min, D1max, D1min, dmax, dmin, d2max, d2min)
# None は PDF の誤植と判断して照合しない値。
JIS_LIMITS = [
    # 並目 (表1, 表2)
    (1.6, 0.35, 1.458, 1.373, 1.321, 1.221, 1.581, 1.496, 1.354, 1.291),
    (1.8, 0.35, 1.658, 1.573, 1.521, 1.421, 1.781, 1.696, 1.554, 1.491),
    (2, 0.4, 1.830, 1.740, 1.679, 1.567, 1.981, 1.886, 1.721, 1.654),
    (2.5, 0.45, 2.303, 2.208, 2.138, 2.013, 2.480, 2.380, 2.188, 2.117),
    (3, 0.5, 2.775, 2.675, 2.599, 2.459, 2.980, 2.874, 2.655, 2.580),
    (3.5, 0.6, 3.222, 3.110, 3.010, 2.850, 3.479, 3.354, 3.089, 3.004),
    (4, 0.7, 3.663, 3.545, 3.422, 3.242, 3.978, 3.838, 3.523, 3.433),
    (5, 0.8, 4.605, 4.480, 4.334, 4.134, 4.976, 4.826, 4.456, None),
    (6, 1, 5.500, 5.350, 5.153, 4.917, 5.974, 5.794, 5.324, 5.212),
    (7, 1, 6.500, 6.350, 6.153, 5.917, 6.974, 6.794, 6.324, 6.212),
    (8, 1.25, 7.348, 7.188, 6.912, 6.647, 7.972, 7.760, 7.160, 7.042),
    (10, 1.5, 9.206, 9.026, 8.676, 8.376, 9.968, 9.732, 8.994, 8.862),
    (12, 1.75, 11.063, 10.863, 10.441, 10.106, 11.966, 11.701, 10.829, 10.679),
    (14, 2, 12.913, 12.701, 12.210, 11.835, 13.962, 13.682, 12.663, 12.503),
    (16, 2, 14.913, 14.701, 14.210, 13.835, 15.962, 15.682, 14.663, 14.503),
    (18, 2.5, 16.600, 16.376, 15.744, 15.294, 17.958, 17.623, 16.334, 16.164),
    (20, 2.5, 18.600, 18.376, 17.744, 17.294, 19.958, 19.623, 18.334, 18.164),
    (22, 2.5, 20.600, 20.376, 19.744, 19.294, 21.958, 21.623, 20.334, 20.164),
    (24, 3, 22.316, 22.051, 21.252, 20.752, 23.952, 23.577, 22.003, 21.803),
    (27, 3, None, 25.051, 24.252, 23.752, 26.952, 26.577, 25.003, 24.803),
    (30, 3.5, 28.007, 27.727, 26.771, 26.211, 29.947, 29.522, 27.674, 27.462),
    (33, 3.5, 31.007, 30.727, 29.771, 29.211, 32.947, 32.522, 30.674, 30.462),
    (36, 4, 33.702, 33.402, 32.270, 31.670, 35.940, 35.465, 33.342, 33.118),
    (39, 4, 36.702, 36.402, 35.270, 34.670, 38.940, 38.465, 36.342, 36.118),
    (42, 4.5, 39.392, 39.077, 37.799, 37.129, 41.937, 41.437, 39.014, 38.778),
    (45, 4.5, 42.392, 42.077, 40.799, 40.129, 44.937, 44.437, 42.014, 41.778),
    (48, 5, 45.087, 44.752, 43.297, 42.587, 47.929, 47.399, 44.681, 44.431),
    (52, 5, 49.087, 48.752, 47.297, 46.587, 51.929, 51.399, 48.681, 48.431),
    (56, 5.5, 52.783, 52.428, 50.796, 50.046, 55.925, 55.365, 52.353, 52.088),
    (60, 5.5, 56.783, 56.428, 54.796, 54.046, 59.925, 59.365, 56.353, 56.088),
    (64, 6, 60.478, 60.103, 58.305, 57.505, 63.920, 63.320, 60.023, 59.743),
    # 細目 (表3, 表4)
    (8, 1, 7.500, 7.350, 7.153, 6.917, 7.974, 7.794, 7.324, 7.212),
    (10, 1, 9.500, 9.350, 9.153, 8.917, 9.974, 9.794, 9.324, 9.212),
    (10, 1.25, 9.348, 9.188, 8.912, 8.647, 9.972, 9.760, 9.160, 9.042),
    (12, 1.25, 11.368, 11.188, 10.912, 10.647, 11.972, 11.760, 11.160, 11.028),
    (12, 1.5, 11.216, 11.026, 10.676, 10.376, 11.968, 11.732, 10.994, 10.854),
    (14, 1.5, 13.216, 13.026, 12.676, 12.376, 13.968, 13.732, 12.994, 12.854),
    (16, 1.5, 15.216, 15.026, 14.676, 14.376, 15.968, 15.732, 14.994, 14.854),
    (18, 1.5, 17.216, 17.026, 16.676, 16.376, 17.968, 17.732, 16.994, 16.854),
    (18, 2, 16.913, 16.701, 16.210, 15.835, 17.962, 17.682, 16.663, 16.503),
    (20, 1.5, 19.216, 19.026, 18.676, 18.376, 19.968, 19.732, 18.994, 18.854),
    (20, 2, 18.913, 18.701, 18.210, 17.835, 19.962, 19.682, 18.663, 18.503),
    (22, 1.5, 21.216, 21.026, 20.676, 20.376, 21.968, 21.732, 20.994, 20.854),
    (22, 2, 20.913, 20.701, 20.210, 19.835, 21.962, 21.682, 20.663, 20.503),
    (24, 2, 22.925, 22.701, 22.210, 21.835, 23.962, 23.682, 22.663, 22.493),
    (27, 2, 25.925, 25.701, 25.210, 24.835, 26.962, 26.682, 25.663, 25.493),
    (30, 2, 28.925, 28.701, 28.210, 27.835, 29.962, 29.682, 28.663, 28.493),
    (33, 2, 31.925, 31.701, 31.210, 30.835, 32.962, 32.682, 31.663, 31.493),
    (36, 3, 34.316, 34.051, 33.252, 32.752, 35.952, 35.577, 34.003, 33.803),
    (39, 3, 37.316, 37.051, 36.252, 35.752, 38.952, 38.577, 37.003, 36.803),
    (42, 3, 40.316, 40.051, 39.252, 38.752, 41.952, 41.577, 40.003, 39.803),
    (45, 3, 43.316, 43.051, 42.252, 41.752, 44.952, 44.577, 43.003, 42.803),
    (48, 3, 46.331, 46.051, 45.252, 44.752, 47.952, 47.577, 46.003, 45.791),
    (52, 4, 49.717, 49.402, 48.270, 47.670, 51.940, 51.465, 49.342, 49.106),
    (56, 4, 53.717, 53.402, 52.270, 51.670, 55.940, 55.465, 53.342, 53.106),
    (60, 4, 57.717, 57.402, 56.270, 55.670, 59.940, 59.465, 57.342, 57.106),
    (64, 4, 61.717, 61.402, 60.270, 59.670, 63.940, 63.465, 61.342, 61.106),
]


@pytest.mark.parametrize("row", JIS_LIMITS, ids=lambda r: f"M{r[0]}x{r[1]}")
def test_limits_match_jis_table(row):
    d, p, D2max, D2min, D1max, D1min, dmax, dmin, d2max, d2min = row
    d2, _d1, D1 = tc.metric_basic_dims(d, p)
    t = tc._iso965_tol(d, p)
    assert t["exact"]
    computed = [
        (d2 + t["TD2"], D2max), (d2, D2min),
        (D1 + t["TD1"], D1max), (D1, D1min),
        (d + t["es"], dmax), (d + t["es"] - t["Td"], dmin),
        (d2 + t["es"], d2max), (d2 + t["es"] - t["Td2"], d2min),
    ]
    for got, want in computed:
        if want is not None:
            assert got == pytest.approx(want, abs=0.0011)


def test_m16x1_dimensions():
    assert tc.metric_basic_dims(16, 1) == (15.350, 14.773, 14.917)
    t = tc._iso965_tol(16, 1)
    assert t["exact"]
    assert (t["es"], t["Td"], t["Td2"], t["TD2"], t["TD1"]) == pytest.approx(
        (-0.026, 0.180, 0.118, 0.160, 0.236))


@pytest.mark.parametrize("text", ["M16x1", "m16X1", "16x1", "M16×1", " M16 x 1 ", "M16*1.0"])
def test_parse_normalises(text):
    assert tc.parse_metric_fine(text) == ("M16x1", 16.0, 1.0)


def test_parse_keeps_decimals():
    assert tc.parse_metric_fine("M10x1.25") == ("M10x1.25", 10.0, 1.25)


@pytest.mark.parametrize("text, message", [
    ("abc", "「M16x1」の形式で入力してください。"),
    ("M16", "「M16x1」の形式で入力してください。"),
    ("", "「M16x1」の形式で入力してください。"),
    ("M1x0.2", "呼び径は 1.6〜355 mm の範囲で入力してください。"),
    ("M400x4", "呼び径は 1.6〜355 mm の範囲で入力してください。"),
    ("M16x10", "ピッチは 0.2〜8 mm の範囲で入力してください。"),
    ("M16x0.1", "ピッチは 0.2〜8 mm の範囲で入力してください。"),
    ("M8x3", "ピッチが呼び径に対して大きすぎます。"),
])
def test_parse_rejects(text, message):
    with pytest.raises(ValueError) as exc:
        tc.parse_metric_fine(text)
    assert str(exc.value) == message


def test_unlisted_combination_is_approximate():
    t = tc._iso965_tol(50, 1)          # 45〜90 の区分に P=1 は規格表にない
    assert not t["exact"]
    assert 0.118 <= t["Td2"] <= 0.140  # 隣の区分 (22.4〜45: 0.125) と同程度
    assert t["es"] == pytest.approx(-0.026)


def test_metric_d_from_name():
    assert tc._metric_d_from_name("M16x1") == 16.0
    assert tc._metric_d_from_name("M2.5") == 2.5
    assert tc._metric_d_from_name("G1/2") is None
    assert tc._metric_d_from_name(None) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_metric_fine_custom.py -q`
Expected: FAIL — `AttributeError: module 'thread_cutting' has no attribute 'metric_basic_dims'` (and similar).

- [ ] **Step 3: Implement**

In `thread_cutting.py`, add `import re` after `import math`.

Insert after the `TAPER_TYPES = {...}` line:

```python
# 手入力（任意の径×ピッチ）を受け付けるねじ種類
MF_TYPE = "メートル細目ねじ (MF)"

# ============================================================
# メートルねじ 任意サイズ計算（JIS B 0205-4 / ISO 965-1 公差グレード6）
# 公差値の単位は μm。計算式を R40 数列に丸めた規格表の値を内蔵する
# （丸め方が一定でなく、計算式だけでは規格表を再現できないため）。
# ============================================================

# 外ねじ g の上の寸法差 es（符号なし） — pitch: μm
_ISO965_ES_G = {
    0.2: 17, 0.25: 18, 0.3: 18, 0.35: 19, 0.4: 19, 0.45: 20, 0.5: 20,
    0.6: 21, 0.7: 22, 0.75: 22, 0.8: 24, 1.0: 26, 1.25: 28, 1.5: 32,
    1.75: 34, 2.0: 38, 2.5: 42, 3.0: 48, 3.5: 53, 4.0: 60, 4.5: 63,
    5.0: 71, 5.5: 75, 6.0: 80, 8.0: 100,
}

# 外ねじ外径公差 Td グレード6 — pitch: μm
_ISO965_TD_6 = {
    0.2: 56, 0.25: 67, 0.3: 75, 0.35: 85, 0.4: 95, 0.45: 100, 0.5: 106,
    0.6: 125, 0.7: 140, 0.75: 140, 0.8: 150, 1.0: 180, 1.25: 212, 1.5: 236,
    1.75: 265, 2.0: 280, 2.5: 335, 3.0: 375, 3.5: 425, 4.0: 475, 4.5: 500,
    5.0: 530, 5.5: 560, 6.0: 600, 8.0: 750,
}

# 内ねじ内径公差 TD1 グレード6 — pitch: μm
_ISO965_TD1_6 = {
    0.35: 100, 0.4: 112, 0.45: 125, 0.5: 140, 0.6: 160, 0.7: 180, 0.75: 190,
    0.8: 200, 1.0: 236, 1.25: 265, 1.5: 300, 1.75: 335, 2.0: 375, 2.5: 450,
    3.0: 500, 3.5: 560, 4.0: 600, 4.5: 670, 5.0: 710, 5.5: 750, 6.0: 800,
    8.0: 1000,
}

# 有効径公差 グレード6 — 径区分の上限: {pitch: (Td2 外ねじ, TD2 内ねじ)} μm
_ISO965_PD_6 = {
    2.8:  {0.35: (63, 85), 0.4: (67, 90), 0.45: (71, 95)},
    5.6:  {0.35: (67, 90), 0.5: (75, 100), 0.6: (85, 112), 0.7: (90, 118),
           0.75: (90, 118), 0.8: (95, 125)},
    11.2: {0.75: (100, 132), 1.0: (112, 150), 1.25: (118, 160), 1.5: (132, 180)},
    22.4: {1.0: (118, 160), 1.25: (132, 180), 1.5: (140, 190), 1.75: (150, 200),
           2.0: (160, 212), 2.5: (170, 224)},
    45:   {1.0: (125, 170), 1.5: (150, 200), 2.0: (170, 224), 3.0: (200, 265),
           3.5: (212, 280), 4.0: (224, 300), 4.5: (236, 315)},
    90:   {1.5: (160, 212), 2.0: (180, 236), 3.0: (212, 280), 4.0: (236, 315),
           5.0: (250, 335), 5.5: (265, 355), 6.0: (280, 375)},
    180:  {2.0: (190, 250), 3.0: (224, 300), 4.0: (250, 335), 6.0: (300, 400),
           8.0: (335, 450)},
    355:  {3.0: (250, 335), 4.0: (280, 375), 6.0: (315, 425), 8.0: (355, 475)},
}

# ISO 965-1 の径区分（を超え・以下）
_ISO965_D_LIMITS = (1.4, 2.8, 5.6, 11.2, 22.4, 45, 90, 180, 355)

_R40 = (10, 10.6, 11.2, 11.8, 12.5, 13.2, 14, 15, 16, 17, 18, 19, 20, 21.2,
        22.4, 23.6, 25, 26.5, 28, 30, 31.5, 33.5, 35.5, 37.5, 40, 42.5, 45,
        47.5, 50, 53, 56, 60, 63, 67, 71, 75, 80, 85, 90, 95, 100)

_MF_INPUT = re.compile(r"^\s*[Mm]?\s*(\d+(?:\.\d+)?)\s*[xX×*]\s*(\d+(?:\.\d+)?)\s*$")


def _r40(x: float) -> float:
    """R40 標準数のうち最も近い値に丸める。"""
    dec = 10 ** (math.floor(math.log10(x)) - 1)
    return min(_R40, key=lambda v: abs(v - x / dec)) * dec


def _by_pitch(table: dict, pitch: float):
    """ピッチが一致する行の値を返す。なければ None。"""
    for p, v in table.items():
        if abs(p - pitch) < 1e-6:
            return v
    return None


def parse_metric_fine(text: str) -> tuple:
    """「M16x1」形式の入力を (正規化した名前, 呼び径, ピッチ) にする。不正なら ValueError。"""
    m = _MF_INPUT.match(text or "")
    if not m:
        raise ValueError("「M16x1」の形式で入力してください。")
    d, pitch = float(m.group(1)), float(m.group(2))
    if not 1.6 <= d <= 355:
        raise ValueError("呼び径は 1.6〜355 mm の範囲で入力してください。")
    if not 0.2 <= pitch <= 8:
        raise ValueError("ピッチは 0.2〜8 mm の範囲で入力してください。")
    if pitch > d / 4:
        raise ValueError("ピッチが呼び径に対して大きすぎます。")
    return f"M{d:g}x{pitch:g}", d, pitch


def metric_basic_dims(d: float, pitch: float) -> tuple:
    """メートルねじの基準寸法 (d2, d1, D1) — JIS B 0205-4。"""
    return (round(d - 0.649519 * pitch, 3),
            round(d - 1.226869 * pitch, 3),
            round(d - 1.082532 * pitch, 3))


def _metric_d_from_name(name) -> float:
    """「M16x1」「M16」から呼び径を返す。メートルねじの名前でなければ None。"""
    m = re.match(r"M(\d+(?:\.\d+)?)", name or "")
    return float(m.group(1)) if m else None


def _iso965_tol(d: float, pitch: float) -> dict:
    """ISO 965-1 公差グレード6 の公差値 (mm)。

    es は外ねじ g の上の寸法差（負値）。規格表にない径×ピッチは計算式を
    R40 数列に丸めた概算値を使い、exact=False を返す。
    """
    for lo, hi in zip(_ISO965_D_LIMITS, _ISO965_D_LIMITS[1:]):
        if lo < d <= hi:
            break
    else:
        raise ValueError("呼び径は 1.6〜355 mm の範囲で入力してください。")

    exact = True
    es = _by_pitch(_ISO965_ES_G, pitch)
    if es is None:
        exact, es = False, round(15 + 11 * pitch)
    Td = _by_pitch(_ISO965_TD_6, pitch)
    if Td is None:
        exact, Td = False, _r40(180 * pitch ** (2 / 3) - 3.15 / math.sqrt(pitch))
    TD1 = _by_pitch(_ISO965_TD1_6, pitch)
    if TD1 is None:
        exact = False
        TD1 = _r40(433 * pitch - 190 * pitch ** 1.22 if pitch < 1
                   else 230 * pitch ** 0.7)
    pd = _by_pitch(_ISO965_PD_6[hi], pitch)
    if pd is None:
        exact = False
        base = 90 * pitch ** 0.4 * math.sqrt(lo * hi) ** 0.1
        pd = (_r40(base), _r40(1.32 * base))

    return {"es": -es / 1000, "Td": Td / 1000, "Td2": pd[0] / 1000,
            "TD2": pd[1] / 1000, "TD1": TD1 / 1000, "exact": exact}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_metric_fine_custom.py -q`
Expected: all pass (80 tests).

- [ ] **Step 5: Bump version and commit**

```bash
python bump_version.py minor
git add thread_cutting.py tests/test_metric_fine_custom.py
git commit -m "v1.5.0: Add metric thread parsing and ISO 965-1 tolerance calculation"
```

---

### Task 2: Route unlisted metric names through the ISO 965-1 calculation

**Files:**
- Modify: `thread_cutting.py` — `_d_major_avg`, `_D1_minor_avg`, `_d2_avg`
- Test: `tests/test_metric_fine_custom.py` (append)

**Interfaces:**
- Consumes: `_iso965_tol`, `_metric_d_from_name`, `metric_basic_dims` (Task 1)
- Produces: `_d_major_avg`, `_D1_minor_avg`, `_d2_avg` keep their signatures; for a `thread_name` starting with `M` that is not in the direct JIS tables they now return ISO 965-1 midpoints.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_metric_fine_custom.py`:

```python
import math


def test_m16x1_midpoints():
    d2, _d1, D1 = tc.metric_basic_dims(16, 1)
    assert tc._d_major_avg(16.0, 1.0, "M16x1") == pytest.approx(15.884)
    assert tc._d2_avg(d2, 1.0, True, 15.884, "M16x1") == pytest.approx(15.265)
    assert tc._d2_avg(d2, 1.0, False, 15.035, "M16x1") == pytest.approx(15.430)
    assert tc._D1_minor_avg(D1, 1.0, "M16x1") == pytest.approx(15.035)


def test_registered_sizes_still_use_direct_tables():
    for (name, p), (d2_avg, d_avg) in tc._METRIC_EXT_AVG_6G.items():
        assert tc._d2_avg(0.0, p, True, None, name) == d2_avg
        assert tc._d_major_avg(0.0, p, name) == d_avg
    for (name, p), (D2_avg, D1_avg) in tc._METRIC_INT_AVG_6H.items():
        assert tc._d2_avg(0.0, p, False, None, name) == D2_avg
        assert tc._D1_minor_avg(0.0, p, name) == D1_avg


def test_non_metric_names_unchanged():
    # 管用平行ねじは従来の予備計算のまま (es=-0.032 は _PD_TOL_6HG の P=1.75〜2.5 相当)
    assert tc._d_major_avg(20.955, 1.814, "G1/2") == round(
        20.955 + tc._PD_TOL_6HG[1.75][0] - tc._MAJOR_TOL_6G[1.75] / 2, 4)


def test_calc_thread_depth_m16x1():
    d2, _d1, _D1 = tc.metric_basic_dims(16, 1)
    tan30, sin30 = math.tan(math.radians(30)), 0.5
    ext = tc.calc_thread_depth(1.0, 0.1, tc.MF_TYPE, True, d2, 15.884, "M16x1")
    assert ext["d2_ext_avg"] == pytest.approx(15.265)
    assert ext["x_target"] == pytest.approx(
        (15.265 / 2 - 0.25 / tan30 + 0.1 / sin30 - 0.1) * 2, abs=1e-4)
    assert ext["total_depth"] == pytest.approx((15.884 - ext["x_target"]) / 2, abs=1e-4)
    inn = tc.calc_thread_depth(1.0, 0.1, tc.MF_TYPE, False, d2, 15.035, "M16x1")
    assert inn["d2_int_avg"] == pytest.approx(15.430)
    assert inn["x_target"] == pytest.approx(
        (15.430 / 2 + 0.25 / tan30 - 0.1 / sin30 + 0.1) * 2, abs=1e-4)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_metric_fine_custom.py -q`
Expected: `test_m16x1_midpoints` and `test_calc_thread_depth_m16x1` FAIL (values from the old fallback, e.g. 15.265 expected but 15.261 returned); the other two new tests pass.

- [ ] **Step 3: Implement**

Add this helper directly above `_d_major_avg`:

```python
def _iso965_for(thread_name, pitch: float):
    """メートルねじ名なら ISO 965-1 公差 dict、それ以外（または範囲外）は None。"""
    d = _metric_d_from_name(thread_name)
    if d is None:
        return None
    try:
        return _iso965_tol(d, pitch)
    except ValueError:
        return None
```

In `_d_major_avg`, insert after the direct-table `if thread_name is not None:` block:

```python
    tol = _iso965_for(thread_name, pitch)
    if tol is not None:
        return round(d_basic + tol["es"] - tol["Td"] / 2, 4)
```

In `_D1_minor_avg`, insert after the direct-table block:

```python
    tol = _iso965_for(thread_name, pitch)
    if tol is not None:
        return round(D1_basic + tol["TD1"] / 2, 4)
```

In `_d2_avg`, insert after the direct-table block:

```python
    tol = _iso965_for(thread_name, pitch)
    if tol is not None:
        if is_external:
            return round(d2_basic + tol["es"] - tol["Td2"] / 2, 4)
        return round(d2_basic + tol["TD2"] / 2, 4)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_metric_fine_custom.py -q`
Expected: all pass.

- [ ] **Step 5: Bump version and commit**

```bash
python bump_version.py patch
git add thread_cutting.py tests/test_metric_fine_custom.py
git commit -m "v1.5.1: Use ISO 965-1 tolerances for metric sizes outside the JIS tables"
```

---

### Task 3: Editable size box in the GUI

**Files:**
- Modify: `thread_cutting.py` — `ThreadCuttingApp.__init__`, `_build_ui` (size combobox), `_on_type_change`, `_on_size_change`, `_set_default_diameter`, `_generate`; new methods `_entries`, `_commit_size`, `_on_size_entered`
- Test: `tests/test_metric_fine_custom.py` (append)

**Interfaces:**
- Consumes: `MF_TYPE`, `parse_metric_fine`, `metric_basic_dims`, `_iso965_tol`, `_metric_d_from_name` (Task 1)
- Produces:
  - `ThreadCuttingApp._entries(ttype: str, size_name: str) -> dict` — `{(name, pitch): value tuple}`
  - `ThreadCuttingApp._commit_size() -> None` — normalises a typed MF size, refreshes pitch/diameter when the size changed, raises `ValueError` on bad input

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_metric_fine_custom.py`:

```python
import tkinter as tk


@pytest.fixture
def app(monkeypatch):
    try:
        a = tc.ThreadCuttingApp()
    except tk.TclError:
        pytest.skip("Tk が使えない環境")
    a.withdraw()
    errors = []
    monkeypatch.setattr(tc.messagebox, "showerror", lambda title, msg: errors.append(msg))
    a.errors = errors
    yield a
    a.destroy()


def _select_type(app, ttype):
    app.thread_type_var.set(ttype)
    app._on_type_change()


def test_size_box_editable_only_for_mf(app):
    assert str(app.cb_size.cget("state")) == "readonly"      # 初期: メートルねじ (M)
    _select_type(app, tc.MF_TYPE)
    assert str(app.cb_size.cget("state")) == "normal"
    _select_type(app, "管用平行ねじ (G)")
    assert str(app.cb_size.cget("state")) == "readonly"


def test_typed_size_fills_pitch_and_diameter(app):
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("m16X1")
    app._commit_size()
    assert app.size_var.get() == "M16x1"
    assert app.pitch_var.get() == "1.0"
    assert app.diam_var.get() == "15.884"
    app.gender_var.set("内")
    app._set_default_diameter()
    assert app.diam_var.get() == "15.035"


def test_generate_typed_size(app):
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("M16x1")
    app._generate()
    assert app.errors == []
    assert app.prog_text.get("1.0", "end").strip()
    info = app.info_text.get("1.0", "end")
    assert "規格表の値" in info
    assert "15.2650" in info


def test_generate_approximate_note(app):
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("M50x1")
    app._generate()
    assert app.errors == []
    assert "計算式による概算" in app.info_text.get("1.0", "end")


def test_registered_size_has_no_tolerance_note(app):
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("M10x1.25")
    app._generate()
    assert app.errors == []
    assert "任意入力" not in app.info_text.get("1.0", "end")
    assert app.diam_var.get() == "9.866"


def test_invalid_size_reports_error(app):
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("abc")
    app._generate()
    assert app.errors == ["「M16x1」の形式で入力してください。"]
    assert app.prog_text.get("1.0", "end").strip() == ""


def test_edited_diameter_survives_recommit(app):
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("M16x1")
    app._commit_size()
    app.diam_var.set("15.900")
    app._commit_size()                 # フォーカス移動や生成時の再確定
    assert app.diam_var.get() == "15.900"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_metric_fine_custom.py -q`
Expected: the 7 new tests FAIL (`AttributeError: ... has no attribute '_commit_size'`, state stays `readonly`).

- [ ] **Step 3: Implement**

In `__init__`, add before `self._build_ui()`:

```python
        self._committed_size = None   # 最後にピッチ・径を反映した呼び径
```

In `_build_ui`, after the existing `self.cb_size.bind("<<ComboboxSelected>>", ...)` line add:

```python
        self.cb_size.bind("<Return>",   lambda e: self._on_size_entered(True))
        self.cb_size.bind("<FocusOut>", lambda e: self._on_size_entered(False))
```

Replace `_on_type_change` and `_on_size_change` with:

```python
    def _on_type_change(self):
        ttype = self.thread_type_var.get()
        db = THREAD_DB[ttype]
        keys = list(db.keys())

        # メートル細目だけ「M16x1」のような手入力を受け付ける
        self.cb_size.configure(state="normal" if ttype == MF_TYPE else "readonly")

        # 呼び径リスト
        names = [k[0] for k in keys]
        self.cb_size["values"] = names
        if names:
            self.cb_size.current(0)
        self._on_size_change()

    def _entries(self, ttype: str, size_name: str) -> dict:
        """size_name に該当する {(名前, ピッチ): 値} を返す。

        メートル細目で未登録の名前は、基準寸法を計算した1行を返す。
        """
        found = {k: v for k, v in THREAD_DB[ttype].items() if k[0] == size_name}
        if not found and ttype == MF_TYPE:
            try:
                name, d, pitch = parse_metric_fine(size_name)
            except ValueError:
                return {}
            found = {(name, pitch): metric_basic_dims(d, pitch)}
        return found

    def _commit_size(self):
        """メートル細目の手入力を正規化して確定する。不正な入力は ValueError。"""
        ttype = self.thread_type_var.get()
        if ttype != MF_TYPE:
            return
        text = self.size_var.get()
        if not any(k[0] == text for k in THREAD_DB[ttype]):
            self.size_var.set(parse_metric_fine(text)[0])
        if self.size_var.get() != self._committed_size:
            self._on_size_change()

    def _on_size_entered(self, show_error: bool):
        try:
            self._commit_size()
        except ValueError as e:
            if show_error:
                messagebox.showerror("入力エラー", str(e))

    def _on_size_change(self):
        ttype = self.thread_type_var.get()
        size_name = self.size_var.get()

        # そのサイズに対するピッチ候補
        pitches = [str(k[1]) for k in self._entries(ttype, size_name)]
        self.cb_pitch["values"] = pitches
        if pitches:
            self.cb_pitch.current(0)
        self._committed_size = size_name

        # 外径を自動セット
        self._set_default_diameter()
```

In `_set_default_diameter`, delete the line `db        = THREAD_DB[ttype]` and replace

```python
        for key, val in db.items():
            if key[0] != size_name:
                continue
            if cur_pitch is not None and abs(key[1] - cur_pitch) > 1e-6:
```

with

```python
        for key, val in self._entries(ttype, size_name).items():
            if cur_pitch is not None and abs(key[1] - cur_pitch) > 1e-6:
```

In `_generate`, add `self._commit_size()` as the first statement inside `try:`, and replace

```python
            db = THREAD_DB[ttype]
            key = (size_nm, pitch)
            if key not in db:
                messagebox.showerror("エラー", f"サイズ/ピッチの組み合わせ ({size_nm}, {pitch}) が見つかりません。")
                return

            d2_basic = db[key][0]   # 全DBで先頭値が基準有効径
```

with

```python
            entries = self._entries(ttype, size_nm)
            key = next((k for k in entries if abs(k[1] - pitch) < 1e-6), None)
            if key is None:
                messagebox.showerror("エラー", f"サイズ/ピッチの組み合わせ ({size_nm}, {pitch}) が見つかりません。")
                return

            d2_basic = entries[key][0]   # 全DBで先頭値が基準有効径

            # 任意入力のときは公差の出典を計算情報に表示する
            tol_note = ""
            if key not in THREAD_DB[ttype]:
                exact = _iso965_tol(_metric_d_from_name(size_nm), pitch)["exact"]
                tol_note = "公差(任意入力)     : ISO 965-1 6g/6H " + (
                    "規格表の値" if exact else "計算式による概算(規格表にない径×ピッチ)")
```

and in the `info_lines` list add `tol_note,` as the last element (after the `各パス切り込み` line).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_metric_fine_custom.py -q`
Expected: all pass.

- [ ] **Step 5: Bump version and commit**

```bash
python bump_version.py patch
git add thread_cutting.py tests/test_metric_fine_custom.py
git commit -m "v1.5.2: Accept typed metric fine thread sizes such as M16x1"
```
