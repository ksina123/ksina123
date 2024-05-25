from flask import Flask, send_from_directory
from pywebio.input import input, PASSWORD
from pywebio.output import put_buttons, put_html, put_markdown, put_table, clear, toast
from pywebio.platform.flask import webio_view
import app from '.static/member_stats.png';
import json
import os
import io
import base64
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
import traceback

# matplotlib 백엔드를 'Agg'로 설정 (서버리스 환경에서 작동)
plt.switch_backend('Agg')

app = Flask(__name__, static_folder='static')

# Ensure the static folder exists
static_folder_path = os.path.join(app.root_path, 'static')
if not os.path.exists(static_folder_path):
    os.makedirs(static_folder_path)

# JSON 파일 경로
data_file = 'guild_data.json'

# 링크 데이터 파일 경로
links_file = 'links_data.json'

# 링크 데이터 초기화
links_data = {
    'damage_calc': 'https://maphe.github.io/e7-damage-calc/kr/index.html',
    'attack_deck': 'https://fribbels.github.io/e7/gw-meta.html',
    'buffs_debuffs': 'https://epic7x.com/buffs-debuffs',
    'maze': 'https://ceciliabot.github.io/',
    'crack_specs': 'https://arca.live/b/epic7/88930300?category=%EC%98%81%EC%9B%85%EC%8A%A4%ED%8E%99&p=1',
    'hero_catalog': 'https://epic7db.com/',
    'catalyst_info': 'https://epicsevendb.com/ko/heroes',
    'arca_live': 'https://arca.live/b/epic7',
    'official_community': 'https://epic7.onstove.com/ko/brand#',
    'hero_spec': 'https://fribbels.github.io/e7/hero-library.html',
    'pvp_search': 'https://epic7.gg.onstove.com/ko',
    'join_inquiry': 'https://open.kakao.com/o/gr6ymkqd'
}

# 기사단 전쟁 전적 데이터
war_records = [
    {"date": "4/29 (월)", "guild": "서풍", "score": 13120, "opponent_score": 8160, "result": "승"},
    {"date": "5/1 (수)", "guild": "강호", "score": 13060, "opponent_score": 12220, "result": "승"},
    {"date": "5/3 (금)", "guild": "모라고라", "score": 13660, "opponent_score": 9960, "result": "승"},
    {"date": "5/6 (월)", "guild": "경화수월", "score": 13720, "opponent_score": 9000, "result": "승"},
    {"date": "5/8 (수)", "guild": "서약", "score": 13060, "opponent_score": 9540, "result": "승"},
    {"date": "5/10 (금)", "guild": "머라고라", "score": 13120, "opponent_score": 13000, "result": "승"},
    {"date": "5/13 (월)", "guild": "레인가르", "score": 13060, "opponent_score": 12160, "result": "승"},
    {"date": "5/15 (수)", "guild": "나이트오브라운즈", "score": 12940, "opponent_score": 11860, "result": "승"},
    {"date": "5/17 (금)", "guild": "EPYON", "score": 12760, "opponent_score": 11380, "result": "승"},
    {"date": "5/20 (월)", "guild": "틸라다", "score": 12940, "opponent_score": 12040, "result": "승"},
    {"date": "5/22 (수)", "guild": "Mabinogi", "score": 12700, "opponent_score": 9940, "result": "승"},
    {"date": "5/24 (금)", "guild": "레인가르", "score": 13360, "opponent_score": 13240, "result": "승"}
]

# 데이터 로드 함수
def load_data(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}  # 파일이 없을 경우 빈 딕셔너리 반환

# 데이터 저장 함수
def save_data(data, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    toast("데이터가 저장되었습니다.", duration=3)

# 전역 변수로 초기 데이터 로드
guild_data = load_data(data_file)

# 링크 열기 함수
def open_link(button_id):
    if button_id in links_data:
        link = links_data[button_id]
        put_html(f"<script>window.open('{link}', '_blank');</script>")
    else:
        toast("링크가 설정되지 않았습니다.", duration=3)

# 기사단 전쟁현황 표시 함수
def show_war_records():
    clear()
    put_markdown("## 경쟁의 시즌 기사단 전쟁현황")
    table_data = [["날짜", "기사단", "점수", "상대 점수", "결과"]]
    for record in war_records:
        table_data.append([record["date"], record["guild"], record["score"], record["opponent_score"], record["result"]])
    put_table(table_data)
    put_html("<div style='text-align: center;'>")
    put_buttons([{'label': '메인 페이지로 돌아가기', 'value': 'topscreen', 'color': 'warning'}], onclick=lambda _: topscreen())
    put_html("</div>")

# 기사단원 전투 기록 표시 함수
def show_member_records():
    clear()
    try:
        password = input("기사단원만 접근 할 수 있습니다. 암호를 입력해주세요", type=PASSWORD)
        
        if password != "121212":
            toast("잘못된 암호입니다. 접근이 거부되었습니다.", color='red', duration=3)
            topscreen()
            return

        selected_member = input("기사단원 닉네임을 입력하세요")

        if selected_member in guild_data:
            records = guild_data[selected_member]
            grouped_records = defaultdict(list)
            for record in records:
                grouped_records[record['opponent_guild']].append(record)

            for opponent_guild, record_list in grouped_records.items():
                put_markdown(f"### 상대 기사단: {opponent_guild}")
                for record in record_list:
                    put_markdown(f"#### 상대 기사단원: {record['opponent_member']}")
                    put_markdown("**공격 기록**")
                    table_data = [["라운드", "나의 공덱", "상대 방덱", "결과"]]
                    for idx, round in enumerate(record['rounds'], 1):
                        table_data.append([f"{idx}라운드", " ".join(round["my_team"]), " ".join(round["opponent_team"]), round["result"]])
                    put_table(table_data)
        else:
            toast("해당 기사단원의 기록을 찾을 수 없습니다.", color='red', duration=3)
    except Exception as e:
        print(traceback.format_exc())
        toast(f"오류가 발생했습니다: {str(e)}", color='red')

    put_html("<div style='text-align: center;'>")
    put_buttons([{'label': '메인 페이지로 돌아가기', 'value': 'topscreen', 'color': 'warning'}], onclick=lambda _: topscreen())
    put_html("</div>")

# 기사단원 승률 통계 표시 함수
def show_member_stats():
    clear()
    try:
        password = input("기사단원만 접근 할 수 있습니다. 암호를 입력해주세요", type=PASSWORD)

        if password != "121212":
            toast("잘못된 암호입니다. 접근이 거부되었습니다.", color='red', duration=3)
            topscreen()
            return

        selected_member = input("기사단원 닉네임을 입력하세요")

        if selected_member in guild_data:
            records = guild_data[selected_member]
            
            attack_deck_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
            defense_deck_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
            
            for record in records:
                for round_info in record['rounds']:
                    attack_deck = " ".join(sorted(round_info["my_team"]))
                    defense_deck = " ".join(sorted(round_info["opponent_team"]))
                    result = round_info["result"]
                    attack_deck_stats[attack_deck]['total'] += 1
                    defense_deck_stats[defense_deck]['total'] += 1
                    if result == "승":
                        attack_deck_stats[attack_deck]['wins'] += 1
                    else:
                        defense_deck_stats[defense_deck]['wins'] += 1
            
            attack_deck_win_rates = {
                deck: (stats['wins'] / stats['total']) * 100 for deck, stats in attack_deck_stats.items()
            }

            defense_deck_win_rates = {
                deck: (stats['wins'] / stats['total']) * 100 for deck, stats in defense_deck_stats.items()
            }

            total_wins = sum(stats['wins'] for stats in attack_deck_stats.values())
            total_matches = sum(stats['total'] for stats in attack_deck_stats.values())
            overall_win_rate = (total_wins / total_matches) * 100

            top_10_attack_decks = sorted(attack_deck_win_rates.items(), key=lambda x: x[1], reverse=True)[:10]
            most_used_attack_decks = sorted(attack_deck_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
            most_faced_defense_decks = sorted(defense_deck_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]

            put_markdown(f"## {selected_member}의 기사단 전투 기록")
            put_markdown(f"### 전체 공격 승률: {overall_win_rate:.2f}%")
            
            put_markdown("### 가장 승률이 높은 공덱 10개")
            table_data = [["공덱", "공격승률 (%)"]]
            for deck, win_rate in top_10_attack_decks:
                table_data.append([deck, f"{win_rate:.2f}%"])
            put_table(table_data)

            put_markdown("### 가장 많이 사용된 공덱 10개")
            table_data = [["공덱", "사용 횟수", "공격승률 (%)"]]
            for deck, stats in most_used_attack_decks:
                win_rate = (stats['wins'] / stats['total']) * 100
                table_data.append([deck, stats['total'], f"{win_rate:.2f}%"])
            put_table(table_data)

            put_markdown("### 가장 많이 상대했던 방덱 10개")
            table_data = [["방덱", "사용 횟수", "방어승률 (%)"]]
            for deck, stats in most_faced_defense_decks:
                win_rate = (stats['wins'] / stats['total']) * 100
                table_data.append([deck, stats['total'], f"{win_rate:.2f}%"])
            put_table(table_data)

            # 그래프 그리기
            plot_win_rates(overall_win_rate, top_10_attack_decks, most_used_attack_decks, most_faced_defense_decks)
            
        else:
            toast("해당 기사단원의 기록을 찾을 수 없습니다.", color='red', duration=3)
    except Exception as e:
        print(traceback.format_exc())
        toast(f"오류가 발생했습니다: {str(e)}", color='red')

    put_html("<div style='text-align: center;'>")
    put_buttons([{'label': '메인 페이지로 돌아가기', 'value': 'topscreen', 'color': 'warning'}], onclick=lambda _: topscreen())
    put_html("</div>")

# 그래프 그리기 함수
def plot_win_rates(overall_win_rate, top_10_attack_decks, most_used_attack_decks, most_faced_defense_decks):
    try:
        plt.rc('font', family='Malgun Gothic')  # 한글 폰트 설정

        plt.figure(figsize=(15, 12))

        # 승률이 높은 공덱 10개
        plt.subplot(3, 1, 1)
        labels = ["전체 공격 승률"] + [deck for deck, _ in top_10_attack_decks]
        win_rates = [overall_win_rate] + [win_rate for _, win_rate in top_10_attack_decks]
        plt.bar(labels, win_rates, color=['blue'] + ['green']*10)
        plt.ylabel('승률 (%)')
        plt.title('전체 공격 승률과 상위 10개 공덱 승률')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)

        # 많이 사용된 공덱 10개
        plt.subplot(3, 1, 2)
        labels = [deck for deck, _ in most_used_attack_decks]
        usage_counts = [stats['total'] for _, stats in most_used_attack_decks]
        win_rates = [(stats['wins'] / stats['total']) * 100 for _, stats in most_used_attack_decks]
        plt.bar(labels, usage_counts, color='orange', alpha=0.6, label='사용 횟수')
        plt.ylabel('사용 횟수')
        plt.title('가장 많이 사용된 공덱 10개')
        plt.xticks(rotation=45, ha='right')
        
        # 추가된 승률 바
        for i, win_rate in enumerate(win_rates):
            plt.text(i, usage_counts[i] + 0.5, f'{win_rate:.2f}%', ha='center', va='bottom', fontsize=10, color='black')

        # 많이 상대했던 방덱 10개
        plt.subplot(3, 1, 3)
        labels = [deck for deck, _ in most_faced_defense_decks]
        usage_counts = [stats['total'] for _, stats in most_faced_defense_decks]
        win_rates = [(stats['wins'] / stats['total']) * 100 for _, stats in most_faced_defense_decks]
        plt.bar(labels, usage_counts, color='red', alpha=0.6, label='사용 횟수')
        plt.ylabel('사용 횟수')
        plt.title('가장 많이 상대했던 방덱 10개')
        plt.xticks(rotation=45, ha='right')
        
        # 추가된 승률 바
        for i, win_rate in enumerate(win_rates):
            plt.text(i, usage_counts[i] + 0.5, f'{win_rate:.2f}%', ha='center', va='bottom', fontsize=10, color='black')

        plt.tight_layout()

       # 그래프를 이미지로 저장하고 base64 인코딩
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()

        # 이미지 HTML로 표시
        img_src = f"data:image/png;base64,{image_base64}"
        put_html(f"<img src='{img_src}' alt='Statistics Graph'>")

    except Exception as e:
        print(traceback.format_exc())
        toast(f"그래프를 생성하는 중 오류가 발생했습니다: {str(e)}", color='red')
        
# 화면 초기화 및 메인 메뉴 표시 함수
def topscreen():
    clear()
    put_html("""
    <style>
        body {
            background: url('https://d2x8kymwjom7h7.cloudfront.net/live/application_no/96001/default/fd968fe88a3e4e0989da33b124863c3c.jpg') no-repeat center center fixed;
            background-size: cover;
        }
        .menu-container {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            padding: 20px;
        }
        .menu-button {
            width: 200px;
            height: 50px;
            margin: 10px;
            font-size: 18px;
            color: white;
            background-color: #ff0000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .menu-button:hover {
            background-color: #cc0000;
        }
        .logo {
            width: 100px;
            height: 100px;
            margin-right: 20px;
        }
        .info-button {
            width: 200px;
            height: 40px;
            margin: 5px;
            font-size: 16px;
            color: white;
            background-color: #007bff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .info-button:hover {
            background-color: #0056b3;
        }
        .member-table {
            width: 80%;
            margin: 20px auto;
            border-collapse: collapse;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .member-table th, .member-table td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
        }
        .member-table th {
            background-color: #f4f4f4;
        }
        .member-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        #pywebio-footer {
            position: absolute;
            right: 10px;
            bottom: 10px;
            color: #fff;
        }
        #creative-by {
            position: absolute;
            left: 10px;
            bottom: 10px;
            color: #fff;
            font-size: 14px;
        }
    </style>
    <div class="menu-container">
        <img src="https://i.ibb.co/VwHg479/logo.png" alt="기사단 로고" class="logo">
        <div>
    """)
    put_buttons([
        {'label': '기사단 소개', 'value': 'intro', 'class': 'menu-button'},
        {'label': '기사단 멤버', 'value': 'members', 'class': 'menu-button'},
        {'label': '에픽세븐 정보', 'value': 'info', 'class': 'menu-button'},
        {'label': '기사단 전쟁현황', 'value': 'war_records', 'class': 'menu-button'},
        {'label': '기사단원 전투 기록', 'value': 'member_records', 'class': 'menu-button'},
        {'label': '기사단원 승률 통계', 'value': 'show_member_stats', 'class': 'menu-button'},
        {'label': '1st 가입문의', 'value': 'join_inquiry', 'class': 'menu-button'}
    ], onclick=navigate)
    put_html("""
        </div>
    </div>
    <div id="creative-by">Creative by Slayer</div>
    """)

def show_intro():
    clear()
    put_markdown("""
    # 에픽세븐 1st 기사단 소개

    환영합니다! 저희는 에픽세븐의 자랑스러운 명예의 전당 기사단, **1st 기사단**입니다. 전투와 전략, 그리고 끈끈한 단결력으로 에픽세븐의 정상에 오른 최고의 기사단입니다.

    ## 우리의 목표
    1st 기사단의 목표는 단순합니다. **승리**와 **우정**입니다. 우리는 에픽세븐에서 최강의 자리를 유지하며, 기사단원들 간의 끈끈한 우정과 협력을 바탕으로 함께 성장해 나갑니다.

    ## 활동 내용
    - **주간 기사단 전투**: 매주 최고의 전략을 구상하고, 각 단원들의 특성을 살려 승리를 거머쥡니다.
    - **공략 공유**: 새로운 영웅, 장비 세팅, 전투 전략 등을 서로 공유하며 효율적인 플레이를 추구합니다.
    - **소통과 협력**: 활발한 소통을 통해 단원들 간의 유대감을 강화하고, 서로 도우며 성장합니다.

    ## 가입 조건
    1st 기사단은 누구에게나 열려 있습니다. 그러나 강한 책임감과 열정을 가진 분들을 찾고 있습니다. 다음의 조건을 만족하는 분들을 환영합니다:
    - **활동적인 플레이어**: 꾸준히 게임을 즐기며, 주간 기사단 전투에 적극적으로 참여할 수 있는 분.
    - **팀워크와 소통**: 단원들과의 원활한 소통을 통해 협력할 수 있는 분.
    - **전략적 사고**: 전투에서 전략적으로 행동하고, 공략을 공유하며 함께 성장할 수 있는 분.

    ## 혜택
    1st 기사단의 일원이 되면 다음과 같은 혜택을 누릴 수 있습니다:
    - **강력한 지원**: 상위 기사단 보상과 다양한 이벤트 참여 기회.
    - **지속적인 성장**: 경험이 풍부한 단원들의 노하우를 공유받아 더욱 빠르게 성장.
    - **단합된 커뮤니티**: 게임 외에도 다양한 활동을 함께하며 끈끈한 유대감을 형성.

    ## 마무리
    에픽세븐의 세계에서 최강의 자리를 지키고 있는 1st 기사단에 오신 것을 환영합니다. 함께 싸우고, 성장하며, 정상의 자리를 유지해 나갈 여러분을 기다리고 있습니다. 지금 바로 가입하세요!
    """)
    put_html("<div style='text-align: center;'>")
    put_buttons([{'label': '메인 페이지로 돌아가기', 'value': 'topscreen', 'color': 'warning'}], onclick=lambda _: topscreen())
    put_html("</div>")

members = [
    {"name": "음률", "role": "기사단장"},
    {"name": "푸니몬", "role": "기사단원"},
    {"name": "영혼탈곡기", "role": "기사단원"},
    {"name": "Gold", "role": "기사단원"},
    {"name": "건학", "role": "기사단원"},
    {"name": "되게신나", "role": "기사단원"},
    {"name": "유즈리엘", "role": "기사단원"},
    {"name": "Seiren", "role": "기사단원"},
    {"name": "Kuzei", "role": "기사단원"},
    {"name": "XiuDoplamin", "role": "기사단원"},
    {"name": "여신힐데", "role": "기사단원"},
    {"name": "상냥함", "role": "기사단원"},
    {"name": "푹신푹신침대", "role": "기사단원"},
    {"name": "닥쳐", "role": "기사단원"},
    {"name": "에이다뎀벼", "role": "기사단원"},
    {"name": "껍데기", "role": "기사단원"},
    {"name": "Slayer", "role": "기사단원"},
    {"name": "화얼신", "role": "기사단원"},
    {"name": "힙합", "role": "기사단원"},
    {"name": "RayNolS", "role": "기사단원"},
    {"name": "채니몬", "role": "기사단원"},
    {"name": "카르텔", "role": "기사단원"},
    {"name": "임시완", "role": "기사단원"},
    {"name": "필유", "role": "기사단원"},
    {"name": "크라우니", "role": "기사단원"},
    {"name": "죽음의탐구자", "role": "기사단원"},
    {"name": "일호", "role": "기사단원"},
    {"name": "운9실력1", "role": "기사단원"},
    {"name": "선의향연", "role": "기사단원"},
]

def show_members(search_term=None):
    clear()

    table_rows = """
    <tr>
        <th>역할</th>
        <th>멤버</th>
    </tr>
    """

    if search_term:
        for member in members:
            if search_term in member['name']:
                name = f"<span style='color: green;'>{member['name']}</span>"
                table_rows += f"""
                <tr>
                    <td>{member['role']}</td>
                    <td>{name}</td>
                </tr>
                """
    else:
        for member in members:
            table_rows += f"""
            <tr>
                <td>{member['role']}</td>
                <td>{member['name']}</td>
            </tr>
            """

    put_markdown("# 현 1st 멤버 구성원")
    put_html("<div style='text-align: center;'>")
    put_buttons([
        {'label': '검색', 'value': 'search', 'color': 'primary', 'style': 'margin-right: 10px;'},
    ], onclick=lambda _: show_members(input("닉네임 검색", placeholder="검색할 닉네임을 입력하세요")))
    put_html("</div>")
    put_html(f"""
    <table class="member-table">
        {table_rows}
    </table>
    """)
    put_html("<div style='text-align: right;'>")
    put_buttons([{'label': '메인 페이지로 돌아가기', 'value': 'topscreen', 'color': 'warning'}], onclick=lambda _: topscreen())
    put_html("</div>")

def show_info():
    clear()
    put_markdown("""
    # 에픽세븐 정보

    에픽세븐에 관한 다양한 정보들을 아래 버튼을 통해 확인하세요.
    """)
    put_buttons([
        {'label': '데미지 계산기', 'value': 'damage_calc', 'class': 'info-button'},
        {'label': '기사단전 공격/방어 덱 정보', 'value': 'attack_deck', 'class': 'info-button'},
        {'label': '버프/디버프', 'value': 'buffs_debuffs', 'class': 'info-button'},
        {'label': '미궁사기 사이트', 'value': 'maze', 'class': 'info-button'},
        {'label': '균열 스팩', 'value': 'crack_specs', 'class': 'info-button'},
        {'label': '영웅 스팩', 'value': 'hero_spec', 'class': 'info-button'},
        {'label': '영웅 도감', 'value': 'hero_catalog', 'class': 'info-button'},
        {'label': '촉매제 정보', 'value': 'catalyst_info', 'class': 'info-button'},
        {'label': '실레나 전적검색', 'value': 'pvp_search', 'class': 'info-button'},
        {'label': '아카라이브 채널', 'value': 'arca_live', 'class': 'info-button'},
        {'label': '공식 커뮤니티', 'value': 'official_community', 'class': 'info-button'}
    ], onclick=open_link)

    put_html("<div style='text-align: center;'>")
    put_buttons([{'label': '메인 페이지로 돌아가기', 'value': 'topscreen', 'color': 'warning'}], onclick=lambda _: topscreen())
    put_html("</div>")

def navigate(choice):
    if choice == 'intro':
        show_intro()
    elif choice == 'members':
        show_members()
    elif choice == 'info':
        show_info()
    elif choice == 'war_records':
        show_war_records()
    elif choice == 'member_records':
        show_member_records()
    elif choice == 'show_member_stats':
        show_member_stats()
    elif choice == 'join_inquiry':
        open_link('join_inquiry')

# 웹 인터페이스
def main():
    topscreen()

app.add_url_rule('/', 'webio_view', webio_view(main), methods=['GET', 'POST', 'OPTIONS'])

# Static 파일 경로 설정
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
