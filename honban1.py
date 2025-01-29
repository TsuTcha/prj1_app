from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import gspread
import random
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime
import time
import pandas as pd
import copy

# Google Driveの認証設定
scopes = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

json_keyfile_dict = st.secrets["service_account"]

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json_keyfile_dict, 
    scopes
)

gauth = GoogleAuth()
gauth.credentials = credentials
drive = GoogleDrive(gauth)

st.session_state.query_params = st.query_params
st.session_state.file_name = st.session_state.query_params.get("user_id")
 #st.session_state.file_name = "test"

st.session_state.custom_css = """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Rerunボタンだけを表示 */
    #MainMenu {visibility: visible;}
    </style>
    """

# 初期状態を設定
if "page" not in st.session_state:
    st.session_state.page = "home"

# ボタンを押すと状態を変更し再レンダリング
def go_to_page(page_name):
    st.session_state.page = page_name
    time.sleep(0.5)
    st.rerun()

# ページごとのコンテンツを表示
if st.session_state.page == "home":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "agreement" not in st.session_state:
        st.session_state.agreement = False
        st.session_state.agreement_check = False
        st.session_state.form_submitted = 0

    st.markdown('# ユーザアンケート トップページ')

    st.markdown('この度は、調査にご協力いただき誠にありがとうございます。 <br> 以下の指示に従って、順番にタスクを行ってください。', unsafe_allow_html=True)

    st.markdown('1. 以下の同意書をお読みになり、必要事項を記入して提出ボタンを押してください。', unsafe_allow_html=True)

    form = st.form(key="research_form")

    with form:
        st.markdown("## 研究へのご協力のお願い", unsafe_allow_html=True)

        st.markdown(""" この文書は、あなたにご協力いただきたい研究の内容について説明したものです。この文書をよく読み、この研究に参加いただけるかどうかを検討してください。<br>
                    もし、お分かりになりにくいことがありましたら、遠慮なく連絡先までお問い合わせください。<br>""", unsafe_allow_html=True)
        
        st.markdown("#### 1. この研究の概要 ", unsafe_allow_html=True)

        st.markdown("###### 研究課題", unsafe_allow_html=True)

        st.markdown("""「人間の仮説に対してフィードバックを与える機械学習モデルが意思決定へ与える影響の調査」<br>
                    研究責任者氏名・所属・職名 <br> ・馬場 雪乃（東京大学大学院総合文化研究科・広域科学専攻・准教授）<br>
                    研究実施者氏名・所属・職名 <br> ・土屋 祐太（東京大学大学院総合文化研究科・広域科学専攻・博士課程学生）<br> """, unsafe_allow_html=True)

        st.markdown("###### 研究の目的・意義", unsafe_allow_html=True)

        st.markdown("""本研究の目的は、人間がAIと協力して意思決定を行う際に、AIから情報が提示されるタイミングやその内容が、
                    意思決定の精度や負荷にどのような影響を与えるかを調査することです。<br> """, unsafe_allow_html=True)
        
        st.markdown("###### 研究の方法", unsafe_allow_html=True)

        st.markdown("""本研究の実験は、クラウドソーシングプラットフォームからアプリケーションおよび回答フォームへアクセスして行います。
                    そのため、オンライン上で完結し、自宅など任意のインターネット接続環境で回答可能です。<br><br>
                    具体的に、以下の手順で取り組みます。<br>
                    1. AIのサポートを受けながら生徒のプロフィール情報(学習状況や家庭環境など)をもとに数学の成績を予測する意思決定課題に取り組みます。<br>
                    ※課題に対する特別な事前知識は必要ありません。1つの課題につき30秒程度、合計20問に取り組みます。<br>
                    ※各課題では、割り当てられたグループごとに異なる方法で、AIから提示される情報を参考にしながら回答します。<br>
                    2. すべての課題の終了後、AIの意思決定支援についての評価アンケートを行います。評価は7段階の尺度と自由記述で行います。<br><br>
                    実験の所要時間は約30分を予定しています。収集したデータは統計的に分析されます。個人を特定できる情報は収集しません。<br><br>""", unsafe_allow_html=True)        

        st.markdown("#### ２．研究協力の任意性と撤回の自由", unsafe_allow_html=True)

        st.markdown("""この研究にご協力いただくかどうかは、あなたの自由意思に委ねられています。回答中に取りやめることも可能です。
                    その場合は、途中までの回答は破棄され、研究に用いられることはありません。<br><br>
                    一旦ご同意いただいて実験を完了した後、もし同意を撤回される場合は「同意撤回書」に日付とIDを記載してご提出ください。
                    なお、研究にご協力いただけないことで、あなたの不利益に繋がることは一切ありません。
                    同意を撤回された場合には、提供いただいたアンケート回答は破棄され、以後研究に用いられることはありません。
                    ただし、本実験の内容が論文として出版された後には、同意を撤回しても、アンケート回答を破棄することができませんのでご理解ください。<br><br>
                    """, unsafe_allow_html=True)        

        st.markdown("#### ３．個人情報の保護", unsafe_allow_html=True)

        st.markdown("""研究にあたってはあなたに不利益が生じないように個人情報の保護、プライバシーの尊重に努力し最大限の注意を払います。
                    アンケートにおいて、あなたの年齢や性別などを聞きますが、この情報は、実験参加者の統計情報として用いるものです。
                    あなたの回答内容と紐づけられることはありません。<br><br>
                    """, unsafe_allow_html=True)    

        st.markdown("#### ４．研究成果の発表", unsafe_allow_html=True)

        st.markdown("""研究の成果は、氏名など個人が特定できないようにした上で、学会発表、学術雑誌及びホームページ等で公表します。<br><br>
                    """, unsafe_allow_html=True)    

        st.markdown("#### ５．研究参加者にもたらされる利益及びリスク・不利益  研究参加者への利益", unsafe_allow_html=True)

        st.markdown("""この研究が、あなたや社会に即座に有益な情報をもたらす可能性は、現在のところ低いと考えられます。
                    しかしながら、この研究の成果は、今後のAI研究の発展に重要な基礎的成果となることが期待されています。<br><br>
                    """, unsafe_allow_html=True)   
 
        st.markdown("###### 研究参加者へのリスク・不利益", unsafe_allow_html=True)

        st.markdown("""本研究は、身体的侵襲や精神的侵襲を伴いません。実験で用いる課題は、日常生活に影響を及ぼす可能性は低いです。
                    万が一、課題の内容が不快に感じられる場合は、回答を止めることが可能です。<br><br> """, unsafe_allow_html=True)

        st.markdown("#### ６．データの取扱方針", unsafe_allow_html=True)

        st.markdown("""あなたからいただいた匿名の回答データは、研究や分析等に用います。また、東京大学総合文化研究科馬場研究室において、
                    この研究成果の発表後少なくとも10年間保存いたします。<br><br>
                    """, unsafe_allow_html=True) 

        st.markdown("#### ７．謝礼の有無", unsafe_allow_html=True)

        st.markdown("""本研究に参加いただいた方には、謝礼として500円をクラウドソーシングプラットフォームを通してお支払いいたします。<br><br>
                    """, unsafe_allow_html=True) 

        st.markdown("#### ８．その他", unsafe_allow_html=True)

        st.markdown("""ご意見、ご質問などがございましたら、お気軽に下記までお寄せください。<br><br>
                    """, unsafe_allow_html=True)  

        st.markdown("###### 連絡先", unsafe_allow_html=True)

        st.markdown("""研究責任者<br>東京大学大学院総合文化研究科・広域科学専攻・准教授<br>馬場 雪乃<br>Mail: yukino-baba@g.ecc.u-tokyo.ac.jp<br>
                    研究実施者<br>東京大学大学院総合文化研究科・広域科学専攻・博士課程学生<br>土屋 祐太<br>Mail: ytsuchi28054@g.ecc.u-tokyo.ac.jp<br> """, unsafe_allow_html=True) 

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("上記の「研究へのご協力のお願い」をお読みになりましたか。", unsafe_allow_html=True)

        submitted = st.form_submit_button(label="はい、読みました。")
    
    if submitted:
        st.session_state.agreement_check = True

    if st.session_state.agreement_check == True:

        agreement_form = st.form(key="research_agreement_form")

        with agreement_form:
            st.markdown("###### 研究参加同意書", unsafe_allow_html=True)

            st.markdown("""東京大学大学院総合文化研究科・広域科学専攻・准教授<br>
                        馬場 雪乃 殿<br>
                        研究課題「人間の仮説に対してフィードバックを与える機械学習モデルが意思決定へ与える影響の調査」<br><br>
                        私は、上記研究への参加にあたり、「研究へのご協力のお願い」の記載事項について説明を受け、これを十分理解しましたので、本研究の研究参加者となることに同意いたします。<br>
                        以下の項目について、説明を受け理解しました。""", unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.checkbox('この研究の概要について理解しました。'):
                st.session_state.form_submitted += 1
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('研究協力の任意性と撤回の自由について理解しました。'):
                st.session_state.form_submitted += 1     
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('個人情報の保護について理解しました。'):
                st.session_state.form_submitted += 1       
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('研究結果の発表について理解しました。'):
                st.session_state.form_submitted += 1
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('研究参加者にもたらされる利益及びリスク・不利益について理解しました。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)
           
            if st.checkbox('情報の取扱方針について理解しました。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('謝礼について理解しました。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('2025年1月28日に行った「【研究アンケート調査】AIのヒントを参考にして問題を解く」には参加していません。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)

            selected_date = st.date_input(
                "日付を入力してください。", 
                value=datetime.now().date()  # 初期値を今日の日付に設定
            )
            user_id = st.text_input("ユーザ名を入力してください。")

            submitted_form = st.form_submit_button(label="提出します。")

        if submitted_form:
            if not user_id.strip():
                st.error("ユーザ名は空白にできません。適切な値を入力してください。")
            elif st.session_state.form_submitted < 8:
                st.error("全ての同意事項にチェックを入れてください。")
            else:
                #st.session_state.form_submitted = True

                #if st.session_state.form_submitted == True:
                    # クエリパラメータを取得
                    #query_params = st.experimental_get_query_params()

                    # パラメータの利用
                    #user_id = query_params.get("user_id")[0]

                max_retries=3

                retries = 0
                while retries <= max_retries:
                    try:

                        st.markdown("同意書を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)

                        f = drive.CreateFile({
                            'title': st.session_state.file_name,
                            'mimeType': 'application/vnd.google-apps.spreadsheet',
                            "parents": [{"id": st.secrets["folder_id"]}]
                        })
                        f.Upload()

                        st.session_state.file = f

                        # gspread用に認証
                        gc = gspread.authorize(credentials)

                        # スプレッドシートのIDを指定してワークブックを選択
                        workbook = gc.open_by_key(st.session_state.file['id'])
                        worksheet = workbook.sheet1

                        cell_list = worksheet.range(1, 1, 1, 9)
                        cell_list[0].value = 'この研究の概要について理解しました。'
                        cell_list[1].value = '研究協力の任意性と撤回の自由について理解しました。'
                        cell_list[2].value = '個人情報の保護について理解しました。'
                        cell_list[3].value = '研究結果の発表について理解しました。'
                        cell_list[4].value = '研究参加者にもたらされる利益及びリスク・不利益について理解しました。'
                        cell_list[5].value = '情報の取扱方針について理解しました。'
                        cell_list[6].value = '謝礼について理解しました。'
                        cell_list[7].value = str(selected_date)
                        cell_list[8].value = str(user_id)

                        # スプレッドシートを更新
                        worksheet.update_cells(cell_list)

                        st.session_state.agreement = True
                        retries += 5

                    except Exception as e:
                        st.error(f"しばらくお待ちください...")
                        if retries == max_retries:
                            st.error(f"申し訳ありませんが、同意書の提出がうまくいきませんでした。リロードして再度お試しいただけますと幸いです。")

                    # 再トライ準備
                    retries += 1

    if st.session_state.agreement == True:
        st.success("同意書の提出が完了しました！「次のページへ」をクリックしてください。")
        st.markdown("<hr>", unsafe_allow_html=True)

        st.session_state.page = "task1"

        if st.button("次のページへ"):
            if st.session_state.agreement == False:
                st.error("同意書に回答してください。提出がうまくいっていない場合は、申し訳ありませんがリロードして再度お試しください。")
            else:
                time.sleep(0.2)
                #go_to_page("task1")

    st.markdown("<hr>", unsafe_allow_html=True)

elif st.session_state.page == "task1":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked" not in st.session_state:
        st.session_state.start_button_clicked = False

    if st.button("ボタンを押してください"):
        st.session_state.start_button_clicked = True

    if st.session_state.start_button_clicked:
        st.markdown("同意書へのご回答ありがとうございました。これからタスクを開始します。<br>タスクは練習と本番に分けて、合計20問行います。また、最後に自由記述を含むアンケートへの回答もお願いします。所用時間は30分程度を見込んでいます。", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('# タスクの概要説明')

        st.markdown('## 概要')

        st.markdown("""
                    この調査では、ポルトガルの中学校における生徒のプロフィール情報をもとに、AIと協力して数学の成績を当てるタスクを行っていただきます。<br><br>
                    それぞれのページで「問題スタート」ボタンをクリックすると、対象となる生徒のプロフィールが表示されます。
                    まずは、AIの助けを借りずに自力で成績を予想しましょう。
                    なお、成績は「平均より優れている」または「平均以下」の２つから選びます。
                    成績の予想ができたら、該当する成績のボタンを選んで、「AIの予想を見る」ボタンを押してください。
                    すると、AIの予測が表示されます。
                    ただし、AIの予想は必ずしも正しいわけではありません。<br><br>
                    プロフィール情報とAIの予想を考慮して、この生徒の数学の成績を改めて予想しましょう。<br>
                    成績の予想ができたら、該当する成績のボタンを選んで、最後に提出ボタンを押してください。<br><br>

                    練習を5問、本番を15問、合計20問に挑戦していただきます。<br><br>
                    ※今回用いている生徒のデータは、全て公開情報に基づくものです。<br>
                    """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('## 例')

        image_path = "./intro_1_control.jpg"  # ローカルの画像ファイルパス
        st.image(image_path, caption="問題を解く画面の例その1")
        image_path = "./intro_2_control.jpg"  # ローカルの画像ファイルパス
        st.image(image_path, caption="問題を解く画面の例その2")
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('準備ができたら、下の「準備ができました」ボタンを押してください。練習問題(5問)が始まります。<br>【重要】画面の不具合がありましたら、右上の黒い点が3つあるボタンから「Rerun」を押してください。<br>この先でURLをリロードすると最初からやり直しになります。', unsafe_allow_html=True)
        image_path = "./info.jpg"  # ローカルの画像ファイルパス
        st.image(image_path, caption="画面の不具合への対処方法")
        st.session_state.page = "t1p1"

        if st.button("準備ができました。"):
            time.sleep(0.2)
            #go_to_page("t1p1")

elif st.session_state.page == "t1p1":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p1" not in st.session_state:
        st.session_state.start_button_clicked_t1p1 = False
        st.session_state.question_t1p1_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p1 = True
    
    if st.session_state.start_button_clicked_t1p1:
        st.title("練習問題 その1")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)

        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'なし', 'あり', 'かなり少ない', '0日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

        #checkboxes = []
        #for name in df["項目"]:
        #    checkbox = st.checkbox(f"{name}")
        #    checkboxes.append(checkbox)

        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai1")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t1p1")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell('A10', text1)
                            worksheet.update_acell('A11', str(elapsed_time))

                            st.session_state.question_t1p1_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.markdown("#### 正解は「平均より優れている」でした。", unsafe_allow_html=True)

                            st.session_state.page = "t1p2"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t1p1",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t1p1_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t1p2")

elif st.session_state.page == "t1p2":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p2" not in st.session_state:
        st.session_state.start_button_clicked_t1p2 = False
        st.session_state.question_t1p2_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p2 = True
    
    if st.session_state.start_button_clicked_t1p2:
        st.title("練習問題 その2")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2時間以下 (全生徒の平均は2-5時間)', 'なし', 'なし', '多い', '4日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai2")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t1p2")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('B10', text1)
                            worksheet.update_acell('B11', str(elapsed_time))

                            st.session_state.question_t1p2_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            st.markdown("#### 正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t1p3"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t1p2",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t1p2_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t1p3")

elif st.session_state.page == "t1p3":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p3" not in st.session_state:
        st.session_state.start_button_clicked_t1p3 = False
        st.session_state.question_t1p3_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p3 = True
    
    if st.session_state.start_button_clicked_t1p3:
        st.title("練習問題 その3")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2時間以下 (全生徒の平均は2-5時間)', 'なし', 'あり', '少ない', '14日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai3")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t1p3")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('C10', text1)
                            worksheet.update_acell('C11', str(elapsed_time))

                            st.session_state.question_t1p3_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            st.markdown("#### 正解は「平均以下」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t1p4"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t1p3",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t1p3_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t1p4")

elif st.session_state.page == "t1p4":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p4" not in st.session_state:
        st.session_state.start_button_clicked_t1p4 = False
        st.session_state.question_t1p4_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p4 = True
    
    if st.session_state.start_button_clicked_t1p4:
        st.title("練習問題 その4")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15-30分 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'あり', 'なし', '普通', '14日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai4")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t1p4")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('D10', text1)
                            worksheet.update_acell('D11', str(elapsed_time))

                            st.session_state.question_t1p4_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            st.markdown("#### 正解は「平均以下」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t1p5"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t1p4",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t1p4_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t1p5")

elif st.session_state.page == "t1p5":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p5" not in st.session_state:
        st.session_state.start_button_clicked_t1p5 = False
        st.session_state.question_t1p5_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p5 = True
    
    if st.session_state.start_button_clicked_t1p5:
        st.title("練習問題 その5")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '10時間以上 (全生徒の平均は2-5時間)', 'なし', 'なし', '少ない', '4日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai5")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t1p5")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('E10', text1)
                            worksheet.update_acell('E11', str(elapsed_time))

                            st.session_state.question_t1p5_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            st.markdown("#### 正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "task2"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t1p5",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t1p5_finished:
            if st.button("次のページに進む"):
                time.sleep(0.2)
                #go_to_page("task2")

elif st.session_state.page == "task2":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2" not in st.session_state:
        st.session_state.start_button_clicked_t2 = False

    if st.button("ボタンを押してください"):
        st.session_state.start_button_clicked_t2 = True

    if st.session_state.start_button_clicked_t2:

        st.markdown("""
                    練習問題お疲れ様でした。それでは、本番の15問に進みます。<br>
                    """, unsafe_allow_html=True)

        st.markdown('準備ができたら、下の「準備ができました」ボタンを押してください。')

        st.session_state.page = "t2p1"

        if st.button("準備ができました。"):
            time.sleep(0.2)
            #go_to_page("t2p1")

elif st.session_state.page == "t2p1":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p1" not in st.session_state:
        st.session_state.start_button_clicked_t2p1 = False
        st.session_state.question_t2p1_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p1 = True
    
    if st.session_state.start_button_clicked_t2p1:
        st.title("問題 その1")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'あり', 'あり', '少ない', '10日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai6")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p1")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('A20', text1)
                            worksheet.update_acell('A21', str(elapsed_time))

                            st.session_state.question_t2p1_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均以下」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p2"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p1",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p1_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p2")

elif st.session_state.page == "t2p2":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p2" not in st.session_state:
        st.session_state.start_button_clicked_t2p2 = False
        st.session_state.question_t2p2_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p2 = True
    
    if st.session_state.start_button_clicked_t2p2:
        st.title("問題 その2")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '5-10時間 (全生徒の平均は2-5時間)', 'なし', 'あり', '少ない', '2日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai7")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p2")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('B20', text1)
                            worksheet.update_acell('B21', str(elapsed_time))

                            st.session_state.question_t2p2_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p3"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p2",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p2_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p3")

elif st.session_state.page == "t2p3":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p3" not in st.session_state:
        st.session_state.start_button_clicked_t2p3 = False
        st.session_state.question_t2p3_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p3 = True
    
    if st.session_state.start_button_clicked_t2p3:
        st.title("問題 その3")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15-30分 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'あり', 'なし', '多い', '6日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai8")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p3")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('C20', text1)
                            worksheet.update_acell('C21', str(elapsed_time))

                            st.session_state.question_t2p3_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p4"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p3",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p3_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p4")

elif st.session_state.page == "t2p4":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p4" not in st.session_state:
        st.session_state.start_button_clicked_t2p4 = False
        st.session_state.question_t2p4_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p4 = True
    
    if st.session_state.start_button_clicked_t2p4:
        st.title("問題 その4")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'なし', 'あり', '少ない', '0日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai9")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p4")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('D20', text1)
                            worksheet.update_acell('D21', str(elapsed_time))

                            st.session_state.question_t2p4_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p5"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p4",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p4_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p5")

elif st.session_state.page == "t2p5":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p5" not in st.session_state:
        st.session_state.start_button_clicked_t2p5 = False
        st.session_state.question_t2p5_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p5 = True
    
    if st.session_state.start_button_clicked_t2p5:
        st.title("問題 その5")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['30分-1時間 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'あり', 'なし', '少ない', '4日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai10")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p5")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('E20', text1)
                            worksheet.update_acell('E21', str(elapsed_time))

                            st.session_state.question_t2p5_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p6"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p5",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p5_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p6")

elif st.session_state.page == "t2p6":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p6" not in st.session_state:
        st.session_state.start_button_clicked_t2p6 = False
        st.session_state.question_t2p6_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p6 = True
    
    if st.session_state.start_button_clicked_t2p6:
        st.title("問題 その6")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2時間以下 (全生徒の平均は2-5時間)', 'なし', 'あり', '普通', '2日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai11")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p6")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('F20', text1)
                            worksheet.update_acell('F21', str(elapsed_time))

                            st.session_state.question_t2p6_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p7"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p6",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p6_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p7")

elif st.session_state.page == "t2p7":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p7" not in st.session_state:
        st.session_state.start_button_clicked_t2p7 = False
        st.session_state.question_t2p7_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p7 = True
    
    if st.session_state.start_button_clicked_t2p7:
        st.title("問題 その7")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2時間以下 (全生徒の平均は2-5時間)', 'なし', 'なし', 'とても多い', '16日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai12")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p7")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('G20', text1)
                            worksheet.update_acell('G21', str(elapsed_time))

                            st.session_state.question_t2p7_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p8"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p7",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p7_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p8")

elif st.session_state.page == "t2p8":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p8" not in st.session_state:
        st.session_state.start_button_clicked_t2p8 = False
        st.session_state.question_t2p8_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p8 = True
    
    if st.session_state.start_button_clicked_t2p8:
        st.title("問題 その8")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2時間以下 (全生徒の平均は2-5時間)', 'なし', 'あり', '少ない', '0日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai13")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p8")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('H20', text1)
                            worksheet.update_acell('H21', str(elapsed_time))

                            st.session_state.question_t2p8_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p9"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p8",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p8_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p9")

elif st.session_state.page == "t2p9":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p9" not in st.session_state:
        st.session_state.start_button_clicked_t2p9 = False
        st.session_state.question_t2p9_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p9 = True
    
    if st.session_state.start_button_clicked_t2p9:
        st.title("問題 その9")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '5-10時間 (全生徒の平均は2-5時間)', 'あり', 'あり', '少ない', '2日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai14")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p9")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('I20', text1)
                            worksheet.update_acell('I21', str(elapsed_time))

                            st.session_state.question_t2p9_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p10"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p9",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p9_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p10")

elif st.session_state.page == "t2p10":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p10" not in st.session_state:
        st.session_state.start_button_clicked_t2p10 = False
        st.session_state.question_t2p10_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p10 = True
    
    if st.session_state.start_button_clicked_t2p10:
        st.title("問題 その10")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15-30分 (全生徒の平均は15分程度)', '5-10時間 (全生徒の平均は2-5時間)', 'なし', 'なし', '普通', '7日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai15")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p10")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('J20', text1)
                            worksheet.update_acell('J21', str(elapsed_time))

                            st.session_state.question_t2p10_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p11"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p10",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p10_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p11")

elif st.session_state.page == "t2p11":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p11" not in st.session_state:
        st.session_state.start_button_clicked_t2p11 = False
        st.session_state.question_t2p11_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p11 = True
    
    if st.session_state.start_button_clicked_t2p11:
        st.title("問題 その11")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'なし', 'あり', '普通', '0日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai16")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p11")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('K20', text1)
                            worksheet.update_acell('K21', str(elapsed_time))

                            st.session_state.question_t2p11_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p12"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p11",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p11_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p12")

elif st.session_state.page == "t2p12":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p12" not in st.session_state:
        st.session_state.start_button_clicked_t2p12 = False
        st.session_state.question_t2p12_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p12 = True
    
    if st.session_state.start_button_clicked_t2p12:
        st.title("問題 その12")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '5-10時間 (全生徒の平均は2-5時間)', 'あり', 'あり', '少ない', '2日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai17")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p12")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('L20', text1)
                            worksheet.update_acell('L21', str(elapsed_time))

                            st.session_state.question_t2p12_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p13"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p12",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p12_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p13")

elif st.session_state.page == "t2p13":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p13" not in st.session_state:
        st.session_state.start_button_clicked_t2p13 = False
        st.session_state.question_t2p13_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p13 = True
    
    if st.session_state.start_button_clicked_t2p13:
        st.title("問題 その13")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'あり', 'あり', '少ない', '8日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai18")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p13")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('M20', text1)
                            worksheet.update_acell('M21', str(elapsed_time))

                            st.session_state.question_t2p13_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p14"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p13",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p13_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p14")

elif st.session_state.page == "t2p14":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p14" not in st.session_state:
        st.session_state.start_button_clicked_t2p14 = False
        st.session_state.question_t2p14_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p14 = True
    
    if st.session_state.start_button_clicked_t2p14:
        st.title("問題 その14")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'なし', 'なし', 'とても多い', '12日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai19")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均より優れている", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p14")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('N20', text1)
                            worksheet.update_acell('N21', str(elapsed_time))

                            st.session_state.question_t2p14_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "t2p15"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p14",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p14_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("t2p15")

elif st.session_state.page == "t2p15":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p15" not in st.session_state:
        st.session_state.start_button_clicked_t2p15 = False
        st.session_state.question_t2p15_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p15 = True
    
    if st.session_state.start_button_clicked_t2p15:
        st.title("問題 その15")
        st.markdown("以下のプロフィール情報をもとに、生徒の数学の成績を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 生徒のプロフィール", unsafe_allow_html=True)
        # ダミーデータの作成
        df = pd.DataFrame({
            '項目': ['家から学校までの通学時間', '毎週の勉強時間', '補習などの教育サポート', '学習塾など有料の教育サポート', '友人と出かける頻度', '学校を休んだ回数'],
            '内容': ['15分以下 (全生徒の平均は15分程度)', '2-5時間 (全生徒の平均は2-5時間)', 'あり', 'なし', '多い', '2日 (全生徒の平均は6日程度)']
        })
        # DataFrameを表示
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai20")

        with form:
            text0 = st.selectbox("生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                st.session_state.human_prediction_finished = True

        if st.session_state.human_prediction_finished:

            st.markdown("続いて、AIの予測を提示します。", unsafe_allow_html=True)
            st.markdown("", unsafe_allow_html=True)
            st.markdown("#### AIの予想：成績は平均以下", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            form = st.form(key="t2p15")

            with form:
                text1 = st.selectbox("最終的に、生徒の成績はどちらだと思いますか？", ["選択してください", "平均より優れている", "平均以下"])
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        gc = gspread.authorize(credentials)
                        try:
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1
                            st.session_state.end = time.time()
                            elapsed_time = st.session_state.end - st.session_state.start
                            worksheet.update_acell('O20', text1)
                            worksheet.update_acell('O21', str(elapsed_time))

                            st.session_state.question_t2p15_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")
                            #st.markdown("#### ちなみに正解は「平均より優れている」でした。", unsafe_allow_html=True)
                            st.session_state.page = "questionnaire"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name + "_t2p15",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f
                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        retries += 1

        if st.session_state.question_t2p15_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                #go_to_page("questionnaire")

elif st.session_state.page == "questionnaire":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "questionnaire" not in st.session_state:
        st.session_state.questionnaire = False

    st.markdown('# ユーザアンケートページ')
    st.markdown('タスクの完了お疲れ様でした。 <br> 最後に、以下の評価アンケートを記入して提出をお願いします。', unsafe_allow_html=True)
    form = st.form(key="questionnaire_form")

    with form:
        # 質問リスト
        questions = [
            "AIが提示した情報をもとに、自分の考えを変えようと思いましたか。AIのヒントに従おうと思いましたか。",
            "AIに意思決定を任せてしまおうと感じましたか。",
            "意思決定を主体的に行なったと感じますか。",
            "意思決定の結果に対する責任はAIにあると思いますか。",
            "AIに自分の意見を誘導されたと感じましたか。",
            "あなたはこのAIを信頼できると思いますか？",
            "技術システムについて詳細に調べるのが好きですか。",
            "新しい技術システムの機能をテストするのが好きですか。",
            "技術システムを主に扱うのは、やらなければならないからですか。",
            "新しい技術システムを目の前にすると、徹底的に試しますか。",
            "新しい技術システムに慣れるために時間を費やすのが好きですか。",
            "技術システムが機能するだけで十分で、どのように、なぜ機能するかは気にしませんか。",
            "技術システムがどのように機能するかを正確に理解しようと努めますか。",
            "技術システムの基本的な機能を知っていれば十分ですか。",
            "技術システムの機能を最大限に活用しようと努めますか。",
            "あなたは実験で使用したAIによって意思決定を支援してほしいですか。",
            "AIから提示された情報は有益だと思いましたか。",
            "こうした意思決定を支援するAIは必要だと思いますか。",
        ]

        # アンケートの表示
        st.title("AIの意思決定支援についての評価アンケート")
        st.markdown("自分の意見に近いものをスライダーで選んでください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # 初期位置を設定
        default_value = "どちらでもない"

        st.session_state.responses = []
        st.session_state.reasons = []
        for i, question in enumerate(questions):
            response = st.select_slider(
                f"Q. {i + 1} {question}",
                options=["全くそう思わない", "そう思わない", "あまりそう思わない", "どちらでもない", "ややそう思う", "そう思う", "非常にそう思う"],
                key=f"slider_q{i + 1}",
                value=default_value 
            )
            st.session_state.responses.append(response)
            if i < 6 or i > 14:
                text1_q1 = st.text_input(f"Q.{i+1} においてそのように回答した理由を教えてください(15文字以上)。", key=f"q{i+1}")
                st.session_state.reasons.append(text1_q1)
            st.markdown("<hr>", unsafe_allow_html=True)
        
        q_submitted = st.form_submit_button(label="回答を提出")

    if q_submitted:

        try:
            count = 0
            for i in range(len(st.session_state.reasons)):
                if len(st.session_state.reasons) < 9:
                    st.error("全ての理由に回答してください。")
                    break
                elif len(st.session_state.reasons[i]) < 15:
                    st.error("理由は15文字以上で回答してください。")
                    break
                elif not st.session_state.reasons[i].strip():
                    st.error("理由は15文字以上で回答してください。")
                    break
                else:
                    count += 1
        except:
            st.error("理由は15文字以上で回答してください。")
        if count == len(st.session_state.reasons):
            st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
            max_retries=3
            retries = 0
            while retries <= max_retries:
                scopes = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                json_keyfile_dict = st.secrets["service_account"]
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    json_keyfile_dict, 
                    scopes
                )
                # gspread用に認証
                gc = gspread.authorize(credentials)
                try:
                    # スプレッドシートのIDを指定してワークブックを選択
                    workbook = gc.open_by_key(st.session_state.file['id'])
                    worksheet = workbook.sheet1

                    cell_list = worksheet.range(30, 1, 30, len(st.session_state.responses)+len(st.session_state.reasons)+1)
                    for i in range(len(st.session_state.responses)):
                        cell_list[i].value = st.session_state.responses[i]
                    for i in range(len(st.session_state.responses), len(st.session_state.responses)+len(st.session_state.reasons)):
                        cell_list[i].value = st.session_state.reasons[i-len(st.session_state.responses)]

                    # スプレッドシートを更新
                    worksheet.update_cells(cell_list)

                    st.session_state.questionnaire = True

                    st.success("回答を提出しました！")

                    retries += 5
                except Exception as e:
                    print(e)
                    f = drive.CreateFile({
                        'title': st.session_state.file_name + "_questionnaire",
                        'mimeType': 'application/vnd.google-apps.spreadsheet',
                        "parents": [{"id": st.secrets["folder_id"]}]
                    })
                    f.Upload()
                    st.session_state.file = f

                    if retries == max_retries:
                        st.error(f"申し訳ありませんが、提出がうまくいきませんでした。再度「回答を提出」ボタンを押してください。")

                # 再トライ準備
                retries += 1

    if st.session_state.questionnaire:
        st.markdown("これでアンケートは終了です。お疲れ様でした。<br>この度は、調査にご協力いただき誠にありがとうございました。", unsafe_allow_html=True)

        st.markdown("最後に、ランサーズのフォームに入力する合言葉を表示します。<br>こちらが正しくないと、謝礼をお支払いできませんので、お間違いないよう確実に入力してください。", unsafe_allow_html=True)

        st.markdown("合言葉："+st.session_state.file_name, unsafe_allow_html=True)

        st.markdown("では、ランサーズのフォームに戻って合言葉を入力してください。", unsafe_allow_html=True)

        #st.markdown("また、もし研究参加への同意を撤回される場合は、以下の同意撤回書をダウンロードしてください。", unsafe_allow_html=True)

        #st.download_button(
        #    label="同意撤回書をダウンロードする",
        #    data= "./disagreement.docx",
        #    file_name="同意撤回書.docx",
        #    mime="application/msword"
        #)
