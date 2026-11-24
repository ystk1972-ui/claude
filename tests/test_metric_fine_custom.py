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


import tkinter as tk


@pytest.fixture(scope="module")
def _shared_app():
    # Tk ルートを何度も作り直すと Windows で断続的に失敗するため、1つを使い回す
    try:
        a = tc.ThreadCuttingApp()
    except tk.TclError:
        pytest.skip("Tk が使えない環境")
    a.withdraw()
    yield a
    a.destroy()


@pytest.fixture
def app(_shared_app, monkeypatch):
    a = _shared_app
    errors = []
    monkeypatch.setattr(tc.messagebox, "showerror", lambda title, msg: errors.append(msg))
    a.errors = errors
    a.gender_var.set("外")
    _select_type(a, "メートルねじ (M)")
    a._clear()
    return a


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


def test_m12x1_uses_11_2_to_22_4_range(app):
    # M12 は「11.2 を超え 22.4 以下」の区分 (Td2=0.118, TD2=0.160)。
    # 以前は M10x1 と同じ区分の値 (11.268 / 11.425) が登録されていた。
    d2, _d1, D1 = tc.METRIC_FINE_THREAD[("M12x1", 1.0)]
    assert tc._d2_avg(d2, 1.0, True, None, "M12x1") == pytest.approx(11.265)
    assert tc._d2_avg(d2, 1.0, False, None, "M12x1") == pytest.approx(11.430)
    assert tc._d_major_avg(12.0, 1.0, "M12x1") == pytest.approx(11.884)
    assert tc._D1_minor_avg(D1, 1.0, "M12x1") == pytest.approx(11.035)
    _select_type(app, tc.MF_TYPE)
    app.size_var.set("M12x1")
    app._generate()
    assert app.errors == []
    assert "任意入力" not in app.info_text.get("1.0", "end")   # 登録済みサイズ扱いのまま
