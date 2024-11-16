import PySimpleGUI as sg
import mifare_read
import pandas as pd
import numpy as np
WINDOW_SIZE_V = 1920
WINDOW_SIZE_H = 1080
BUTTON_SIZE = 200
BUTTON_SIZE_SMALL = 100
BUTTON_SIZE_VERY_SMALL = 80
FONT_SIZE = 50
FONT_SIZE_SMALL = 30
#選択した日付を取得する
date = sg.Text(key='-text_date-', font=('Arial',10))
date_start = sg.Text(key='-text_date_start-', font=('Arial',10))
date_end = sg.Text(key='-text_date_end-', font=('Arial',10))

#メイン画面
def start_window():

    layout = [[sg.Button('貸出', font=('Arial',BUTTON_SIZE)), sg.Button('返却', font=('Arial',BUTTON_SIZE))],
          [sg.Button('ユーザ登録', font=('Arial',BUTTON_SIZE_SMALL)), sg.Button('備品登録', font=('Arial',BUTTON_SIZE_SMALL))],
          [sg.Button('登録済みユーザ', font=('Arial',BUTTON_SIZE_SMALL)), sg.Button('登録済み備品（貸出状況確認）', font=('Arial',50))]
          ]
    return layout

#社員証タッチ要求画面
def touch_read_id_card_window():
    layout =  [[sg.Text('社員証をタッチ', font=('Arial',FONT_SIZE) ,enable_events=True)],
                ]
    return layout

#貸出開始ウインドウ
def item_rental_start_window(user_name):
    layout =  [[sg.Text('利用者：'+ user_name, font=('Arial',FONT_SIZE))],
               [sg.Text('備品をタッチ', font=('Arial',FONT_SIZE))],
               
               [sg.Button('OK', font=('Arial',BUTTON_SIZE_SMALL))]]
    return layout

# 複数貸出ウィンドウ
def item_rental_multi_window(user_name,list_rental):
    if len(list_rental)>0:
        txt_rental = ''
        for s in list_rental:
            txt_rental += s + "\n"
        layout =  [[sg.Text('利用者：'+ user_name, font=('Arial',FONT_SIZE))],
                    [sg.Text('備品をタッチ\n\n', font=('Arial',FONT_SIZE))],
                    [sg.Text('貸出処理済み一覧', font=('Arial',FONT_SIZE))],
                    [sg.Text(txt_rental, font=('Arial',FONT_SIZE_SMALL))],
                    [sg.Button('貸出処理実施', font=('Arial',BUTTON_SIZE_SMALL))],
                    [sg.Button('キャンセル', font=('Arial',BUTTON_SIZE_SMALL))]]
    else:
        layout =  [[sg.Text('利用者：'+ user_name, font=('Arial',FONT_SIZE))],
                   [sg.Text('備品をタッチ\n\n', font=('Arial',FONT_SIZE))],
                   [sg.Button('キャンセル', font=('Arial',BUTTON_SIZE_SMALL))]]
    return layout
#返却開始ウインドウ
def item_return_start_window():
    layout =  [[sg.Text('備品をタッチ', font=('Arial',FONT_SIZE))],
                ]
    return layout

#貸出処理ウインドウ
def item_rental_result_window(register_result):
    #予約中
    if(register_result == mifare_read.RESERVED):
        layout =  [[sg.Text('予約中につき貸出できません\n(5秒後にトップページに自動遷移)', font=('Arial',FONT_SIZE))],
               [[ sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]],
               [sg.Button('貸出備品タグタッチ画面', font=('Arial',BUTTON_SIZE_SMALL))]]
    #貸出中
    elif(register_result == mifare_read.USED):
        layout =  [[sg.Text('貸出中につき貸出できません\n(5秒後にトップページに自動遷移)', font=('Arial',FONT_SIZE))],
               [[ sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]],
               [sg.Button('貸出備品タグタッチ画面', font=('Arial',BUTTON_SIZE_SMALL))]]
    #貸出完了
    elif(register_result == mifare_read.ITEM_RENTALED):
        layout =  [[sg.Text('貸出完了しました\n(5秒後にトップページに自動遷移)', font=('Arial',FONT_SIZE))],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    #例外エラー
    else:
        layout =  [[sg.Text('エラー：貸出失敗\n(5秒後にトップページに自動遷移)', font=('Arial',FONT_SIZE))],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    return layout

#複数貸出処理ウインドウ
def item_multi_rental_result_window():
    #例外エラー
    layout =  [[sg.Text('エラー：貸出失敗', font=('Arial',FONT_SIZE))],
            [[sg.Button('貸出備品タグタッチ画面', font=('Arial',BUTTON_SIZE_SMALL))]],
            [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    return layout

def item_return_result_window(return_result):
    if(return_result == mifare_read.ITEM_RETURNED):
        layout =  [[sg.Text('返却完了\n(5秒後にトップページに自動遷移)', font=('Arial',FONT_SIZE))],
               [[ sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    else:
        layout =  [[sg.Text('エラー：返却失敗\n(5秒後にトップページに自動遷移)', font=('Arial',FONT_SIZE))],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    return layout
#日付選択ウインドウ
#
def day_select_window(text,date):
    layout = [[date,
           sg.CalendarButton(text,
                format='%Y-%m-%d',
                locale='ja_JP',
                font=('Arial',10),
                close_when_date_chosen=True,
                key='-button_calendar-',
                target='-text_date-')],
          [sg.Button('OK', font=('Arial',10))],
          [sg.Exit()]]
    return layout

#貸出開始日付選択ウインドウ
#
def start_day_select_window(text,date_start):
    layout = [[date_start,
           sg.CalendarButton(text,
                format='%Y-%m-%d',
                locale='ja_JP',
                font=('Arial',10),
                close_when_date_chosen=True,
                key='-button_calendar-',
                target='-text_date_start-')],
          [sg.Button('OK', font=('Arial',10))],
          [sg.Exit()]]
    return layout

#貸出終了日付選択ウインドウ
#
def end_day_select_window(text,date_end):
    layout = [[date_end,
           sg.CalendarButton(text,
                format='%Y-%m-%d',
                locale='ja_JP',
                font=('Arial',10),
                close_when_date_chosen=True,
                key='-button_calendar-',
                target='-text_date_end-')],
          [sg.Button('OK', font=('Arial',10))],
          [sg.Exit()]]
    return layout


#予約開始ウインドウ
def item_reserve_start_window():
    layout =  [[sg.Text('備品をタッチしながらOKをクリック', font=('Arial',FONT_SIZE))],
                [sg.Button('OK', font=('Arial',BUTTON_SIZE_SMALL))]]
    return layout

#予約完了
def item_reserve_result_window(reserve_result):
    if(reserve_result == mifare_read.ITEM_RESERVED):
        layout =  [[sg.Text('予約完了', font=('Arial',FONT_SIZE))],
               [[ sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    else:
        layout =  [[sg.Text('エラー：予約失敗', font=('Arial',FONT_SIZE))],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    return layout
#ユーザ登録ウインドウ
def register_user_window():
    layout=[
        [sg.Text("以下をアルファベットで入力してOKを押してください。", font=('Arial',50))],
        # key= でイベント発生時のkeyを指定
        [sg.Text("名前　　", font=('Arial',50)), sg.Input("", key="name",size=(70,50), font=('Arial',50))],
        [sg.Text("社員番号", font=('Arial',50)), sg.Input("", key="employee_id",size=(70,50), font=('Arial',50))],
        [sg.Text("所属部署", font=('Arial',50)), sg.Input("", key="department",size=(70,50), font=('Arial',50))],
        [sg.Text("内線番号", font=('Arial',50)), sg.Input("", key="phone_number",size=(70,50), font=('Arial',50))],
        [sg.Button("OK", font=('Arial',BUTTON_SIZE_SMALL), key="ok")]]
    return layout
def register_user_finish_window(state):
    if(state==mifare_read.USER_REGISTERED):
        layout =  [[sg.Text('登録完了', font=('Arial',FONT_SIZE))],
               [[ sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    else:
        layout =  [[sg.Text('エラー：登録失敗', font=('Arial',FONT_SIZE))],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    return layout

#アイテム登録ウインドウ
def register_item_window():
    layout=[
        [sg.Text("以下を入力してOKを押してください。")],
        # key= でイベント発生時のkeyを指定
        [sg.Text("備品名　　　　", font=('Arial',50)), sg.Input(default_text="", key="name",size=(70,50), font=('Arial',50))],
        [sg.Text("計測器管理番号", font=('Arial',50)), sg.Input("", key="item_id",size=(70,50), font=('Arial',50))],
        [sg.Text("管理者　　　　", font=('Arial',50)), sg.Input("", key="administrator",size=(70,50), font=('Arial',50))],
        [sg.Text("備考　　　　　", font=('Arial',50)), sg.Input("", key="note",size=(70,50), font=('Arial',50))],
        [sg.Button("OK", key="ok")]]
    return layout

def item_register_start_window():
    layout =  [[sg.Text('備品をタッチしながらOKをクリック', font=('Arial',FONT_SIZE))],
                [sg.Button('OK', font=('Arial',BUTTON_SIZE_SMALL))]]
    return layout

def register_item_finish_window(state):
    if(state==mifare_read.ITEM_REGISTERED):
        layout =  [[sg.Text('登録完了', font=('Arial',FONT_SIZE))],
               [[ sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    else:
        layout =  [[sg.Text('エラー：登録失敗', font=('Arial',FONT_SIZE))],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    return layout

#登録済み備品情報の表示
def registered_item_list_window(destination):
    layout =  [[sg.Text('登録済み備品一覧', font=('Arial',FONT_SIZE))],
               [sg.Listbox(destination, size=(200, 10), key='ITEM_NAME',font=('Arial',20))],
               [[sg.Button('OK', font=('Arial',BUTTON_SIZE_SMALL))],[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    
    return layout

#登録済みユーザ情報の表示
def registered_user_list_window(header,destination):
    L=sg.Table(destination,headings=header,def_col_width=10,auto_size_columns=False, font=('Arial',20))
    layout =  [[sg.Text('登録済みユーザ一覧', font=('Arial',FONT_SIZE))],
               [L],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    
    return layout

#登録済み備品情報の表示
def registered_item_use_list_window(header,destination):
    L=sg.Table(destination,headings=header,def_col_width=20,auto_size_columns=False, font=('Arial',20))
    layout =  [[sg.Text('登録済み備品一覧', font=('Arial',FONT_SIZE))],
               [L],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    
    return layout

#予約備品情報の表示
def registered_item_date_window(name,header,destination):
    L=sg.Table(destination,headings=header,def_col_width=10,auto_size_columns=False, font=('Arial',20))
    layout =  [[sg.Text(name, font=('Arial',FONT_SIZE))],
               [L],
               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    
    return layout

#汎用的なメッセージ表示ウインドウ
def message_window(message):
    layout =  [[sg.Text(message, font=('Arial',FONT_SIZE))],

               [[sg.Button('トップページ', font=('Arial',BUTTON_SIZE_SMALL))]]]
    
    return layout

# メインの処理
if __name__ == "__main__":
    while(1):
        #まずはメイン画面に遷移
        window = sg.Window("貸出管理システム", start_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
        event, values = window.read()
        window.close()
        if(event == '貸出'):
            print("社員証をタッチ") 
            window = sg.Window("貸出管理システム", touch_read_id_card_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5)
            uid = mifare_read.read_nfc()
            
            print(uid)
            print(f'eventは{event}')
            print(f'valuesは{values}')
            window.close()
            #TODO 例外処理を追加
            # 返却日を入力しない
            #date_end=sg.Text(key='-text_date_end-', font=('Arial',10))
            #window = sg.Window("返却予定日を選択", end_day_select_window("返却予定日を選択してください",date_end), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            #event, values = window.read()
            #print(f'eventは{event}')
            #print(f'valuesは{values}')
            #window.close()
       
            
            rental_start = mifare_read.datetime.date.today()
            #rental_endtime = mifare_read.datetime.datetime.strptime(date_end.get(), '%Y-%m-%d')          
            #rental_end= mifare_read.datetime.date(rental_endtime.year, rental_endtime.month, rental_endtime.day)
            #print(rental_end)
            rental_end = rental_start

            window = sg.Window("貸出備品タグをタッチ", item_rental_start_window(mifare_read.get_user_name(uid)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            
            # 社員証がおしっぱだったらループ
            while True:
                event, values = window.read(timeout=5)
                print("貸出備品タグをタッチ")
                item_tag_id = mifare_read.read_nfc()

                if uid != item_tag_id:
                    break
            window.close()

            window = sg.Window("貸出備品タグをタッチ", item_rental_result_window(mifare_read.write_item_rental(uid, item_tag_id,rental_start,rental_end)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5000)
            window.close()
        
        elif(event == '返却'):
            print("返却備品タグをタッチ")
            window = sg.Window("返却備品タグをタッチ", item_return_start_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5)
            item_tag_id = mifare_read.read_nfc()
            window.close()
            window = sg.Window("返却処理結果", item_return_result_window(mifare_read.write_item_return(item_tag_id)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5000)
            window.close()
        
        elif(event == '予約'):
            print("社員証をタッチ") 
            window = sg.Window("貸出管理システム", touch_read_id_card_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5)
            uid = mifare_read.read_nfc()
            
            print(uid)
            print(f'eventは{event}')
            print(f'valuesは{values}')
            window.close()
            #TODO 例外処理を追加

            date_start=sg.Text(key='-text_date_start-', font=('Arial',10))
            window = sg.Window("予約開始日を選択", start_day_select_window("予約開始日を選択してください",date_start), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            print(f'eventは{event}')
            print(f'valuesは{values}')
            window.close()

            rental_starttime =  mifare_read.datetime.datetime.strptime(date_start.get(), '%Y-%m-%d')          
            rental_start= mifare_read.datetime.date(rental_starttime.year, rental_starttime.month, rental_starttime.day)
            print(rental_start)
            
            
            date_end = sg.Text(key='-text_date_end-', font=('Arial',10))
            window = sg.Window("返却予定日を選択", end_day_select_window("返却予定日を選択してください",date_end), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            print(f'eventは{event}')
            print(f'valuesは{values}')
            window.close()

            rental_endtime =  mifare_read.datetime.datetime.strptime(date_end.get(), '%Y-%m-%d')          
            rental_end= mifare_read.datetime.date(rental_endtime.year, rental_endtime.month, rental_endtime.day)
            print(rental_end)

            print("予約備品タグをタッチ")
            window = sg.Window("予約備品タグをタッチ", item_reserve_start_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            item_tag_id = mifare_read.read_nfc()
            window.close()

            window = sg.Window("予約処理結果", item_reserve_result_window(mifare_read.write_item_reserv(uid, item_tag_id,rental_start,rental_end)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            window.close()

        elif(event == 'ユーザ登録'):
            print("社員証をタッチ")
            window = sg.Window("ユーザ登録システム", touch_read_id_card_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5)
            uid = mifare_read.read_nfc()
            
            print(uid)
            print(f'eventは{event}')
            print(f'valuesは{values}')
            window.close()
            
            #TODO 例外処理を追加

            if(mifare_read.check_duplicate(uid, mifare_read.USER_FILE)):
                window = sg.Window("ユーザ登録システム", register_user_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                event, values = window.read()
                window.close()
                print(f'eventは{event}')
                print(f'valuesは{values}')
                name = values['name']
                employee_id = values['employee_id']
                employee_id = int(employee_id)
                department = values['department']
                phone_number = values['phone_number']
                phone_number = int(phone_number)
                
                window = sg.Window("ユーザ登録システム", register_user_finish_window(mifare_read.register_user(uid, name,department, employee_id,phone_number)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                event, values = window.read()
                window.close()
                
            else:
                window = sg.Window("ユーザ登録システム", register_user_finish_window(-1), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                event, values = window.read()
                window.close()


        elif(event == '備品登録'):
            print("登録備品タグをタッチ")
            window = sg.Window("登録備品タグをタッチ", item_register_start_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            uid = mifare_read.read_nfc()
            window.close()

            #登録済み製品かを確認
            if(mifare_read.check_duplicate(uid, mifare_read.ITEM_FILE)):
                window = sg.Window("備品登録システム", register_item_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                event, values = window.read()
                window.close()
                #登録を実施
                name = values['name']
                item_id = values['item_id']
                item_id = int(item_id)
                administrator= values['administrator']
                note = values['note']
                window = sg.Window("備品登録システム", register_item_finish_window(mifare_read.register_item(uid, name, item_id,administrator,mifare_read.USABLE,note)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                window.read()
                #event, values = window.read()
                window.close()
            else:
                print("登録済み")
                window = sg.Window("備品登録システム", register_item_finish_window(-1), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                
                event, values = window.read()
                window.close()
        elif(event == '登録済み備品（貸出状況確認）'):

            df = mifare_read.get_item_list_df()
            #df2 = df.loc[:,['name','states']]
            df['user_name']='-'
            df['phone_number']='-'
            tmp_uid=df[df['states']!=0].uid
            print(tmp_uid)
            for user in tmp_uid:
                tmp_df =mifare_read.get_reg_item_date(user)
                tmp_df2=mifare_read.get_user_data(tmp_df.iloc[-1]['user_id'])
                df.loc[df['uid'] == user,'user_name'] = tmp_df2.iloc[-1]['name']
                df.loc[df['uid'] == user,'phone_number'] = tmp_df2.iloc[-1]['phone_number']
                

            df2 = df.loc[:,['name','states','user_name','phone_number']]
            conditions = [
                df2['states'] ==1
            ]
            choices = ['貸出中']
            df2['states'] = np.select(conditions, choices, default='貸出可能')
            header_string=['登録備品', '貸出状況', '利用者', '内線番号']
            output_string = df2.values.tolist()
            window = sg.Window("貸出情報確認", registered_item_use_list_window(header_string,output_string), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            window.close()
            #window = sg.Window("貸出情報確認", registered_item_list_window(df.name), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            #event, values = window.read()
            #window.close()
            #print(df.name)
            # window = sg.Window("貸出情報確認", registered_item_list_window(df.name), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            

            # event, values = window.read()
            # window.close()
            # if event == 'OK':
            #     print({values['ITEM_NAME'][0]})
            #     uid = df[df['name']==values['ITEM_NAME'][0]].uid
            #     uid = uid.iloc[-1]
            #     print(uid)
            #     print(mifare_read.read_item_register(uid))
            #     reg_df=mifare_read.read_item_register(uid)
                
            #     #output_string='利用者名, 内線番号, 所属部署, 予約開始日, 返却予定日\n'
            #     header_string=['利用者名', '内線番号', '所属部署', '予約開始日', '返却予定日']
                
                    
            #     if(len(reg_df)==0):
            #         #TODO 例外処理
            #         print('no reserve')
                    
            #         window = sg.Window("予約はありません", message_window('予約情報はありません'), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            #         event, values = window.read()
            #         window.close()
            #     else:
            #         for item in reg_df['user_id'].values:
            #             print(item)
            #             print(mifare_read.get_user_name(item))
            #             reg_df = reg_df.replace(item,mifare_read.get_user_name(item))

            #         window = sg.Window("予約情報確認", registered_item_date_window(values['ITEM_NAME'][0],header_string,reg_df.values.tolist()), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            #         event, values = window.read()
            #         window.close()


                #print(reg_df.start_date)
                #window = sg.Window("登録済み備品", registered_item_date_window(values['ITEM_NAME'][0],output_string), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                #event, values = window.read()
                #window.close()

        elif(event == '登録済みユーザ'):
            #ユーザリストの生成
            user_df = mifare_read.get_user_list_df()
            header_string=['登録者名', '所属部署', '社員番号', '内線番号']
            output_string = user_df[['name','department','employee_id','phone_number']].values.tolist()
            #for user in zip(user_df['name'],user_df['department'],user_df['employee_id'],user_df['phone_number']):
            #    output_string
            #    output_string = output_string + str(user[0]) +', '+ str(user[1]) +', '+ str(user[2]) +', '+ str(user[3])+ '\n'
            print(output_string)
            window = sg.Window("登録済みユーザ", registered_user_list_window(header_string,output_string), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read()
            window.close()
                
                
        elif(event == '複数予約'):
            df_item_list = pd.read_csv("/home/pi/Mifare/items.csv")

            header_string=['登録者名', '所属部署', '備品名', '予約ステータス']

            window = sg.Window("貸出管理システム", touch_read_id_card_window(), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            event, values = window.read(timeout=5)
            uid = mifare_read.read_nfc()
            window.close()

            rental_start = mifare_read.datetime.date.today()
            rental_end = rental_start

            # USERが戻るまでループする。
            # 貸出するもののリストを表示する。
            # 取り消したらやっぱりやめる。
            # もし貸出失敗したらわかるように表示する。
            list_item_id = []
            list_item_name = []

            user_name = mifare_read.get_user_name(uid)
            f_loop = True
            while f_loop:


                window = sg.Window("貸出備品タグをタッチ", 
                                    item_rental_multi_window(user_name,list_item_name),
                                    size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            
                # 社員証がおしっぱだったらループ
                while True:
                    event, values = window.read(timeout=5)
                    print("貸出備品タグをタッチ")
                   
                    item_tag_id = mifare_read.read_nfc_with_timeout(timeout = 0.005)

                    if item_tag_id=="timeout":
                        # 社員証タッチ以外
                        if event == "貸出処理実施":
                            f_loop = False
                            break

                        elif event == "キャンセル":
                            f_loop = False
                            break
                        else:
                            pass

                    elif uid == item_tag_id:
                        # 社員証をリードしている。
                        pass
                    elif uid != item_tag_id:
                        # 社員証以外をリード。
                        window.close()


                        # 貸出可能かチェック

                        f_can_rental = mifare_read.check_item_can_rental(uid, item_tag_id,rental_start,rental_end)

                        if f_can_rental == mifare_read.ITEM_CAN_RENTAL:
                            # 貸出可能
                            
                            list_item_id.append(item_tag_id)
                            list_item_name.append(df_item_list[df_item_list.uid == item_tag_id].name.iloc[0])
                            window = sg.Window("貸出備品タグをタッチ", 
                                                item_rental_multi_window(user_name,list_item_name),
                                                size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                        else:
                            # 貸出不可
                            window = sg.Window("貸出備品タグをタッチ", 
                                                item_multi_rental_result_window(),
                                                size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                            event, values = window.read()

                            if event == "貸出備品タグタッチ画面":
                                window = sg.Window("貸出備品タグをタッチ", 
                                                    item_rental_multi_window(user_name,list_item_name),
                                                    size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
                            elif event == "トップページ":
                                event = "キャンセル"
                                f_loop = False
                                break
                            else:
                                pass




                        break
                    else:
                        # 想定外遷移
                        pass

                window.close()

            # ループ処理抜ける際のボタンで分岐
            if event == "貸出処理実施":
                # 一括登録
                window = sg.Window("貸出備品タグをタッチ", item_rental_result_window(mifare_read.write_item_rental(uid, item_tag_id,rental_start,rental_end)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))

            else: 
                # event == "キャンセル":
                # 何もしない。
                window = sg.Window("貸出備品タグをタッチ", item_rental_result_window(mifare_read.write_item_rental(uid, item_tag_id,rental_start,rental_end)), size=(WINDOW_SIZE_V, WINDOW_SIZE_H))
            
            event, values = window.read(timeout=5000)
            window.close()
        
        elif(event == '複数返却'):
            pass
            
            
                


        else:
            break