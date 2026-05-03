import ctypes

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
# SWP_NOSIZE|SWP_NOMOVE|SWP_NOZORDER|SWP_NOACTIVATE|SWP_FRAMECHANGED
_SWP_FLAGS = 0x0037

DWMWA_CAPTION_COLOR = 35


def apply_tool_window_style(window) -> None:
    hwnd = int(window.winId())
    user32 = ctypes.windll.user32
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ex_style = (ex_style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, _SWP_FLAGS)


def set_caption_color(window, color_hex: str = "#2B2B2B") -> None:
    """Apply DWM titlebar color. Windows 11 (build 22000+) only; silently skipped on older builds."""
    hwnd = int(window.winId())
    h = color_hex.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    colorref = r | (g << 8) | (b << 16)  # COLORREF: 0x00BBGGRR
    try:
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_CAPTION_COLOR,
            ctypes.byref(ctypes.c_uint(colorref)),
            ctypes.sizeof(ctypes.c_uint),
        )
    except OSError:
        pass
