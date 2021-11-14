import pandas as pd
import matplotlib.pyplot as plt

file_name = "test.csv"
columns_name = ["T","Timestamp","I","ID","format","D","DLC","Data0","Data1","Data2","Data3","Data4","Data5","Data6","Data7","C","Channel"]
df = pd.read_csv(file_name,names = columns_name,delim_whitespace=True)#1個以上の空白で区切る
df = df.drop(["T","I","D","C","Channel"],axis = 1)#不要な列を削除
# print(df["ID"].duplicated())
id_list = list(df.drop_duplicates("ID")["ID"])#今回流れているIDの一覧をリスト化
del id_list[0]


for id_name in id_list:#全てのIDに対して解析を実施
    if id_name == "0158":#158だけは手動で解析
        df_temp = df[df["ID"] == id_name]#該当するIDがある行だけ抽出
        df_temp[id_name+"car_speed"] = df_temp["Data0"]+df_temp["Data1"]
        df_temp["Time_diff"] = df["Timestamp"]-df["Timestamp"][1]
        df_temp[id_name+"car_speed"] = (df_temp[id_name+"car_speed"].apply(lambda x: int(x,16)))*0.01
        print(df_temp[id_name+"car_speed"])      
        print(df_temp["Time_diff"])

plt.plot(df_temp["Time_diff"],df_temp["0158"+"car_speed"])  
plt.xlabel("時間[秒]",fontname="MS Gothic")
plt.ylabel("車速[km/h]",fontname="MS Gothic")
plt.grid()
plt.show()
        # print(df["Speed_hex"])

        
    # print(df[df["ID"]==id_name]) 