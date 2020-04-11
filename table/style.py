"""Common functions for achieving a consistent custom style."""


def adjust_font(widget, size=8, bold=False):
    """Adjust a widget's font."""
    font = widget.font()
    font.setPointSize(size)
    font.setBold(bold)
    widget.setFont(font)
    return widget
