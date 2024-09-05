import warnings

from gpiozero import CompositeDevice, SourceMixin, OutputDevice


class ShiftRegister(SourceMixin, CompositeDevice):
    def __init__(
        self,
        data_pin,
        latch_pin,
        shift_pin,
        output_enable_pin=None,
        reset_pin=None,
        initial_value=0,
        bit_count=8,
        pin_factory=None,
    ):
        devices = {
            "data_device": OutputDevice(data_pin, pin_factory=pin_factory),
            "latch_device": OutputDevice(latch_pin, pin_factory=pin_factory),
            "shift_device": OutputDevice(shift_pin, pin_factory=pin_factory),
        }
        if output_enable_pin is not None:
            devices["output_enable_device"] = OutputDevice(
                output_enable_pin, pin_factory=pin_factory
            )
        if reset_pin is not None:
            devices["reset_device"] = OutputDevice(reset_pin, pin_factory=pin_factory)

        super().__init__(_order=devices.keys(), **devices)

        self._bit_count = bit_count
        self._value: int = 0

        self.value = initial_value

        self._has_reset = reset_pin is not None

        self._has_oe = output_enable_pin is not None
        self._output_enabled = True

        self.reset()

    @property
    def output_enabled(self) -> bool:
        return self._output_enabled

    @output_enabled.setter
    def output_enabled(self, enabled: bool) -> None:
        if not self._has_oe:
            return

        self._output_enabled = enabled
        if self._output_enabled:
            self.output_enable_device.off()
        else:
            self.output_enable_device.on()

    @property
    def bit_count(self) -> int:
        return self._bit_count

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        if (value >> self.bit_count) != 0:
            warnings.warn(
                f"Value {value} is too big to fit in {self.bit_count} bits; truncating."
            )
        self._value = value
        self._shift()
        self._show()

    def _shift(self):
        # shift data in

        for i in range(self.bit_count):
            self.data_device.value = (self.value >> i) & 1

            self.shift_device.on()
            self.shift_device.off()

        self.data_device.off()

    def _show(self):
        # cycle the output latch
        self.latch_device.on()
        self.latch_device.off()

    def reset(self):
        # reset/srclr must be high (or floating?) during normal operation
        if not self._has_reset:
            warnings.warn("No reset pin specified; not resetting.")
            return

        self.reset_device.off()
        self.reset_device.on()

        self._show()


