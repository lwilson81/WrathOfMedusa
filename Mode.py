from enum import Enum


# Value Meaning:
# - Even numbers: non-live
# - Odd numbers:  live
class Mode(Enum):
    ARPEGGIOS = 1
    STRUM = 3
    DANCE = 0

    @staticmethod
    def from_str(text):
        text = text.upper()
        modes = [mode for mode in dir(
            Mode) if not mode.startswith('_')]
        if text in modes:
            return getattr(Mode, text)
        return None


def getMode(value):
    for option in Mode:
        if value == option:
            return option
    return None
