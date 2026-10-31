"""Raspberry Pi example; replace the example sensor with real GPIO/I2C code."""

import random
import time

from python.optipus_peripheral import OptipusPeripheral


peripheral = OptipusPeripheral(
    host="127.0.0.1",  # Use the Optipus server IP for a remote Raspberry Pi.
    port=8100,
    peripheral_id="raspberry-pi-01",
    name="Greenhouse Raspberry Pi",
    request_interval=3.0,
    heartbeat_interval=15.0,
)

peripheral.resetError()  # Writes peripheral.status.errorFlag = 0.

while True:
    try:
        requested_setpoint = peripheral.read("setpoint")
        measured_temperature = 20.0 + random.random()
        peripheral.write("temperature", measured_temperature)
        peripheral.run_once({}, {"temperature": measured_temperature})
        print(f"setpoint={requested_setpoint}, temperature={measured_temperature:.2f}")
    except Exception as error:
        peripheral.setErrorCode(1)
        print(f"Optipus request failed: {error}")
    time.sleep(peripheral.request_interval)
