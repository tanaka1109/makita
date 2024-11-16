#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import csv
import nfc
import pandas as pd
from functools import partial
from enum import Enum
import time
import numpy as np

# CSVファイルのパスを指定
USER_FILE = 'users.csv'
ITEM_FILE = 'items.csv'

#エラー状態

class ERR_CODE(Enum):
    #項目の重複
    DUPLICATE_ERR = 100
    #貸出中
    CURRENTLY_RENTING = 101
    #予約中
    CURRENTLY_RESERVING = 102
    #使用不可
    ITEM_DISABLED = 103
    #登録失敗
    REGISTER_FAILED = 104
    #ユーザ登録が確認できない
    USER_DATA_FAILED = 105
    #備品登録が確認できない
    ITEM_DATA_FAILED = 106

    #その他のエラー
    UNKNOWN_ERR = 999


#状態
DUPLICATE_ERR = -11
USER_REGISTERED =12
ITEM_REGISTERED =13
ITEM_RETURNED = 14
ITEM_RENTALED = 15
ITEM_RESERVED = 16
ITEM_CAN_RENTAL = 17
ITEM_FILE_PASS = 'items_data/'
#計測器状態
USABLE = 0
USED = 1
RESERVED = 2
ERROR = -1
#csv内のuidとの重複を確認する関数
#重複していた場合falseを返す

#個別アイテムファイルの読み出し
def get_reg_item_date(uid):
    print('read_item_data')
    file_name = ITEM_FILE_PASS+uid + '.csv'
    df =pd.read_csv(file_name,encoding='utf-8')
    return df

def check_duplicate(uid, check_csv_file_name):
    duplicate_flag = True
    check_list =pd.read_csv(check_csv_file_name)
    uid_list = check_list["uid"]
    for i in uid_list:
        if(uid == i):
            duplicate_flag = False
            break
    return duplicate_flag


# ユーザ情報を登録する関数
def register_user(uid, name,department, employee_id,phone_number):
    if(check_duplicate(uid,USER_FILE) == False):
        print("dublicate err")
        return DUPLICATE_ERR

    # CSVファイルにユーザ情報を書き込む
    with open(USER_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([uid, name,department, employee_id, phone_number])
        print('ユーザ情報を登録しました')
    return USER_REGISTERED

# 備品情報を登録する関数
def register_item(uid, name, item_id,administrator,states,note):
    if(check_duplicate(uid,ITEM_FILE) == False):
        print("dublicate err")
        return DUPLICATE_ERR

    # CSVファイルに備品情報を書き込む
    with open(ITEM_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([uid, name, item_id,administrator,states,note])
        #個別記録ファイルを生成する
        create_item_register(uid)
        print('備品情報を登録しました')
    return ITEM_REGISTERED

#予約情報を読み出す
def read_item_register(uid):
    file_name = ITEM_FILE_PASS+uid + '.csv'
    df =pd.read_csv(file_name,encoding='utf-8')
    #返却日がrental_start以降かつ貸出日がrental_end以前かつstateがRESERVEDのもののみを取り出す
    reserved_list = df[(df['state']==RESERVED) ]
    #print(reserved_list)
    rental_start = datetime.date.today()
    print("debug")
    print(pd.to_datetime(reserved_list['return_date']))
    check_list = reserved_list[(pd.to_datetime(reserved_list['return_date']).dt.date>=rental_start)]
    return check_list

#貸出、予約情報などを個別に記録する帳票を生成する
def create_item_register(uid):
    try:
        file_name = ITEM_FILE_PASS+uid + '.csv'
        with open(file_name, "x", newline='') as f:
            # 操作ユーザ、その行を追記した日時、予約or貸出開始日、返却予定日、情報（貸出、予約、返却操作）
            writer = csv.writer(f)
            writer.writerow(["user_id","record_date","start_date","return_date","state"])
            return 0
    except FileExistsError:
        print("ファイルが既に存在します。")
        return ERR_CODE.DUPLICATE_ERR
#貸出操作を行う
def write_item_rental(uid, item_tag_id,rental_start,rental_end):
    #登録済みかを確認
    #存在しない場合trueが帰ってくる
    if(check_duplicate(uid, USER_FILE)):
       print("ユーザ登録が確認できません")
       return ERR_CODE.USER_DATA_FAILED
    if(check_duplicate(item_tag_id, ITEM_FILE)):
        print("備品登録が確認できません")
        return ERR_CODE.ITEM_DATA_FAILED
    
    #重複確認を行う
    item_file_name = ITEM_FILE_PASS+item_tag_id  + '.csv'
    if(check_reserved(item_file_name,rental_start,rental_end)==False):
        print('予約期間と重複しています')
        return RESERVED
    else:
        #ITEM_FILEをdfとして読み込み
        df =get_item_list_df()
        #ステータスを確認し、貸出中か確認
        #print(df[df["uid"]==item_tag_id].states )
        if(int(df[df["uid"]==item_tag_id].states) !=USABLE):
            print("貸出できません")
            return ERR_CODE.CURRENTLY_RENTING
        else:
            #問題がなければ、ステータスを貸出中にし、個別帳票に貸出期間を追記
            df.loc[df['uid']==item_tag_id,'states']=USED
            df.to_csv(ITEM_FILE,index=False)
            file_name = ITEM_FILE_PASS+item_tag_id + '.csv'
            with open(file_name,  'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([uid, datetime.date.today(), rental_start,rental_end,USED])
            return ITEM_RENTALED

def write_item_rental2(uid, item_tag_id,rental_start):
    #登録済みかを確認
    #存在しない場合trueが帰ってくる
    if(check_duplicate(uid, USER_FILE)):
       print("ユーザ登録が確認できません")
       return ERR_CODE.USER_DATA_FAILED
    if(check_duplicate(item_tag_id, ITEM_FILE)):
        print("備品登録が確認できません")
        return ERR_CODE.ITEM_DATA_FAILED
    
    #重複確認を行う
    item_file_name = ITEM_FILE_PASS+item_tag_id  + '.csv'

    #ITEM_FILEをdfとして読み込み
    df =get_item_list_df()
    #ステータスを確認し、貸出中か確認
    #print(df[df["uid"]==item_tag_id].states )
    if(int(df[df["uid"]==item_tag_id].states) !=USABLE):
        print("貸出できません")
        return ERR_CODE.CURRENTLY_RENTING
    else:
        #問題がなければ、ステータスを貸出中にし、個別帳票に貸出期間を追記
        df.loc[df['uid']==item_tag_id,'states']=USED
        df.to_csv(ITEM_FILE,index=False)
        file_name = ITEM_FILE_PASS+item_tag_id + '.csv'
        with open(file_name,  'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([uid, datetime.date.today(), rental_start,USED])
        return ITEM_RENTALED

#貸出可能か確認する関数
def check_item_can_rental(uid, item_tag_id,rental_start,rental_end):
    #登録済みかを確認
    #存在しない場合trueが帰ってくる
    if(check_duplicate(uid, USER_FILE)):
       print("ユーザ登録が確認できません")
       return ERR_CODE.USER_DATA_FAILED
    if(check_duplicate(item_tag_id, ITEM_FILE)):
        print("備品登録が確認できません")
        return ERR_CODE.ITEM_DATA_FAILED
    
    #重複確認を行う
    item_file_name = ITEM_FILE_PASS+item_tag_id  + '.csv'
    if(check_reserved(item_file_name,rental_start,rental_end)==False):
        print('予約期間と重複しています')
        return RESERVED
    else:
        #ITEM_FILEをdfとして読み込み
        df =get_item_list_df()
        #ステータスを確認し、貸出中か確認
        #print(df[df["uid"]==item_tag_id].states )
        if(int(df[df["uid"]==item_tag_id].states) !=USABLE):
            print("貸出できません")
            return ERR_CODE.CURRENTLY_RENTING
        else:
            #貸出可能
            return ITEM_CAN_RENTAL

#アイテムリストをdfとして返す関数
def get_item_list_df():
    return pd.read_csv(ITEM_FILE,encoding='utf-8')

#登録済みユーザをdfとして返す関数
def get_user_list_df():
    return pd.read_csv(USER_FILE,encoding='utf-8')

#登録済みユーザ情報dfとして返す関数
def get_user_data(uid):
    df = pd.read_csv(USER_FILE,encoding='utf-8')
    return df[df['uid']==uid]


#予約期間と貸出期間の重複確認をおこなう 重複している場合false
def check_reserved(check_csv_file_name,rental_start,rental_end):
    
    df =pd.read_csv(check_csv_file_name,encoding='utf-8')
    #print(df.dtypes)
    #返却日がrental_start以降かつ貸出日がrental_end以前かつstateがRESERVEDのもののみを取り出す
    reserved_list = df[(df['state']==RESERVED) ]
    #print(reserved_list)
    check_list = reserved_list[(pd.to_datetime(reserved_list['return_date']).dt.date>=rental_start)&(pd.to_datetime(reserved_list['start_date']).dt.date<=rental_end)]
    #該当のものが存在する=予約期間と重複している
    if(len(check_list)==0):
        return True
    else:
        return False

#返却情報の記録を帳票に追記する
def write_item_return(uid):
    #登録済みかを確認
    #存在しない場合trueが帰ってくる

    if(check_duplicate(uid, ITEM_FILE)):
        print("備品登録が確認できません")
        return ERR_CODE.ITEM_DATA_FAILED
    
    #ITEM_FILEをdfとして読み込み
    df =pd.read_csv(ITEM_FILE,encoding='utf-8')
    #print(df)
    #ステータスを返却済みにし、個別帳票に返却操作を追記
    df.loc[df['uid']==uid,'states']=USABLE
    #print(df)
    df.to_csv(ITEM_FILE,index=False)
    file_name = ITEM_FILE_PASS+uid + '.csv'
    with open(file_name,  'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['-', datetime.date.today(), '-','-',USABLE])


    return ITEM_RETURNED


#予約操作を行う
def write_item_reserv(uid, item_tag_id,rental_start,rental_end):
    #登録済みかを確認
    #存在しない場合trueが帰ってくる
    if(check_duplicate(uid, USER_FILE)):
       print("ユーザ登録が確認できません")
       return ERR_CODE.USER_DATA_FAILED
    if(check_duplicate(item_tag_id, ITEM_FILE)):
        print("備品登録が確認できません")
        return ERR_CODE.ITEM_DATA_FAILED
    
    #重複確認を行う
    item_file_name = ITEM_FILE_PASS+item_tag_id + '.csv'
    if(check_reserved(item_file_name,rental_start,rental_end)==False):
        print('予約期間と重複しています')
        return ERR_CODE.CURRENTLY_RESERVING
    else: 
        #問題がなければ、個別帳票に予約期間を追記
        file_name = ITEM_FILE_PASS+item_tag_id + '.csv'
        with open(file_name,  'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([uid, datetime.date.today(), rental_start,rental_end,RESERVED])
        return ITEM_RENTALED


# NFCタグのUIDを読み取る関数
def read_nfc():
    with nfc.ContactlessFrontend() as clf:
        clf.open('usb:054c:06c1')
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        uid = tag.identifier.hex()

    return uid


# NFCタグのUIDを読み取る関数 + タイムアウト処理
def afrer(n, started):
    return time.time() - started > n
def read_nfc_with_timeout(timeout):
    started = time.time()
    with nfc.ContactlessFrontend() as clf:
        clf.open('usb:054c:06c1')
        tag = clf.connect(rdwr={'on-connect': lambda tag: False},
                          terminate=partial(afrer, timeout, started))
    # timeoutだとNoneが帰ってくる。
    if type(tag)==type(None):
        uid = "timeout"
    else:
        uid = tag.identifier.hex()
    #print(uid)
    #print(type(uid))
    #print("None Check : ",type(uid)==type(None))
    return uid

# ユーザ情報から氏名を取り出す関数
def get_user_name(uid):
    if(check_duplicate(uid, USER_FILE)):
        print("ユーザ登録が確認できません")
        return -1
    else:
        df =pd.read_csv(USER_FILE,encoding='utf-8')
        return df[df['uid']==uid].name.iloc[-1]

def get_user_phone_number(uid):
    if(check_duplicate(uid, USER_FILE)):
        print("ユーザ登録が確認できません")
        return -1
    else:
        df =pd.read_csv(USER_FILE,encoding='utf-8')
        return df[df['uid']==uid].phone_number.iloc[-1]
def get_user_department(uid):
    if(check_duplicate(uid, USER_FILE)):
        print("ユーザ登録が確認できません")
        return -1
    else:
        df =pd.read_csv(USER_FILE,encoding='utf-8')
        return df[df['uid']==uid].department.iloc[-1]

# メインの処理
# if __name__ == "__main__":

#     #デバッグ用にループで処理を回す
#     while(1):

#         #モード取得
#         print("******************")
#         print("モードセレクト")
#         print("1:ユーザ登録")
#         print("2:備品登録")
#         print("3:貸出")
#         print("4:返却")
#         print("5:予約")
#         print("6:終了")
#         mode = input("実行モード数値を入力：")
#         mode = int(mode)
#         #ユーザ登録
#         if(mode == 1):
#             print("社員証をタッチ") 
#             uid = read_nfc()
#             #登録済みユーザかを確認
#             if(check_duplicate(uid, USER_FILE)):
#                 #ユーザ登録を実施
#                 name = input("氏名：")
#                 employee_id = input("社員番号：")
#                 employee_id = int(employee_id)
#                 department = input("所属部署")
#                 phone_number = input("内線番号：")
#                 phone_number = int(phone_number)
#                 register_user(uid, name,department, employee_id,phone_number)
                
                
#             else:
#                 print("ユーザ登録済みです")
#         #備品登録
#         elif(mode == 2):
#             print("登録する備品タグをタッチ") 
#             uid = read_nfc()
#             #登録済み製品かを確認
#             if(check_duplicate(uid, ITEM_FILE)):
#                 #ユーザ登録を実施
#                 name = input("備品名：")
#                 item_id = input("計測器管理番号：")
#                 item_id = int(item_id)
#                 administrator= input("管理者")
#                 note = input("備考：")
#                 register_item(uid, name, item_id,administrator,USABLE,note)
                
                
#             else:
#                 print("備品登録済みです")
#         #貸出
#         elif(mode == 3):
#             print("社員証をタッチ") 
#             uid = read_nfc()
#             #rental_start_str = input("利用開始日を入力(例:2023-4-01：")
#             #rental_starttime = datetime.datetime.strptime(rental_start_str,"%Y-%m-%d")
#             #rental_start= datetime.date(rental_starttime.year, rental_starttime.month, rental_starttime.day)
#             rental_start = datetime.date.today()
#             print("貸出日")
#             print(rental_start)
#             #rental_end_str = input("返却予定日を入力(例:2023-4-01：")
#             #rental_endtime = datetime.datetime.strptime(rental_end_str,"%Y-%m-%d")
#             rental_end_str = input("何日後に返却するかを入力(例:6：")
#             rental_endtime = rental_start + datetime.timedelta(days=int(rental_end_str))
#             rental_end= datetime.date(rental_endtime.year, rental_endtime.month, rental_endtime.day)

#             print("貸出備品タグをタッチ")
#             item_tag_id = read_nfc()

#             if(write_item_rental(uid, item_tag_id,rental_start,rental_end) == ITEM_RENTALED):
#                 print("貸出完了しました")
#         #返却
#         elif(mode == 4):
            

#             print("貸出備品タグをタッチ")
#             item_tag_id = read_nfc()

#             if(write_item_return(item_tag_id) == ITEM_RETURNED):
#                 print("返却完了しました")

#         #予約
#         elif(mode == 5):
#             print("社員証をタッチ") 
#             uid = read_nfc()
#             rental_start_str = input("予約開始日を入力(例:2023-4-01：")
#             rental_starttime = datetime.datetime.strptime(rental_start_str,"%Y-%m-%d")
#             rental_start= datetime.date(rental_starttime.year, rental_starttime.month, rental_starttime.day)
#             print(rental_start)
#             rental_end_str = input("返却予定日を入力(例:2023-4-01：")
#             rental_endtime = datetime.datetime.strptime(rental_end_str,"%Y-%m-%d")
#             rental_end= datetime.date(rental_endtime.year, rental_endtime.month, rental_endtime.day)

#             print("予約備品タグをタッチ")
#             item_tag_id = read_nfc()

#             if(write_item_reserv(uid, item_tag_id,rental_start,rental_end) == ITEM_RESERVED):
#                 print("予約完了しました") 
#         #デバッグ
#         elif(mode == -1):
            
#             uid = read_nfc()
#             print(uid)

#         else:
#             print("終了")
#             break        



# #

if __name__ == "__main__":
    print("start")
    read_nfc_with_timeout(1)