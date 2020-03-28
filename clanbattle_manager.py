import requests
from datetime import datetime
import load_settings
import gspread
import discord
from oauth2client.service_account import ServiceAccountCredentials
from pdf2image import convert_from_bytes
import requests
from io import BytesIO


def fetch_status():
    """
    解析サイト<https://redive.estertion.win> からクラバト情報を取ってくる
    return {
        "cb_start": datetime,
        "cb_end": datetime,
        "cb_days": int
    }
    """
    # クラバト開催情報取得
    r = requests.get(
        "https://redive.estertion.win/ver_log_redive/?page=1&filter=clan_battle"
    ).json()

    # クラバト開始日取得
    cb_start = r["data"][0]["clan_battle"][0]["start"]
    cb_start = datetime.strptime(cb_start, "%Y/%m/%d %H:%M:%S")

    # クラバト終了日取得
    cb_end = r["data"][0]["clan_battle"][0]["end"]
    cb_end = datetime.strptime(cb_end, "%Y/%m/%d %H:%M:%S")

    # クラバト開催日数
    cb_days = (cb_end - cb_start).days + 1

    return {"cb_start": cb_start, "cb_end": cb_end, "cb_days": cb_days}


def get_cbday():
    """
    確認用
    bot本体では未使用
    """
    #cb_status=fetch_status()
    cb_status = {
        'cb_start': datetime.strptime('2020/02/23 5:00:00',
                                      '%Y/%m/%d %H:%M:%S'),
        'cb_end': datetime.strptime('2020/02/28 23:59:59',
                                    '%Y/%m/%d %H:%M:%S'),
        'cb_days': 6
    }
    #now_datetime=datetime.now()
    now = "2020-02-29 15:00:00"
    now_datetime = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    now_cbday = (now_datetime - cb_status["cb_start"]).days + 1

    print("現在日時：", now)
    print("開始日時：", cb_status["cb_start"])
    print("終了日時：", cb_status["cb_end"])
    print("開催期間：", cb_status["cb_days"])
    print(cb_status['cb_days'] - now_cbday)
    if now_cbday <= 0:
        print(f"クラバト開催まであと{now_cbday+1}日")
    elif now_cbday >= 1 and now_cbday <= cb_status["cb_days"]:
        print(f"クラバト開催中！　{now_cbday}/{cb_status['cb_days']}日目")
    else:
        print(f"クラバトは終了しています。{now_cbday-cb_status['cb_days']}日経過")

    #print(now_cbday)


def set_cbstatus(status):
    """
    クランバトル開催情報と日数を設定する。

    return
    ----
    return cb_is_open:bool,cb_remaining_days:int

    cb_is_open:クラバトが開催中の場合はTrueを返す
    remaining_days:当日を含めない残日数を返す（最終日は0が返される）
    now_cbday:現在の日数（開催当日は1）
    """
    # 現在日時
    now_datetime = datetime.now()
    # クラバト何日目か
    now_cbday = (now_datetime - status["cb_start"]).days + 1
    # 残り何日か（最終日は0が返される）
    remaining_days = status['cb_days'] - now_cbday

    # 1日目以上&開催日数以下の場合（開催中）
    if now_cbday >= 1 and now_cbday <= status["cb_days"]:
        return True, remaining_days, now_cbday
    # それ以外（非開催中）
    else:
        return False, remaining_days, now_cbday

def shot_capture():
    """
    スプレッドシート1枚目のキャプチャを取る。

    return
    ---
    - BytesIO(png)
    """
    r = requests.get(
        "https://docs.google.com/spreadsheets/d/10fTu0MzvI-eNysZ1FGD-dmpogBsDKb_FKjdPFuxuaEM/export?format=pdf&size=executive&portrait=false&scale=4&top_margin=0.10&bottom_margin=0.00&left_margin=0.10&right_margin=0.00&horizontal_alignment=CENTER&vertical_alignment=MIDDLE"
    )
    images = convert_from_bytes(r.content)
    f = BytesIO()
    images[0].save(f, "PNG")
    f.seek(0)
    return f




class spreadsheet:
    #def __init__(self):
    #    self._authorize()

    def _authorize(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credential = load_settings.SHEETS_CREDENTIAL
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credential, scope)
        gc = gspread.authorize(credentials)
        self.sheet = gc.open_by_url(load_settings.SPREADSHEET_URL)

    def _chk_registered_user(self, username):
        """
        ユーザーがスプレッドシートに登録されているか確認する。

        return
        -----
        - 登録済み：True
        - 未登録：False
        """
        ws = self.sheet.worksheet("main")
        result = ws.range(2, 1, ws.row_count, 1)
        #result=ws.findall(username)
        count = len([i.value for i in result if i.value == username])
        if count == 0:
            return False
        else:
            return True

    def add_user(self, username):
        """
        ユーザーをスプレッドシートに登録する。
        """
        self._authorize()
        if not self._chk_registered_user(username):
            ws = self.sheet.worksheet("main")
            cell_range = f"B{ws.row_count+1}:K{ws.row_count+1}"
            result = ws.append_row([
                username, '', '', '', '', '', '', '', '', '', '',
                f'=COUNTIF({cell_range},"3凸")+COUNTIF({cell_range},"2凸")+COUNTIF({cell_range},"1凸")+COUNTIF({cell_range},"報忘")',
                f'=COUNTIF({cell_range},"報忘")'
            ],
                                   value_input_option='USER_ENTERED')
            print("add_user", result)
            return result["updates"]["updatedColumns"]
        else:
            raise Exception("ユーザーはすでに存在します。")

    def delete_user(self, username):
        """
        ユーザーをスプレッドシートから削除する。
        """
        self._authorize()
        if self._chk_registered_user(username):
            ws = self.sheet.worksheet("main")
            result = ws.range(2, 1, ws.row_count, 1)
            user_list = [i for i in result if i.value == username]
            if len(user_list) == 1:
                result = ws.delete_row(user_list[0].row)
                print("delete_user", result)

            else:
                raise Exception("同名ユーザーが2人以上登録されています。")
        else:
            raise Exception("ユーザーが存在しません。")

    def set_attack(self, username, count, cbday):
        """
        凸登録する。
        """
        self._authorize()
        if self._chk_registered_user(username):
            ws = self.sheet.worksheet("main")
            result = ws.range(2, 1, ws.row_count, 1)
            user_list = [i for i in result if i.value == username]
            if len(user_list) == 1:
                result = ws.update_cell(user_list[0].row, cbday + 1,
                                        ["", "1凸", "2凸", "3凸"][count])
                print("set_attack", result)

            else:
                raise Exception("同名ユーザーが2人以上登録されています。")
        else:
            raise Exception("ユーザーが存在しません。")

    def clear_all_attack(self):
        self._authorize()
        ws = self.sheet.worksheet("main")
        # 1日目から10日目を削除
        self.sheet.values_clear(f"{ws.title}!B2:K{ws.row_count}")
        # メモ欄1を削除
        self.sheet.values_clear(f"{ws.title}!N2:N{ws.row_count}")





if __name__ == "__main__":
    spreadsheet = spreadsheet()
    spreadsheet.clear_all_attack()
