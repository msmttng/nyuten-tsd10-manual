# -*- coding: utf-8 -*-
# 入店チャイム 起動役（センサー箱・チャイム箱 共通）。Pico に main.py として保存する。
# 本体のプログラムは app.mpy。更新後の app.mpy が起動に失敗したら、自動で前の版（app_prev.mpy）に戻す。
# 起動役 版 3（2026-10-30）：TSD10版センサー箱（外部ドライバ不要）に対応した案内文に更新
# 必ず UTF-8（BOMなし）で保存すること。
import os, sys, time, machine


def _exists(fn):
    try:
        os.stat(fn)
        return True
    except OSError:
        return False


def _crash(e):
    try:
        with open("crash.txt", "w") as f:
            sys.print_exception(e, f)
    except Exception:
        pass


def _rollback():
    # 更新したばかり（まだ「正常」の印が無い）で、前の版が残っていれば戻す
    if _exists("app_ok.flag") or not _exists("app_prev.mpy"):
        return False
    if _exists("app_bad.mpy"):
        os.remove("app_bad.mpy")
    if _exists("app.mpy"):
        os.rename("app.mpy", "app_bad.mpy")
    os.rename("app_prev.mpy", "app.mpy")
    return True


# 更新の途中で電源が切れて app.mpy が無いときの立て直し
if not (_exists("app.mpy") or _exists("app.py")):
    if _exists("app_new.mpy"):
        os.rename("app_new.mpy", "app.mpy")
        print("更新の途中だったので、新しい版の適用を済ませました")
    elif _exists("app_prev.mpy"):
        os.rename("app_prev.mpy", "app.mpy")
        print("app.mpy が無かったので、前の版を使います")

try:
    if not (_exists("app.mpy") or _exists("app.py")):
        print("app.mpy がありません。Thonny の「表示」→「ファイル」で app.mpy を Pico に入れてください")
        print("（名前が sensor_app.mpy / chime_app.mpy のままなら、右クリック →「リネーム」で app.mpy に）")
        raise SystemExit
    import app
except (KeyboardInterrupt, SystemExit):
    raise
except ImportError as e:
    if _rollback():
        _crash(e)
        print("新しい版に必要なファイルが無いため（%s）、前の版に戻して再起動します" % e)
        time.sleep(5)
        machine.reset()
    # 部品ファイルが足りないときは、再起動を繰り返さずに止める（Thonny で直せるように）
    print("必要なファイルが Pico にありません:", e)
    print("wifi_secret.py（旧VL53版センサー箱なら vl53l0x.py も）が入っているか確認してください")
    raise SystemExit
except Exception as e:
    sys.print_exception(e)
    _crash(e)
    if _rollback():
        print("新しい版で起動できなかったため、前の版に戻して再起動します")
    else:
        print("エラーで止まったため、5秒後に再起動します")
    time.sleep(5)
    machine.reset()
