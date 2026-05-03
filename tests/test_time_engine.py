from datetime import datetime

from src.time_engine import render, remap_position, remap_run


_NOW = datetime(2026, 5, 2, 9, 7, 3)


def test_basic_substitution():
    text, _ = render("{HH}:{mm}:{ss}", _NOW)
    assert text == "09:07:03"


def test_all_variables():
    text, _ = render("{YYYY}-{MM}-{DD}", _NOW)
    assert text == "2026-05-02"


def test_ddd_is_non_empty():
    text, _ = render("{ddd}", _NOW)
    assert len(text) > 0


def test_no_variables():
    text, omap = render("hello", _NOW)
    assert text == "hello"
    assert omap == []


def test_only_variable():
    text, omap = render("{HH}", _NOW)
    assert text == "09"
    assert len(omap) == 1
    t_start, t_len, r_start, r_len = omap[0]
    assert t_start == 0
    assert t_len == 4  # len("{HH}")
    assert r_start == 0
    assert r_len == 2  # len("09")


def test_remap_position_before_token():
    # Template "{HH}:rest" — position 0 is before the token
    _, omap = render("{HH}:rest", _NOW)
    assert remap_position(0, omap) == 0


def test_remap_position_after_token():
    # Template "{HH}:rest" — position 4 (the ":") maps to rendered position 2
    _, omap = render("{HH}:rest", _NOW)
    assert remap_position(4, omap) == 2


def test_remap_position_inside_token_snaps_to_end():
    # Position 2 is inside {HH} (len=4) — should snap to r_start + r_len = 2
    _, omap = render("{HH}:rest", _NOW)
    assert remap_position(2, omap) == 2


def test_remap_run_after_variable():
    # Run at template pos 4 (":"), length 1 — maps to rendered pos 2, length 1
    _, omap = render("{HH}:{mm}", _NOW)
    r_start, r_len = remap_run(4, 1, omap)
    assert r_start == 2
    assert r_len == 1


def test_remap_run_spanning_variable():
    # Run spanning "{HH}:" (template 0..4, length 5) maps to rendered "09:" (0..2, length 3)
    _, omap = render("{HH}:rest", _NOW)
    r_start, r_len = remap_run(0, 5, omap)
    assert r_start == 0
    assert r_len == 3  # "09:" is 3 chars


def test_remap_run_zero_length():
    _, omap = render("{HH}", _NOW)
    r_start, r_len = remap_run(0, 0, omap)
    assert r_len == 0


def test_multiple_variables_order():
    text, omap = render("{YYYY}-{MM}-{DD}", _NOW)
    assert text == "2026-05-02"
    assert len(omap) == 3
    # Each variable maps correctly
    r_start, r_len = remap_run(0, 6, omap)  # "{YYYY}" len=6 → "2026" len=4
    assert r_start == 0
    assert r_len == 4


# ── New format variables ────────────────────────────────────────────────────

def test_non_padded_month_day():
    # May 3 → "5월 3일" (no zero padding)
    text, _ = render("{M}월 {D}일", _NOW)
    assert text == "5월 2일"


def test_non_padded_time():
    text, _ = render("{H}:{m}:{s}", _NOW)
    assert text == "9:7:3"


def test_two_digit_year():
    text, _ = render("{YY}", _NOW)
    assert text == "26"


def test_korean_weekday_is_single_char():
    text, _ = render("{KW}", _NOW)
    assert text in ("월", "화", "수", "목", "금", "토", "일")


def test_korean_weekday_saturday():
    # datetime(2026, 5, 2) is a Saturday
    import calendar
    now = datetime(2026, 5, 2, 9, 7, 3)
    assert now.weekday() == 5  # Saturday
    text, _ = render("{KW}", now)
    assert text == "토"


def test_kr_weekday_monday():
    # Find a Monday: 2026-05-04
    now = datetime(2026, 5, 4, 0, 0, 0)
    assert now.weekday() == 0
    text, _ = render("{KW}", now)
    assert text == "월"


def test_non_padded_no_leading_zero():
    now = datetime(2026, 1, 3, 9, 5, 7)
    text, _ = render("{M}/{D} {H}:{m}:{s}", now)
    assert text == "1/3 9:5:7"


def test_padded_still_works_alongside_non_padded():
    now = datetime(2026, 1, 3, 9, 5, 7)
    text, _ = render("{MM}/{DD} {HH}:{mm}:{ss}", now)
    assert text == "01/03 09:05:07"
