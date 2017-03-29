from selenium import webdriver
from PIL import Image
import glob
import os
import tinify
from tqdm import tqdm
import re
from bs4 import BeautifulSoup
import urllib.request
import time
import configparser


# -------------------------------------------------
# 変数
# -------------------------------------------------
# 設定ファイルの読み込み
conf = configparser.ConfigParser()
conf.read('setting.config')

# キーの設定
tinify.key = conf['RESIZE']['tiny_key']
# 縮小前の画像があるdir
FROM_DIR = conf['CAPTURE']['img_pass']
# 縮小後の画像を置くdir
MIN_DIR = conf['CAPTURE']['min_img_pass']
# 設定項目
INIT_ROW = list(conf['WRITE']['init_row'].split(','))
# 画像のURL
IM_ADRRESS = conf['WRITE']['up_address']
# 設定する投稿タイプ
POST_TYPE = conf['WRITE']['post_type']
POST_STATUS = conf['WRITE']['post_status']


# -------------------------------------------------
# 関数
# -------------------------------------------------
# -------------------------------------------------
# ファイル名の整形
# -------------------------------------------------

def image_name(url) :
    # URLのドメイン抽出パターン作成
    pat = r"https?://(www.)?([\w-]+).[\w.]"
    # 正規表現でマッチして抽出
    find_list = re.findall(pat, url)
    name = find_list[0][1]
    # png形式にして名前を返す
    return name + ".png"

# -------------------------------------------------
# キャプチャの作成
# -------------------------------------------------
def cap(browser, url, image_dir, file, wait) :
    # URLを開く
    browser.get(url)
    # ウィンドウサイズを設定
    browser.set_window_size(1250, 1036)
    # 読み込み待機
    time.sleep(wait)
    # スクリーンショット取得
    browser.save_screenshot(image_dir + "/" + file)

# -------------------------------------------------
# urlからtitleの取得
# -------------------------------------------------
def get_title(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string
    return title

# -------------------------------------------------
# ログの確認、書き込み
# -------------------------------------------------
def log_conf() :
    with open('list.txt','r') as in_file, open('added_list.txt','a+') as log_file:
        # log_fileのポインタを先頭に戻す
        log_file.seek(0)

        # 改行でリストへ分割。さらに左右の空白消去
        urls = list(map(str.strip,(in_file.read().strip().split("\n"))))
        logs = log_file.read().strip()

        # 初期化
        conf_urls = []
        # listがlogにあるか確認。あればスキップ
        for url in urls :
            if url not in logs :
                conf_urls.append(url)
                # ログに書き込み
                log_file.write(url + '\n')
            else :
                print("{0}はログにあるのでスキップします".format(url))

    # 確認後のものをリストを書き出し
    with open('list.txt', 'w') as in_file :
        for conf_url in conf_urls :
            in_file.write(conf_url + "\n")

# -------------------------------------------------
# カテゴリーの取得
# -------------------------------------------------s

def get_category(title) :
    category = []
    if '鍼灸' in title or '灸' in title or 'はり' in 'きゅう' in title:
        category.append('shinkyu')
    if '整骨' in title :
        category.append('seikotsu')
    if '整体' in title :
        category.append('seitai')
    if '訪問マッサージ' in title :
        category.append('houmon_masa')
    elif 'マッサージ' in title :
        category.append('masa')
    if 'リラクゼーション' in title :
        category.append('rira')
    if '介護' in title:
        category.append('kaigo')
    if '訪問看護' in title:
        category.append('hou_kan')
    if 'カイロプラクティック' in title :
        category.append('kairo')
    if 'アロマ' in title :
        category.append('aroma')
    if '接骨' in title :
        category.append('sekkotsu')
    if not category :
        category.append('other')

    conma = '"'
    result = conma + ','.join(category) + conma
    return result

# -------------------------------------------------
# タイトルの整形
# -------------------------------------------------
# seo目的でタイトルにキーワードを入れている場合に店名のみ取り出すために入力
def form_title(title) :
    print("抽出タイトル：\n",title)
    f_title = input("店名を入力してください:\n")
    return f_title

# -------------------------------------------------
# メイン
# -------------------------------------------------
# -------------------------------------------------
# キャプチャ取得
# -------------------------------------------------

# ログファイルの確認、スキップ処理
log_conf()

# URL取得(list.txt)のファイルより読み込み。履歴ファイルも読み込み。
with open('list.txt','r') as in_file:

    # 改行でリストへ分割。さらに左右の空白消去
    urls = list(map(str.strip,(in_file.read().strip().split("\n"))))

    # プラウザ起動
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    try:
        # リストからURLをひとつづつ処理
        for url in urls :
            # ドメインの一部をファイル名として設定
            file = image_name(url)
            # キャプチャ保存
            cap(driver, url,FROM_DIR, file, 2)
            print('{0}のキャプチャを保存'.format(url))
    finally:
        driver.quit()

# -------------------------------------------------
# リサイズ
# -------------------------------------------------

# 縮小切り抜
for infile in tqdm(glob.glob(os.path.join(FROM_DIR, "*.png"))):
    # 画像サイズ変更
    im = Image.open(infile)
    im.crop((0, 0, 590, 335))
    im.thumbnail((600,600), Image.ANTIALIAS)
    #スクロールバーの切り抜き
    im = im.crop((0, 0, 590, 335))
    im.save(os.path.join(MIN_DIR, os.path.basename(infile)))

# 無劣化圧縮
for infile in tqdm(glob.glob(os.path.join(MIN_DIR, "*.png"))):
    # tinypngに接続して圧縮
    op = tinify.from_file(infile)
    op.to_file(os.path.join(MIN_DIR, os.path.basename(infile)))


# -------------------------------------------------
# csv書き込み
# -------------------------------------------------

with open('list.txt',mode='r') as inp_f, open('up-list.csv',mode='w') as out_f :
    # 設定行の書き込み
    out_f.write(",".join(INIT_ROW))
    out_f.write("\n")

    # list.txtからurlを取得して一つづつ設定
    for line in tqdm(inp_f) :
        #初期化
        set_row = []
        url = line.strip()

        #タイトル行の追加
        title = get_title(url)
        f_title = form_title(title)
        set_row.append(f_title)

        #カテゴリーの追加
        category = get_category(title)
        set_row.append(category)

        #画像アドレスの追加
        img_name = image_name(url)
        set_row.append(IM_ADRRESS + img_name)

        #URL行の追加
        set_row.append(url)

        #投稿タイプの設定
        set_row.append(POST_TYPE)

        #投稿ステータスの設定
        set_row.append(POST_STATUS)

        #辞書を結合して書き出し
        out_f.write(','.join(set_row))
        out_f.write("\n")