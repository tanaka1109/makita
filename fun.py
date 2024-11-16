import pandas as pd
import csv
import datetime
from enum import Enum

USER_FILE = 'users.csv'
ITEM_FILE = 'items.csv'
ITEM_FILE_PASS = 'items_data/'  # アイテムデータを保存するパス

# アイテム状態を表すEnum
class ItemState(Enum):
    USABLE = 0  # 利用可能
    USED = 1    # 使用中
    RESERVED = 2  # 予約済み
    ERROR = -1   # エラー

# エラーコードや操作結果を表すEnum
class OperationResult(Enum):
    DUPLICATE_ERR = -11  # 重複エラー
    USER_REGISTERED = 12  # ユーザー登録成功
    ITEM_REGISTERED = 13  # アイテム登録成功
    ITEM_RETURNED = 14  # アイテム返却成功
    ITEM_RENTED = 15  # アイテム貸出成功
    ITEM_RESERVED = 16  # アイテムが予約済み
    ITEM_CAN_RENT = 17  # アイテム貸出可能
    ERROR = -1  # エラー

# CSVファイルの読み込み
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()

# CSVファイルの保存
def save_csv(df, file_path):
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error saving CSV file: {e}")

# ユーザーがすでに登録されているかチェックする関数
def check_user_registered(file_path, uid):
    df = load_csv(file_path)
    return uid in df['uid'].values

# ユーザー名を取得する関数
def get_user_name(file_path, uid):
    df = load_csv(file_path)
    user = df[df['uid'] == uid]
    if not user.empty:
        return user['name'].iloc[0]
    return None

# ユーザー登録関数
def register_user(uid, name, department, employee_id, phone_number):
    if check_user_registered(USER_FILE, uid):
        return OperationResult.DUPLICATE_ERR

    try:
        with open(USER_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([uid, name, department, employee_id, phone_number])
            print('ユーザ情報を登録しました')
        return OperationResult.USER_REGISTERED
    except Exception as e:
        print(f"Error registering user: {e}")
        return OperationResult.ERROR

# アイテム登録関数
def register_item(uid, name, item_id, administrator, note):
    if not check_duplicate(uid, ITEM_FILE):
        return OperationResult.DUPLICATE_ERR

    try:
        with open(ITEM_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([uid, name, item_id, administrator, note])
            print('備品情報を登録しました')
        return OperationResult.ITEM_REGISTERED
    except Exception as e:
        print(f"Error registering item: {e}")
        return OperationResult.ERROR

# アイテムが重複していないか確認する関数
def check_duplicate(uid, check_csv_file_name):
    df = load_csv(check_csv_file_name)
    return uid not in df['uid'].values

# アイテム貸出処理
def write_item_rental(uid, iid, rental_start, rental_end):
    item_file_name = ITEM_FILE_PASS + iid + '.csv'
    if not check_reserved(item_file_name, rental_start, rental_end):
        print('予約期間と重複しています')
        return OperationResult.ITEM_RESERVED

    try:
        df = load_csv(ITEM_FILE)
        if ItemState(int(df[df["uid"] == iid].states)) != ItemState.USABLE:
            print("貸出できません")
            return OperationResult.ERROR
        df.loc[df['uid'] == iid, 'states'] = ItemState.USED.value
        save_csv(df, ITEM_FILE)
        
        with open(item_file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([uid, datetime.date.today(), rental_start, rental_end, ItemState.USED.value])
        
        return OperationResult.ITEM_RENTED
    except Exception as e:
        print(f"Error during rental: {e}")
        return OperationResult.ERROR

# アイテム返却処理
def write_item_return(uid):
    try:
        df = load_csv(ITEM_FILE)
        df.loc[df['uid'] == uid, 'states'] = ItemState.USABLE.value
        save_csv(df, ITEM_FILE)

        file_name = ITEM_FILE_PASS + uid + '.csv'
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['-', datetime.date.today(), '-', '-', ItemState.USABLE.value])
        return '返却完了'
    except Exception as e:
        print(f"Error during item return: {e}")
        return '返却エラー'

# 貸出予約が重複していないかチェックする関数
def check_reserved(check_csv_file_name, rental_start, rental_end):
    try:
        df = load_csv(check_csv_file_name)
        reserved_list = df[df['state'] == ItemState.RESERVED.value]
        overlapping_reservations = reserved_list[
            (pd.to_datetime(reserved_list['return_date']).dt.date >= rental_start) &
            (pd.to_datetime(reserved_list['start_date']).dt.date <= rental_end)
        ]
        return overlapping_reservations.empty
    except Exception as e:
        print(f"Error checking reservation: {e}")
        return False

# 登録済みユーザーのリストを取得する関数
def get_list(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8').to_dict('records')
    except Exception as e:
        print(f"Error getting list: {e}")
        return []

# アイテムリストをDataFrameとして返す関数
def get_item_list_df():
    return load_csv(ITEM_FILE)

# 個別アイテムファイルの読み出し
def get_reg_item_date(uid):
    file_name = ITEM_FILE_PASS + uid + '.csv'
    return load_csv(file_name)

# 登録済みユーザ情報をDataFrameとして返す関数
def get_user_data(uid):
    df = load_csv(USER_FILE)
    return df[df['uid'] == uid]

# 備品の貸出処理全体を管理する関数
def handle_item_rental(user_file, item_file, uid, iid):
    try:
        if check_duplicate(iid, item_file):
            return "備品が登録されていません"
        
        result = write_item_rental(uid, iid, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=7))
        if result == OperationResult.ITEM_RENTED:
            return "貸出成功"
        return "貸出できません"
    except Exception as e:
        print(f"Error handling rental: {e}")
        return "エラーが発生しました"