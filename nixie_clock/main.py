import time
import datetime
from typing import Never
from collections.abc import Iterable
from nixie_clock.shift_register import ShiftRegister

from typing import NewType

DisplayValue = NewType("DisplayValue", int)


REFRESH_RATE = 50 * 0.001


def main() -> Never:
    sr = ShiftRegister(
        bit_count=24,
        data_pin=17,
        latch_pin=23,
        shift_pin=27,
        output_enable_pin=24,
        reset_pin=22,
    )
    try:
        _main(sr)
    finally:
        sr.value = 0x0

def _main(sr: ShiftRegister) -> Never:

    # spin(sr)
    while True:
        now = datetime.datetime.now()

        if now.minute % 5 == 0 and 15 <= now.second <= 25:
            # Show date every 5 minutes between xx:xx:15 and xx:xx:40
            if now.microsecond // 500_000 == 0:
                # Also flash the date to make it easily distinguisable from the time
                sr.value = get_date()
            else:
                sr.value = get_blank()
        elif now.minute == 1 and 2 < now.second < 5:
            # Apparently it's good to exercise your tubes every now and then
            spin(sr)
        else:
            sr.value = get_time()

        time.sleep(REFRESH_RATE)


def hex_string_to_binary(hex_string: str) -> DisplayValue:
    return number_to_binary(int(hex_string, 16))


def number_to_binary(number: int) -> DisplayValue:
    """ My poorly thought out electronics for the IN-18 tubes need the digits to be put in in reverse order."""
    padded_hex = f"{number:06x}"
    return DisplayValue(int(padded_hex[::-1], 16))


def get_time() -> DisplayValue:
    now = datetime.datetime.now()
    return hex_string_to_binary(f"{now.hour:02d}{now.minute:02d}{now.second:02d}")


def get_date() -> DisplayValue:
    now = datetime.datetime.now()
    return hex_string_to_binary(f"{now.day:02d}{now.month:02d}{now.year%100:02d}")


def get_blank() -> DisplayValue:
    # Any hex digit not 0-9 will render as blank
    return number_to_binary(0xAAAAAA)


def spin(sr: ShiftRegister, steps_ms: Iterable[int] = range(20, 200, 20)) -> None:
    values = [0x111111 * i for i in range(10)]
    for step_ms in steps_ms:
        for value in values:
            sr.value = value
            time.sleep(step_ms / 1000)


if __name__ == "__main__":
    main()
