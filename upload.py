from selenium import webdriver
import os
import glob
import shutil
from tqdm import tqdm
import configparser

# ----------------------------------------------------
# 変数
# ----------------------------------------------------
# 設定ファイルの読み込み
conf = configparser.SafeConfigParser()
conf.read('setting.config')

# 縮小済み画像のパス
IMAGE_INP = conf['CAPTURE']['min_img_pass']
# WPログインURL
LOGIN_URL = conf['UPLOAD']['login_url']
# WPログインID
ID = conf['UPLOAD']['login_id']
# WPログインパス
PASS = conf['UPLOAD']['login_pass']
# インポート先パス
IMPORT_URL = conf['UPLOAD']['import_url']
# アップロード先画像パス
IMAGE_OUT = conf['UPLOAD']['img_up_pass']


# ----------------------------------------------------
# メイン
# ----------------------------------------------------
# プラウザ起動
driver = webdriver.Chrome('/usr/local/bin/chromedriver')
try:

    # ----------------------------------------------------
    # ログイン
    # ----------------------------------------------------

    # LOGIN_URLを開く
    driver.get(LOGIN_URL)

    # ログインID・PASS入力
    inp = driver.find_element_by_id("user_login")
    inp.clear()
    inp.send_keys(ID)
    inp = driver.find_element_by_id("user_pass")
    inp.clear()
    inp.send_keys(PASS)

    # フォーム送信
    form = driver.find_element_by_id("loginform")
    form.submit()

    # ----------------------------------------------------
    # csv送信
    # ----------------------------------------------------

    # インポートにアクセス
    driver.get(IMPORT_URL)

    # インポートファイルを選択
    inp_file = driver.find_element_by_id("upload")
    inp_file.send_keys(os.getcwd()+"/up-list.csv")

    # フォーム送信
    form = driver.find_element_by_id("import-upload-form")
    form.submit()


    # ----------------------------------------------------
    # メディアをアップロード
    # ----------------------------------------------------
    # フォルダ全てをアップロード
    for image_pass in tqdm(glob.glob(os.path.join(IMAGE_INP, "*.png"))):

        # 画像をwordpressテーマの公開ディレクトリへ移動
        shutil.copy(image_pass, IMAGE_OUT)


finally:

    driver.quit()