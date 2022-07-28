
def onBluetoothData(cbk) -> None:
  from PicoBLE import IOBluetooth
  from scheduler import loop
  bluetooth = IOBluetooth()
  loop.register(bluetooth, cbk)
