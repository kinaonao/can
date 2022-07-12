#TODO
#----------------------------------------------------------------------------------
#TODO IGOFF信号が一瞬しか受信できないため、信号をラッチする処理を追記
#TODO 今まではCANの情報をすべて保存するしか無かったが必要な情報だけを保存する処理を追加
#----------------------------------------------------------------------------------

#CANを受信するコード
#----------------------------------------------------------------------------------
import os
import can
import pandas as pd
import time
import datetime
import traceback

#変数定義箇所
#----------------------------------------------------------------------------------
def cal_hex2dec_2byte(data_name1, data_name2):#16進数の文字列2バイト分を受け取って、10進数に変換する関数
    data_mix = str(data_name1)+str(data_name2)
    data_int = int(data_mix,16)
    return data_int

def cal_hex2dec_1byte(data_name1):#16進数の文字列1バイト分を受け取って、10進数に変換する関数
    data_int = int(data_name1,16)
    return data_int
def cal_hex2bin_1byte(data_name):#16進数の文字列を1バイト分受け取って、2進数に変換する関数
    data_int = int(data_name,16)#受信値を一度10進数に変換
    #data_bin = bin(data_int)[2:]#受け取ったデータを10進数から2進数に変換。先頭の2文字が接頭辞なので先頭の2文字は無視
    data_bin = format(data_int,"08b")
    #print(data_bin)
    return data_bin

#----------------------------------------------------------------------------------

os.system('sudo ip link set can0 type can bitrate 500000')
os.system('sudo ifconfig can0 up')

# can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native (python canのバージョンが4以下の場合)
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native(pythoncanのバージョンが4以上の場合)

#msg = can.Message(arbitration_id=0x123, data=[0, 1, 2, 3, 4, 5, 6, 7], extended_id=False)
#ファイル出力用の初期化処理
#----------------------------------------------------------------------------------
dt_now = datetime.datetime.now()
f_name = str(dt_now)+".csv"
file = open(str(dt_now)+"log.txt","w",encoding="utf-8")
print("Start\n",file=file)
print("Start")
#----------------------------------------------------------------------------------

#変数初期化処理
#----------------------------------------------------------------------------------
df = pd.DataFrame()
loging_time = time.time()
msg = 0#初期化処理
list = []
distance_before = 0
distance = 0
gas_pedal_open = 0
water_temp = 0 
fi_total = 0
fi_diff = 0
fi_before = 0
fuel_remain = 0
fuel_economy = 0
car_speed = 0
rpm = 0
IG_OFF_FLAG = 0
IG_OFF_FLAG_RATCH = 0
#----------------------------------------------------------------------------------


while (msg != None) or (IG_OFF_FLAG_RATCH == 0):#message None or IGON
    msg = can0.recv(10.0)
    msg_list = [x.strip() for x in str(msg).split()]#空白を削除して配列に格納
    #print(msg_list)
    list.append(msg)#データ保存用に受信データをリストに格納 
    if len(msg_list) > 3:#エンジン停止後のECUスリープ前にメッセージがタイムスタンプのみ保存され、msg_list[3]の処理が要素外アクセスエラーが発生するため回避用
        if msg_list[3] == "0158":
            # car_speed = cal_hex2dec_2byte(msg_list[7],msg_list[8])*0.01 #車速情報(python-CANのバージョンが4未満)
            car_speed = cal_hex2dec_2byte(msg_list[8],msg_list[9])*0.01 #車速情報(python-CANのバージョンが4以上)
            # distance_after = cal_hex2dec_1byte(msg_list[13])*0.01#距離情報(kmに変換)(python-CANのバージョンが4未満)
            distance_after = cal_hex2dec_1byte(msg_list[14])*0.01#距離情報(kmに変換)(python-CANのバージョンが4以上)

            if ((distance_after - distance_before) >= 0 ):#カウンターが255までなので、1周する前の処理
                distance += (distance_after - distance_before)
                distance_before = distance_after
            else:
                distance += ((2.55-distance_before) + distance_after)#カウンターが255までなので、1周したあとの処理
                distance_before = distance_after

        elif msg_list[3] == "013a":
            # gas_pedal_open = cal_hex2dec_1byte(msg_list[8])#アクセル開度情報
            gas_pedal_open = cal_hex2dec_1byte(msg_list[9])#アクセル開度情報
        
        elif msg_list[3] == "0324":
            # water_temp = cal_hex2dec_1byte(msg_list[7])-40#水温情報(51℃以上で警告灯消灯、71℃で暖気終了) 
            water_temp = cal_hex2dec_1byte(msg_list[8])-40#水温情報(51℃以上で警告灯消灯、71℃で暖気終了) 
            # fi_total = cal_hex2dec_2byte(msg_list[9],msg_list[10])*0.10886#燃料噴出量積算値ml(エンジン停止で0)
            fi_total = cal_hex2dec_2byte(msg_list[10],msg_list[11])*0.10886#燃料噴出量積算値ml(エンジン停止で0)

            fi_diff = fi_total - fi_before#インジェクション噴出量の最新値と前回値の差分を格納(瞬間燃費を求める)
            fi_before = fi_total#値の更新
            ID324_6byte = cal_hex2bin_1byte(msg_list[14])
            IG_OFF_FLAG = ID324_6byte[-4]#IG2→IG1になったら1になる。(エンジンを切った後もECUのスリープ処理？でECUがデータを送り続けてしまうため、ロギング停止処理用として使用)
            if IG_OFF_FLAG == 1:
                IG_OFF_FLAG_RATCH = 1#一度でもIGOFFの信号を受信したらラッチする。
            #IG_OFF_FLAG = ID324_6byte#debag
            #print("IGOFF_FLAG")
            #print(IG_OFF_FLAG)
        elif msg_list[3] == "0164":
            # fuel_remain = cal_hex2dec_1byte(msg_list[10])
            fuel_remain = cal_hex2dec_1byte(msg_list[11])

        elif msg_list[3] == "017c":
            # rpm = cal_hex2dec_2byte(msg_list[9],msg_list[10])#回転数情報        
            rpm = cal_hex2dec_2byte(msg_list[10],msg_list[11])#回転数情報
        if (distance != 0) and (fi_total != 0):
            fuel_economy = distance/(fi_total/1000)#燃料噴出量をℓに変換したうえで燃費を求める
        print("\r car_speed: %lf [km/h] \n rpm : %lf [rpm] \n distance: %lf [km] \n gas_pedal_open: %lf [%%] \n water_temp: %lf [℃] \n fuel_remain : %lf [%%] \n FI_total: %lf [ml] \n FI_diff:%lf [ml] \n fuel_economy: %lf [km/l]  \033[8A" %(car_speed, rpm, distance, gas_pedal_open, water_temp, fuel_remain, fi_total, fi_diff, fuel_economy), end =" ")#必要な情報を表示

    else:
        print("\033[8B")#カーソルを元の位置に戻す
        print("ECU Sleep")


loging_time = time.time() -loging_time
if (msg is None) or (IG_OFF_FLAG_RATCH == 1):#メッセージが流れなくなるかエンジンが切られたらロギング終了
#if (msg is None):
    print("Logging end. File output in progress.\n",file=file)
    print("Logging end. File output in progress.")

    df=pd.DataFrame(list)
    file_out_put_time = time.time()
    df.to_csv(f_name)
    file_out_put_time = time.time() - file_out_put_time
    # print("Finish\n\n",file=file)
    print("Finish_OUTPUT_DATA\n")
    print("START_OUTPUT_LOGING_TIME")
    print("Logging time : "+str(loging_time)+"\n",file=file)
    print("File_output_time : "+str(file_out_put_time)+"\n",file=file)
    print("type:"+str(type(msg)),file=file)
    print(msg,file=file)
    print("type(str):"+str(msg),file=file)
    print(str(msg),file=file)
    IG_OFF_FLAG_RATCH = 0#念のためIG信号のラッチを解除
else:
    print("ERROR",file=file)
    print("File NOT SAVED",file=file)
    print(traceback.format_exc(),file = file)
    
    
file.close()
os.system('sudo ifconfig can0 down')
