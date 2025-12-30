import streamlit as st
import random
import matplotlib.pyplot as plt

# ================== 기본 설정 ==================
st.set_page_config(page_title="🏪 매점 주식 게임", layout="wide")

ITEMS = ["이온음료", "오꾸밥", "아이스크림", "젤리", "포켓몬빵"]
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
DAY_LIMIT = 30
START_CASH = 50000

# ================== 초기화 ==================
def reset_game():
    st.session_state.day = 1
    st.session_state.cash = START_CASH
    st.session_state.portfolio = {k: 0 for k in ITEMS}
    st.session_state.risk = 0
    st.session_state.show_result = False
    st.session_state.stocks = {
        "이온음료": {"price": 1200, "vol": 0.12, "history": [1200]},
        "오꾸밥": {"price": 2000, "vol": 0.10, "history": [2000]},
        "아이스크림": {"price": 1500, "vol": 0.15, "history": [1500]},
        "젤리": {"price": 1000, "vol": 0.08, "history": [1000]},
        "포켓몬빵": {"price": 1800, "vol": 0.13, "history": [1800]},
    }

if "day" not in st.session_state:
    reset_game()

# ================== 이벤트 ==================
EVENTS = {
    3: ("모의고사 → 쉬는 시간 증가", {"이온음료": 0.25}),
    5: ("중간고사 → 이용 감소", {"전체": -0.15}),
    6: ("시험 과목 多 → 음료 폭증", {"이온음료": 0.4}),
    13: ("단축수업", {"오꾸밥": 0.2}),
    14: ("이동수업 많음", {"전체": -0.1}),
    18: ("급식 맛없음", {"오꾸밥": 0.3, "포켓몬빵": 0.3}),
    20: ("폭염", {"아이스크림": 0.45}),
    25: ("급식 맛있음", {"전체": -0.25}),
}

# ================== 가격 변동 ==================
def update_prices():
    for name, data in st.session_state.stocks.items():
        change = random.uniform(-data["vol"], data["vol"])
        if st.session_state.day in EVENTS:
            _, effect = EVENTS[st.session_state.day]
            if name in effect:
                change += effect[name]
            elif "전체" in effect:
                change += effect["전체"]
        if random.random() < 0.15:
            change += random.uniform(-0.25, 0.25)
        new_price = max(500, int(data["price"] * (1 + change)))
        data["price"] = new_price
        data["history"].append(new_price)

def arrow(h):
    if len(h) < 2: return "➖"
    if h[-1] > h[-2]: return "▲"
    if h[-1] < h[-2]: return "▼"
    return "➖"

def calc_total_asset():
    return st.session_state.cash + sum(
        st.session_state.portfolio[n] * st.session_state.stocks[n]["price"] for n in ITEMS
    )

# ================== 결과 페이지 ==================
if st.session_state.show_result:
    st.title("🏁 모의 투자 결과")
    st.caption("이 페이지를 다음 링크에 업로드해주시면 랭킹에 따라 추후 소정의 상품을 드립니다❤ by 컴퓨터온 동아리")

    total_asset = calc_total_asset()
    profit = total_asset - START_CASH
    profit_rate = profit / START_CASH * 100

    if st.session_state.risk >= 15:
        style = "공격형 🐯"
    elif st.session_state.risk >= 5:
        style = "균형형 🦊"
    else:
        style = "안정형 🐢"

    st.metric("💰 최종 자산", f"{total_asset:,}원")
    st.metric("📈 총수익", f"{profit:+,}원")
    st.metric("📊 수익률", f"{profit_rate:+.1f}%")
    st.metric("🧠 투자 성향", style)

    st.subheader("📦 보유 자산")
    for k, v in st.session_state.portfolio.items():
        st.write(f"{k}: {v}개")

    if st.button("🔄 다시 하기"):
        reset_game()
        st.experimental_rerun()
    st.stop()

# ================== 게임 화면 ==================
st.title("🏪 매점 모의 주식 게임")
st.caption("⚠️ 하루에 최소 한 번 매수/매도를 해야 뉴스와 그래프가 갱신됩니다. ▶ 다음 날 버튼으로 보유 개수와 현금이 업데이트됩니다.")
st.write(f"📅 Day {st.session_state.day} / {DAY_LIMIT}")
st.write(f"💰 현금: {st.session_state.cash:,}원")

# 오늘 뉴스
if st.session_state.day in EVENTS:
    st.info(f"📰 오늘 뉴스: {EVENTS[st.session_state.day][0]}")
# 내일 뉴스
if st.session_state.day + 1 in EVENTS:
    trust = random.randint(50, 100)
    st.warning(f"🔮 사전 뉴스: {EVENTS[st.session_state.day+1][0]} (신뢰도 {trust}%)")

# ================== 총자산 표시 ==================
total_asset = calc_total_asset()
profit = total_asset - START_CASH
profit_rate = profit / START_CASH * 100
st.metric("💰 총자산", f"{total_asset:,}원")
st.metric("📈 총수익", f"{profit:+,}원")
st.metric("📊 수익률", f"{profit_rate:+.1f}%")
st.divider()

# ================== 매수 / 매도 ==================
cols = st.columns(len(ITEMS))
for i, name in enumerate(ITEMS):
    stock = st.session_state.stocks[name]
    with cols[i]:
        st.subheader(name)
        st.write(f"{stock['price']:,}원 {arrow(stock['history'])}")
        st.write(f"보유: {st.session_state.portfolio[name]}개")
        if st.button(f"매수 {name}", key=f"buy_{name}"):
            if st.session_state.cash >= stock["price"]:
                st.session_state.cash -= stock["price"]
                st.session_state.portfolio[name] += 1
                st.session_state.risk += 1
        if st.button(f"매도 {name}", key=f"sell_{name}"):
            if st.session_state.portfolio[name] > 0:
                st.session_state.cash += stock["price"]
                st.session_state.portfolio[name] -= 1
                st.session_state.risk -= 1

# ================== 다음 날 ==================
legend = ""
for i, name in enumerate(ITEMS):
    legend += f"<span style='color:{COLORS[i]}'>⬛ {name}</span>&nbsp;&nbsp;"
st.markdown(legend, unsafe_allow_html=True)

next_day_clicked = st.button("▶ 다음 날")
if next_day_clicked:
    if st.session_state.day < DAY_LIMIT:
        st.session_state.day += 1
        update_prices()
    else:
        st.session_state.show_result = True
    st.experimental_rerun()  # 버튼 클릭 시만 rerun

# ================== 그래프 ==================
fig, ax = plt.subplots(figsize=(9, 4), dpi=120)
for i, name in enumerate(ITEMS):
    ax.plot(
        st.session_state.stocks[name]["history"],
        color=COLORS[i],
        linewidth=2,
        label=name,
    )
ax.set_xlabel("Day")
ax.set_ylabel("Price")
ax.grid(alpha=0.3)
ax.legend(fontsize=8)
st.pyplot(fig)
