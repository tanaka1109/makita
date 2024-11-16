# main.py -----------------------------------------------------------------------------------------

import fun
import nfc
import numpy    as np
import pandas   as pd
import time
import datetime
from kivy.app               import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text         import LabelBase
from kivy.core.window       import Window
from kivy.clock             import Clock
from kivy.uix.label         import Label
from kivy.uix.gridlayout    import GridLayout
from kivy.uix.button        import Button
from kivy.properties        import ListProperty
from kivy.uix.scrollview    import ScrollView
from kivy.graphics import Color, Line

# ファイル
USER_FILE = 'users.csv'
ITEM_FILE = 'items.csv'

# 日本語フォントを登録
LabelBase.register(name='NotoSans', fn_regular='C:/Users/ryuu1/python/fonts/NotoSansJP-ExtraBold.ttf')

#--------------------------------------------------------------------------------------------------
# 5秒でタイムアウト
#--------------------------------------------------------------------------------------------------
class TimedScreen(Screen):
    """各画面で一定時間後に自動でメイン画面に戻るための基底クラス"""
    def on_enter(self):
        # 5秒後にメイン画面に戻る処理をスケジュール
        self._timer = Clock.schedule_once(self.return_to_main, 5)

    def on_leave(self):
        # 画面を離れる際にタイマーをキャンセル
        if hasattr(self, '_timer'):
            self._timer.cancel()

    def return_to_main(self, *args):
        # メイン画面に戻る
        self.manager.current = 'main'

#--------------------------------------------------------------------------------------------------
# NFC処理
#--------------------------------------------------------------------------------------------------
class NFCHandler:
    def __init__(self):
        self.clf = None

    def connect_nfc(self):
        try:
            self.clf = nfc.ContactlessFrontend('usb:054c:06c1')
            return True
        except Exception as e:
            print(f"Error connecting NFC device: {e}")
            return False

    def read_tag(self):
        if self.clf is None:
            print("NFC device not connected")
            return None
        try:
            tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
            return tag.identifier.hex()
        except Exception as e:
            print(f"Error reading NFC tag: {e}")
            return None

    def close_nfc(self):
        if self.clf:
            self.clf.close()
            self.clf = None

#--------------------------------------------------------------------------------------------------
# GUI
#--------------------------------------------------------------------------------------------------
# メイン画面 (初期画面)
class MainScreen(Screen):
    Window.size = (960, 540)

    def go_to_rental_screen(self):
        self.manager.current = 'rental_uid'

    def go_to_return_screen(self):
        self.manager.current = 'return'

    def go_to_reserve_screen(self):
        self.manager.current = 'reserve_uid'

    def go_to_user_registration_screen(self):
        self.manager.current = 'user_registration'

    def go_to_item_registration_screen(self):
        self.manager.current = 'item_registration'

    def go_to_user_list_screen(self):
        self.manager.current = 'user_list'

    def go_to_item_list_screen(self):
        self.manager.current = 'item_list'

#--------------------------------------------------------------------------------------------------
# 貸出画面 (uid読み取り)
class Rental_Uid_Screen(TimedScreen):
    def on_enter(self):
        nfc_handler = NFCHandler()
        if not nfc_handler.connect_nfc():
            self.show_error("NFCデバイスの接続に失敗しました")
            return

        uid = nfc_handler.read_tag()
        if uid is None:
            self.show_error("UIDの読み取りに失敗しました")
            return

        result_screen = self.manager.get_screen('rental_iid')
        result_screen.set_uid(uid)
        
        if fun.check_user_registered(USER_FILE, uid):
            user_name = fun.get_user_name(USER_FILE, uid)
            result_screen.set_uid(user_name)
            self.manager.current = 'rental_iid'  # 次の画面に遷移
        else:
            self.show_error("ユーザが未登録です")
            self.show_back_to_main_button()  # ボタンを表示
            return

    def show_error(self, message):
        self.ids.message_label.text = message  # エラーメッセージを画面に表示

    def show_back_to_main_button(self):
        # 「メインに戻る」ボタンを表示
        self.ids.back_to_main_button.opacity = 1
        self.ids.back_to_main_button.disabled = False

    def reset_screen(self):
        # メッセージとボタンをリセット
        self.ids.message_label.text = ""
        self.ids.back_to_main_button.opacity = 0
        self.ids.back_to_main_button.disabled = True

    def go_to_main_screen(self):
        # メイン画面に戻るときにリセット処理を追加
        self.manager.current = 'main'

    def on_leave(self):
        # 画面を離れる時にリセット
        self.reset_screen()

#--------------------------------------------------------------------------------------------------
# 貸出画面 (iid読み取り)
class Rental_Iid_Screen(TimedScreen):
    def set_uid(self, uid):
        self.ids.tag_label.text = f"{uid}"

    def on_enter(self):
        nfc_handler = NFCHandler()
        if not nfc_handler.connect_nfc():
            self.show_error("NFCデバイスの接続に失敗しました")
            return

        iid = nfc_handler.read_tag()
        if iid is None:
            self.show_error("IIDの読み取りに失敗しました")
            return

        result_screen = self.manager.get_screen('rental_result')

        # UIDが設定されていない場合はエラーメッセージを表示
        if not hasattr(self, 'uid'):
            result_screen.set_message("Error: UID not set")
        else:
            rental_result = fun.handle_item_rental(USER_FILE, ITEM_FILE, self.uid, iid)
            result_screen.set_message(rental_result)

        self.manager.current = 'rental_result'

    def show_error(self, message):
        print(f"Error: {message}")
        self.ids.message_label.text = message  # エラーメッセージを画面に表示

#--------------------------------------------------------------------------------------------------
# 貸出結果画面
class RentalResultScreen(TimedScreen):
    def set_message(self, message):
        self.ids.tag_label.text = message

    def go_to_main_screen(self):
        self.manager.current = 'main'

#--------------------------------------------------------------------------------------------------
# 返却画面(iid読み取り)
class ReturnScreen(TimedScreen):
    def on_enter(self):
        nfc_handler = NFCHandler()
        if not nfc_handler.connect_nfc():
            self.show_error("NFCデバイスの接続に失敗しました")
            return

        iid = nfc_handler.read_tag()
        if iid is None:
            self.show_error("IIDの読み取りに失敗しました")
            return

        result_screen = self.manager.get_screen('return_result')
        return_result = fun.write_item_return(iid)
        result_screen.set_message(f"{return_result}")

        self.manager.current = 'return_result'

    def show_error(self, message):
        print(f"Error: {message}")
        self.ids.message_label.text = message  # エラーメッセージを画面に表示

#--------------------------------------------------------------------------------------------------
# 返却結果画面
class ReturnResultScreen(TimedScreen):
    def set_message(self, message):
        self.ids.tag_label.text = message

    def go_to_main_screen(self):
        self.manager.current = 'main'
        self.ids.tag_label.text = ""

#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# 予約画面 (uid読み取り)
class Reserve_Uid_Screen(TimedScreen):
    def on_enter(self):
        nfc_handler = NFCHandler()
        if not nfc_handler.connect_nfc():
            self.show_error("NFCデバイスの接続に失敗しました")
            return

        uid = nfc_handler.read_tag()
        if uid is None:
            self.show_error("UIDの読み取りに失敗しました")
            return

        result_screen = self.manager.get_screen('reserve_info')
        result_screen.set_uid(uid)
        
        if fun.check_user_registered(USER_FILE, uid):
            user_name = fun.get_user_name(USER_FILE, uid)
            result_screen.set_uid(user_name)
            self.manager.current = 'reserve_info'  # 次の画面に遷移
        else:
            self.show_error("ユーザが未登録です")
            self.show_back_to_main_button()  # ボタンを表示
            return

    def show_error(self, message):
        self.ids.message_label.text = message  # エラーメッセージを画面に表示

    def show_back_to_main_button(self):
        # 「メインに戻る」ボタンを表示
        self.ids.back_to_main_button.opacity = 1
        self.ids.back_to_main_button.disabled = False

    def reset_screen(self):
        # メッセージとボタンをリセット
        self.ids.message_label.text = ""
        self.ids.back_to_main_button.opacity = 0
        self.ids.back_to_main_button.disabled = True

    def go_to_main_screen(self):
        # メイン画面に戻るときにリセット処理を追加
        self.manager.current = 'main'

    def on_leave(self):
        # 画面を離れる時にリセット
        self.reset_screen()

#--------------------------------------------------------------------------------------------------
# 予約期間入力画面（カレンダー）
class Reserve_Info_Screen(TimedScreen):
    def set_uid(self, uid):
        self.ids.tag_label.text = f"{uid}"
        
    def set_message(self, message):
        self.ids.tag_label.text = message

    def go_to_main_screen(self):
        self.manager.current = 'main'
        self.ids.tag_label.text = ""

#--------------------------------------------------------------------------------------------------
# 予約結果画面
class ReserveResultScreen(TimedScreen):
    def set_message(self, message):
        self.ids.tag_label.text = message

    def go_to_main_screen(self):
        self.manager.current = 'main'
        self.ids.tag_label.text = ""

#--------------------------------------------------------------------------------------------------
# ユーザ登録画面（uid読み取り）
class UserRegistrationScreen(TimedScreen):
    def on_enter(self):
        nfc_handler = NFCHandler()
        if not nfc_handler.connect_nfc():
            self.show_error("NFCデバイスの接続に失敗しました")
            return

        uid = nfc_handler.read_tag()
        if uid is None:
            self.show_error("UIDの読み取りに失敗しました")
            return

        result_screen = self.manager.get_screen('user_registration2')
        if fun.check_user_registered(USER_FILE, uid):
            self.ids.message_label.text = "ユーザ登録済です"
            self.show_back_to_main_button()  # ボタンを表示
        else:
            result_screen.set_uid(uid)
            self.manager.current = 'user_registration2'

    def show_error(self, message):
        print(f"Error: {message}")
        self.ids.message_label.text = message

    def show_back_to_main_button(self):
        self.ids.back_to_main_button.opacity = 1
        self.ids.back_to_main_button.disabled = False

    def reset_screen(self):
        self.ids.message_label.text = '社員証をタッチしてください'
        self.ids.back_to_main_button.opacity = 0
        self.ids.back_to_main_button.disabled = True

    def go_to_main_screen(self):
        self.manager.current = 'main'

    def on_leave(self):
        self.reset_screen()
    
#--------------------------------------------------------------------------------------------------
# ユーザ登録画面2（情報入力）
class UserRegistrationScreen2(Screen):
    uid = 0

    def set_uid(self, uid):
        self.uid = uid

    def regist(self):
        if not self.all_fields_filled():
            self.ids.message_label.text = "全ての項目を入力してください"
            return

        result = fun.register_user(self.uid, self.get_name(), self.get_department(), self.get_employee_id(), self.get_phone_number())
        if result == fun.OperationResult.USER_REGISTERED:
            self.ids.message_label.text = "ユーザ登録が完了しました"
        else:
            self.ids.message_label.text = "エラーが発生しました"

    def all_fields_filled(self):
        return all([self.uid, self.get_name(), self.get_department(), self.get_employee_id(), self.get_phone_number()])

    def get_name(self):
        return self.ids.name_input.text

    def get_department(self):
        return self.ids.department_input.text

    def get_employee_id(self):
        return self.ids.employee_id_input.text

    def get_phone_number(self):
        return self.ids.phone_number_input.text

    def go_to_main_screen(self):
        self.ids.name_input.text = ""
        self.ids.department_input.text = ""
        self.ids.employee_id_input.text = ""
        self.ids.phone_number_input.text = ""
        self.ids.message_label.text = ""
        self.manager.current = 'main'

#--------------------------------------------------------------------------------------------------
# 備品登録画面（iid読み取り）
class ItemRegistrationScreen(TimedScreen):
    def on_enter(self):
        nfc_handler = NFCHandler()
        if not nfc_handler.connect_nfc():
            self.show_error("NFCデバイスの接続に失敗しました")
            return

        uid = nfc_handler.read_tag()
        if uid is None:
            self.show_error("UIDの読み取りに失敗しました")
            return

        result_screen = self.manager.get_screen('item_registration2')
        if fun.check_duplicate(uid, ITEM_FILE):
            result_screen.set_uid(uid)
            self.manager.current = 'item_registration2'
        else:
            self.ids.message_label.text = "備品登録済です"
            self.show_back_to_main_button()  # ボタンを表示

    def show_error(self, message):
        print(f"Error: {message}")
        self.ids.message_label.text = message

    def show_back_to_main_button(self):
        self.ids.back_to_main_button.opacity = 1
        self.ids.back_to_main_button.disabled = False

    def reset_screen(self):
        self.ids.message_label.text = '備品をタッチしてください'
        self.ids.back_to_main_button.opacity = 0
        self.ids.back_to_main_button.disabled = True

    def go_to_main_screen(self):
        self.manager.current = 'main'

    def on_leave(self):
        self.reset_screen()

#--------------------------------------------------------------------------------------------------
# 備品登録画面2（情報入力）
class ItemRegistrationScreen2(Screen):
    uid = 0

    def set_uid(self, uid):
        self.uid = uid

    def regist(self):
        name = self.ids.name_input.text
        item_id = self.ids.item_id_input.text
        administrator = self.ids.administrator_input.text
        note = self.ids.note_input.text

        if self.uid and name and item_id and administrator and note:
            result = fun.register_item(self.uid, name, item_id, administrator, note)
            if result == fun.OperationResult.ITEM_REGISTERED:
                self.ids.message_label.text = "備品登録が完了しました"
            else:
                self.ids.message_label.text = "エラーが発生しました"
        else:
            self.ids.message_label.text = "全ての項目を入力してください"

    def go_to_main_screen(self):
        self.ids.name_input.text = ""
        self.ids.item_id_input.text = ""
        self.ids.administrator_input.text = ""
        self.ids.note_input.text = ""
        self.ids.message_label.text = ""
        self.manager.current = 'main'

#--------------------------------------------------------------------------------------------------
# ユーザ確認画面
class UserListScreen(Screen):
    def get_user_list(self):
        users = fun.get_list(USER_FILE)
        return users

    def create_table(self, users):
        layout = GridLayout(cols=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        headers = ['UID', '名前', '所属', '従業員番号', '内線']
        for header in headers:
            label = Label(
                text=header, size_hint_y=None, height=50,
                halign='center', valign='middle',
                font_name='NotoSans',
                font_size=40
            )
            label.bind(size=label.setter('text_size'))

            def draw_lines(instance, *args):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(1, 1, 1, 1)  # 白色の線
                    Line(points=[instance.x, instance.y, instance.x + instance.width, instance.y])  # 下線
                    Line(points=[instance.x, instance.y, instance.x, instance.y + instance.height])  # 左線
                    Line(points=[instance.x, instance.y + instance.height, instance.x + instance.width, instance.y + instance.height])  # 上線
                    Line(points=[instance.x + instance.width, instance.y, instance.x + instance.width, instance.y + instance.height])  # 右線

            label.bind(size=draw_lines, pos=draw_lines)
            layout.add_widget(label)

        for user in users:
            for key in ['uid', 'name', 'department', 'employee_id', 'phone_number']:
                label = Label(
                    text=str(user.get(key, '')), size_hint_y=None, height=50,
                    halign='center', valign='middle',
                    font_name='NotoSans',
                    font_size=36
                )
                label.bind(size=label.setter('text_size'))

                def draw_lines(instance, *args):
                    instance.canvas.before.clear()
                    with instance.canvas.before:
                        Color(1, 1, 1, 1)  # 白色の線
                        Line(points=[instance.x, instance.y, instance.x + instance.width, instance.y])  # 下線
                        Line(points=[instance.x, instance.y, instance.x, instance.y + instance.height])  # 左線
                        Line(points=[instance.x, instance.y + instance.height, instance.x + instance.width, instance.y + instance.height])  # 上線
                        Line(points=[instance.x + instance.width, instance.y, instance.x + instance.width, instance.y + instance.height])  # 右線

                label.bind(size=draw_lines, pos=draw_lines)
                layout.add_widget(label)

        return layout

    def on_enter(self):
        users = self.get_user_list()
        table = self.create_table(users)
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(table)
        self.ids.user_list_container.clear_widgets()
        self.ids.user_list_container.add_widget(scroll_view)

    def go_to_main_screen(self):
        self.manager.current = 'main'

#--------------------------------------------------------------------------------------------------
# 備品確認画面
class ItemListScreen(Screen):
    def get_item_list(self):
        # items.csvを読み込み
        try:
            items_df = pd.read_csv(ITEM_FILE, encoding='utf-8')
        except Exception as e:
            print(f"Error reading {ITEM_FILE}: {e}")
            return pd.DataFrame()

        # users.csvを読み込み
        try:
            users_df = pd.read_csv(USER_FILE, encoding='utf-8')
        except Exception as e:
            print(f"Error reading {USER_FILE}: {e}")
            return pd.DataFrame()

        # 貸出状況の初期設定
        items_df['貸出状況'] = '貸出可能'
        items_df['利用者'] = '-'
        items_df['内線'] = '-'

        # 貸出中のアイテムを処理
        borrowed_items = items_df[items_df['states'] != 0]
        for _, row in borrowed_items.iterrows():
            user_data = users_df[users_df['uid'] == row['uid']]
            if not user_data.empty:
                items_df.loc[items_df['uid'] == row['uid'], '利用者'] = user_data.iloc[-1]['name']
                items_df.loc[items_df['uid'] == row['uid'], '内線'] = user_data.iloc[-1]['phone_number']
                items_df.loc[items_df['uid'] == row['uid'], '貸出状況'] = '貸出中'

        # 必要な列のみ取得してソート
        items_df = items_df[['name', '貸出状況', '利用者', '内線']].rename(columns={
            'name': '登録備品'
        })
        items_df = items_df.sort_values(by='登録備品')
        return items_df

    def create_table(self, items_df):
        layout = GridLayout(cols=4, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # ヘッダーを作成
        headers = ['登録備品', '貸出状況', '利用者', '内線']
        for header in headers:
            label = Label(
                text=header, size_hint_y=None, height=50,
                halign='center', valign='middle',
                font_name='NotoSans',
                font_size=40
            )

            # 線を描画する関数
            def draw_lines(instance, *args):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(1, 1, 1, 1)  # 白色の線
                    Line(points=[instance.x, instance.y, instance.x + instance.width, instance.y])  # 下線
                    Line(points=[instance.x, instance.y, instance.x, instance.y + instance.height])  # 左線
                    Line(points=[instance.x, instance.y + instance.height, instance.x + instance.width, instance.y + instance.height])  # 上線
                    Line(points=[instance.x + instance.width, instance.y, instance.x + instance.width, instance.y + instance.height])  # 右線

            label.bind(size=draw_lines, pos=draw_lines)
            layout.add_widget(label)

        # データ行を追加
        for _, row in items_df.iterrows():
            for cell in row:
                label = Label(
                    text=str(cell), size_hint_y=None, height=50,
                    halign='center', valign='middle',
                    font_name='NotoSans',
                    font_size=36
                )

                # 線を描画する関数
                def draw_lines(instance, *args):
                    instance.canvas.before.clear()
                    with instance.canvas.before:
                        Color(1, 1, 1, 1)  # 白色の線
                        Line(points=[instance.x, instance.y, instance.x + instance.width, instance.y])  # 下線
                        Line(points=[instance.x, instance.y, instance.x, instance.y + instance.height])  # 左線
                        Line(points=[instance.x, instance.y + instance.height, instance.x + instance.width, instance.y + instance.height])  # 上線
                        Line(points=[instance.x + instance.width, instance.y, instance.x + instance.width, instance.y + instance.height])  # 右線

                label.bind(size=draw_lines, pos=draw_lines)
                layout.add_widget(label)

        return layout

    def on_enter(self):
        items_df = self.get_item_list()
        if items_df.empty:
            print("No data available for items.")
            return
        table = self.create_table(items_df)
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(table)
        self.ids.item_list_container.clear_widgets()
        self.ids.item_list_container.add_widget(scroll_view)

    def go_to_main_screen(self):
        self.manager.current = 'main'

#--------------------------------------------------------------------------------------------------
# メインアプリケーションクラス
class NFCApp(App):
    def build(self):
        self.title = 'バッテリ管理システム'
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(Rental_Uid_Screen(name='rental_uid'))
        sm.add_widget(Rental_Iid_Screen(name='rental_iid'))
        sm.add_widget(RentalResultScreen(name='rental_result'))
        sm.add_widget(ReturnScreen(name='return'))
        sm.add_widget(ReturnResultScreen(name='return_result'))
        sm.add_widget(Reserve_Uid_Screen(name='reserve_uid'))
        sm.add_widget(Reserve_Info_Screen(name='reserve_info'))
        sm.add_widget(ReserveResultScreen(name='reserve_result'))
        sm.add_widget(UserRegistrationScreen(name='user_registration'))
        sm.add_widget(UserRegistrationScreen2(name='user_registration2'))
        sm.add_widget(ItemRegistrationScreen(name='item_registration'))
        sm.add_widget(ItemRegistrationScreen2(name='item_registration2'))
        sm.add_widget(UserListScreen(name='user_list'))
        sm.add_widget(ItemListScreen(name='item_list'))
        return sm

if __name__ == '__main__':
    NFCApp().run()