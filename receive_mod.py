import os
import can
import pandas as pd

os.system('sudo ip link set can0 type can bitrate 500000')
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native
msg = 0#初期化処理
list = []
#msg = can.Message(arbitration_id=0x123, data=[0, 1, 2, 3, 4, 5, 6, 7], extended_id=False)

print("Start")
df = pd.DataFrame()
while msg != None:
    msg = can0.recv(10.0)
    list.append(msg) 
if msg is None:
    print("Logging end. File output in progress.")
    df=pd.DataFrame(list)
    df.to_csv("test.csv")
print("Finish")
os.system('sudo ifconfig can0 down')
