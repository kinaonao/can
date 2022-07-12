
#取得したデータを解析するもの
#----------------------------------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt

file_name = "2022-07-10 21-10-04.536497.csv"
columns_name = ["T","Timestamp","I","ID","format","D","DLC","TX_RX","Data0","Data1","Data2","Data3","Data4","Data5","Data6","Data7","C","Channel","None"]#python-can 4以上はこちら(#ID4というものが一つずれるためNoneを入れてる)
# columns_name = ["T","Timestamp","I","ID","format","D","DLC","Data0","Data1","Data2","Data3","Data4","Data5","Data6","Data7","C","Channel"]#python-can3.3.4はこちら

df = pd.read_csv(file_name,names = columns_name,delim_whitespace=True,skiprows=1)#1個以上の空白で区切る
# df.to_csv("test2.csv")
df = df.drop(["T","I","D","C","Channel","None"],axis = 1)#不要な列を削除
# print(df["ID"].duplicated())
id_list = list(df.drop_duplicates("ID")["ID"])#今回流れているIDの一覧をリスト化
# print(id_list)
# del id_list[0]#当時なぜdelしたか忘れたので、コメントアウト。。。(恐らくID004を削除したかったと推定)
# print(id_list)

def cal_hex2dec_2byte(data_name1,data_name2,data):#2byteのデータを結合してデシマルに変換
    df_temp1 = pd.DataFrame()#空のデータフレームを作成
    df_temp1["temp"] = data[data_name1]+data[data_name2]
    df_temp1["temp"] = df_temp1["temp"].apply(lambda x:int(x,16))
    return df_temp1["temp"]
def cal_hex2dec_1byte(data_name1,data):#2byteのデータを結合してデシマルに変換
    df_temp2 = pd.DataFrame()#空のデータフレームを作成
    df_temp2["temp"] = data[data_name1].apply(lambda x:int(x,16))
    return df_temp2["temp"]

def cal_hex2bin_1byte(data_name,data):
    df_temp3 = pd.DataFrame()#空のデータフレームを作成
    df_temp3["temp"] = data[data_name].apply(lambda x:int(x,16))#一度10進数に変換
    df_temp3["temp"] = df_temp3["temp"].apply(lambda x:format(x,"b"))#2進数に変換
    df_temp3["temp"] = df_temp3["temp"].apply(lambda x:format(x,"0>8"))#0埋め
    return df_temp3["temp"]
def cal_time_diff(data_name,data):
    df_temp4 = pd.DataFrame()#空のデータフレームを作成
    # print(data.index)
    df_temp4["temp"] = data[data_name]-data[data_name][data.index[0]]
    return df_temp4["temp"]

for id_name in id_list:#全てのIDを解析
    if id_name == "0158":#158だけは手動で解析
        df_temp = df[df["ID"] == id_name]#該当するIDがある行だけ抽出
        # df_temp[id_name+"_Time_diff"] = df["Timestamp"]-df["Timestamp"][1]
        df_temp[id_name+"_Time_diff"] = cal_time_diff("Timestamp",df_temp)
        df_temp[id_name+"_car_speed"] = cal_hex2dec_2byte("Data0","Data1",df_temp)*0.01#車速情報（0.01km/h）
        df_temp[id_name+"_4,5byte"] = cal_hex2dec_2byte("Data4","Data5",df_temp)*0.01#車速情報（0.01km/h）
        df_temp[id_name+"_6byte"] = cal_hex2dec_1byte("Data6",df_temp)#移動距離（10m）
        df_temp[id_name+"_car_speed(m)"] = df_temp[id_name+"_car_speed"] *1000/3600 *(df_temp[id_name+"_Time_diff"].diff())#単位時間当たりに進む距離を求め、配列に格納[m/s]に変換し時間と書けてる
        df_temp[id_name+"_car_speed_sum"] = (df_temp[id_name+"_car_speed(m)"].cumsum())*0.1#車速情報配列から累積和を使って距離を算出(距離のLSBが10mなので、それと合わせるために0.1を掛ける)
        df_temp[id_name+"_7byte_bit"] = cal_hex2bin_1byte("Data7",df_temp)
        # df_temp[id_name+"_7byte_bit"].to_csv("ID158_7byte.csv")#7byte目をビットに変換しCSV出力
        # print(df_temp[id_name+"_car_speed"])      
        # print(df_temp[id_name+"_Time_diff"])
        # print(df_temp[id_name+"_car_speed(m)"])

    elif id_name == "017c":
        df_temp_17c = df[df["ID"] == id_name]#該当するIDがある行だけ抽出
        df_temp_17c[id_name+"_rpm"] = cal_hex2dec_2byte("Data2","Data3",df_temp_17c)
        df_temp_17c[id_name+"_4byte"] = cal_hex2bin_1byte("Data4",df_temp_17c)
        df_temp_17c[id_name+"_7byte"] = cal_hex2bin_1byte("Data7",df_temp_17c)
        df_temp_17c[id_name+"_Brake"] = df_temp_17c[id_name+"_4byte"].str[-1:]#ブレーキペダルON/OFF情報(7 bit)
        df_temp_17c[id_name+"_Gas_pedal"] = df_temp_17c[id_name+"_4byte"].str[:1]#アクセルON/OFF情報(0 bit目を抜き出し)
        df_temp_17c[id_name+"_Time_diff"] = cal_time_diff("Timestamp",df_temp_17c)
        df_temp_17c[id_name+"_7byte"].to_csv("ID17c_7byte.csv")

    elif id_name == "013a":
        df_temp_13a = df[df["ID"] == id_name]
        df_temp_13a[id_name+"_Gas_pedal"] = cal_hex2dec_1byte("Data1",df_temp_13a)#アクセル開度情報
        df_temp_13a[id_name+"_Time_diff"] = cal_time_diff("Timestamp",df_temp_13a)

    elif id_name == "0164":
        df_temp_164 = df[df["ID"] == id_name]
        df_temp_164[id_name+"_Time_diff"] = cal_time_diff("Timestamp",df_temp_164)
        df_temp_164[id_name+"_Fuel_Remain"] = cal_hex2dec_1byte("Data3",df_temp_164)#燃料の残量
    
    elif id_name == "0324":
        df_temp_324 = df[df["ID"] == id_name]
        df_temp_324[id_name+"_Time_diff"] = cal_time_diff("Timestamp",df_temp_324)
        df_temp_324[id_name+"_Watar_temp"] = cal_hex2dec_1byte("Data0",df_temp_324)-40#水温(51℃以上で警告灯消灯、71℃で暖気終了)
        df_temp_324[id_name+"_FI"] = cal_hex2dec_2byte("Data2","Data3",df_temp_324)*0.10886#燃料噴出量ml(積算値(エンジン停止で0))
        
    elif id_name == "0136":
        df_temp_136 = df[df["ID"] == id_name]
        df_temp_136[id_name+"_Time_diff"] = cal_time_diff("Timestamp",df_temp_136)
        df_temp_136[id_name+"_0byte"] = cal_hex2bin_1byte("Data0",df_temp_136)
        df_temp_136[id_name+"_FI_CUT"] = df_temp_136[id_name+"_0byte"].str[-2:-1]#燃料カットフラグ(1bit)
        for i in range(1000):
            print("test")


print(df_temp)
#走行距離と燃料噴出量
#----------------------------------------------------------------------------------
plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_car_speed_sum"],label="car_speed_sum",marker ="o",markersize=3)  
plt.plot(df_temp_324["0324"+"_Time_diff"],df_temp_324["0324"+"_FI"],label="Total injection Fuel",marker ="o",markersize=3)  

plt.legend()
plt.grid()
plt.show()
#----------------------------------------------------------------------------------

#ブレーキアクセルON/OFFの表示
#----------------------------------------------------------------------------------
# # plt.plot(df_temp_17c["017c"+"_Time_diff"],df_temp_17c["017c"+"_4byte"],label="17c_4byte",marker ="o",markersize=3 )

# fig = plt.figure()
# ax1 = fig.subplots()
# ax2 = ax1.twinx()
# ax1.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_car_speed"],label="158_0,1byte",marker ="o",markersize=3)
# ax2.plot(df_temp_17c["017c"+"_Time_diff"],df_temp_17c["017c"+"_Gas_pedal"],label="17c_4byte_7bit",marker ="o",markersize=3,color = "orangered")
# ax2.plot(df_temp_17c["017c"+"_Time_diff"],df_temp_17c["017c"+"_Brake"],label="17c_4byte_0bit",marker ="o",markersize=3,color = "g")

# # ax2.plot(df_temp_17c["017c"+"_Time_diff"],df_temp_17c["017c"+"_rpm"],label="17c_0,1byte",marker ="o",markersize=3,color = "r")
# ax1.set_ylabel("車速[km/h]",fontname="MS Gothic")
# # ax2.set_ylabel("エンジン回転数[rpm]",fontname="MS Gothic")
# ax2.set_ylabel("アクセル/ブレーキON OFF情報",fontname="MS Gothic")
# ax1.set_xlabel("時間[秒]",fontname="MS Gothic")

# h1, l1 = ax1.get_legend_handles_labels()
# h2, l2 = ax2.get_legend_handles_labels()
# ax1.legend(h1 + h2, l1 + l2)
# # plt.legend()
# plt.grid()
# plt.show()
#----------------------------------------------------------------------------------

#燃料の残量の表示
#----------------------------------------------------------------------------------
# plt.plot(df_temp_164["0164"+"_Time_diff"],df_temp_164["0164"+"_Fuel_Remain"],label="Fuel_Remain",marker ="o",markersize=3 )
# plt.legend()
# plt.grid()
# plt.show()
#----------------------------------------------------------------------------------

#アクセル開度の表示
#----------------------------------------------------------------------------------
# plt.plot(df_temp_17c["017c"+"_Time_diff"],df_temp_17c["017c"+"_4byte"],label="17c_4byte",marker ="o",markersize=3 )
fig = plt.figure()
ax1 = fig.subplots()
ax2 = ax1.twinx()
ax1.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_car_speed"],label="CAR_SPEED",marker ="o",markersize=3)
# ax2.plot(df_temp_136["0136"+"_Time_diff"],df_temp_136["0136"+"_FI_CUT"],label = "FI_CUT",marker ="o",markersize=3)
ax2.plot(df_temp_13a["013a"+"_Time_diff"],df_temp_13a["013a"+"_Gas_pedal"],label="GAS_PEADL",marker ="o",markersize=3,color = "orangered")
ax1.plot(df_temp_324["0324"+"_Time_diff"],df_temp_324["0324"+"_FI"],label="FI_amount",marker ="o",markersize=3)

# ax2.plot(df_temp_13a["013a"+"_Time_diff"],df_temp_17c["017c"+"_Brake"],label="17c_4byte_0bit",marker ="o",markersize=3,color = "g")

# ax2.plot(df_temp_17c["017c"+"_Time_diff"],df_temp_17c["017c"+"_rpm"],label="17c_0,1byte",marker ="o",markersize=3,color = "r")
ax1.set_ylabel("車速[km/h]",fontname="MS Gothic")
# ax2.set_ylabel("エンジン回転数[rpm]",fontname="MS Gothic")
ax2.set_ylabel("アクセル開度",fontname="MS Gothic")
ax1.set_xlabel("時間[秒]",fontname="MS Gothic")

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2)
# plt.legend()
plt.grid()
plt.show()


# plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_4,5byte"],label="158_4,5byte",marker ="o",markersize=3)



#----------------------------------------------------------------------------------

#走行距離の描画
#----------------------------------------------------------------------------------
# plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_6byte"],label="158_6byte",marker ="o",markersize=3 )
# plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_car_speed_sum"],label="158__car_speed_sum",marker ="o",markersize=3)

# plt.xlabel("時間[秒]",fontname="MS Gothic")
# plt.ylabel("走行距離[100 m]",fontname="MS Gothic")

# plt.legend()
# plt.grid()
# plt.show()
#----------------------------------------------------------------------------------


        # print(df["Speed_hex"])

        
    # print(df[df["ID"]==id_name]) 