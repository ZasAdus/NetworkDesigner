from mac import MAC as mac
import ipaddress as ip
from router import Router
from switch import Switch
from computer import Computer
from database import Database

Database.initialize()

router1 = Router(x=10, y=20)
router1.set_interface_router(1, "192.168.2.1", 30, 10)

switch1 = Switch(x=30, y=40)
switch1.set_interface_switch(1, [10, 20], 'trunk')

computer1 = Computer(x=50, y=60)
computer1.set_interface_computer("192.168.2.2", "30")

devices = Database.get_devices()
for device in devices:
    print(device)