import pandas as pd
import matplotlib.pyplot as plt

file_name = "test.csv"
columns_name = ["T","Timestamp","I","ID","format","D","DLC","Data0","Data1","Data2","Data3","Data4","Data5","Data6","Data7","C","Channel"]
df = pd.read_csv(file_name,names = columns_name,delim_whitespace=True)#1個以上の空白で区切る
df = df.drop(["T","I","D","C","Channel"],axis = 1)#不要な列を削除
# print(df["ID"].duplicated())
id_list = list(df.drop_duplicates("ID")["ID"])#今回流れているIDの一覧をリスト化
del id_list[0]

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
    df_temp4["temp"] = data[data_name]-data[data_name][1]
    return df_temp4["temp"]

for id_name in id_list:#全てのIDに対して解析を実施
    if id_name == "0158":#158だけは手動で解析
        df_temp = df[df["ID"] == id_name]#該当するIDがある行だけ抽出
        df_temp[id_name+"_Time_diff"] = df["Timestamp"]-df["Timestamp"][1]
        df_temp[id_name+"_car_speed"] = cal_hex2dec_2byte("Data0","Data1",df_temp)*0.01
        df_temp[id_name+"_4,5byte"] = cal_hex2dec_2byte("Data4","Data5",df_temp)*0.01
        df_temp[id_name+"_6byte"] = cal_hex2dec_1byte("Data6",df_temp)
        df_temp[id_name+"_car_speed(m)"] = df_temp[id_name+"_car_speed"] *1000/3600 *(df_temp[id_name+"_Time_diff"].diff())#前回地との差分の配列を作成
        df_temp[id_name+"_car_speed_sum"] = (df_temp[id_name+"_car_speed(m)"].cumsum())*0.1#車速情報から距離を算出
        df_temp[id_name+"_7byte_bit"] = cal_hex2bin_1byte("Data7",df_temp)
        df_temp[id_name+"_7byte_bit"].to_csv("ID158_7byte.csv")
        print(df_temp[id_name+"_car_speed"])      
        print(df_temp[id_name+"_Time_diff"])
        print(df_temp[id_name+"_car_speed(m)"])
    if id_name == "17C":


# plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_car_speed"],label="158_0,1byte")  
# plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_4,5byte"],label="158_4,5byte")
plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_6byte"],label="158_6byte",marker ="o",markersize=3 )
plt.plot(df_temp["0158"+"_Time_diff"],df_temp["0158"+"_car_speed_sum"],label="158__car_speed_sum",marker ="o",markersize=3)

plt.xlabel("時間[秒]",fontname="MS Gothic")
plt.ylabel("走行距離[100 m]",fontname="MS Gothic")

plt.legend()
plt.grid()
plt.show()


        # print(df["Speed_hex"])

        
    # print(df[df["ID"]==id_name]) 