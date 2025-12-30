import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ================== 페이지 설정 ==================
st.set_page_config(page_title="🏪 매점 주식 게임", layout="wide")

# ================== 한글 폰트 (있으면 적용) ==================
try:
    font_path = "NanumGothic-Regular.ttf"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = font_prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False
except:
    pass  # 폰트 없어도 실행되게

# ================== 상수 ==================
DAY_LIMIT = 30
ITEMS = ["이온음료", "오꾸밥", "아이스크림", "젤리", "포켓몬빵"]
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

# ================== 초기화 ==================
def reset_game():
    st.session_state.day = 1
    st.session_state.cash = 50000
    st.session_state.risk = 0
    st.session_state.portfolio = {k: 0 for k in ITEMS}
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
    3: ("모의고사", {"이온음료": 0.25}),
    5: ("중간고사", {"전체": -0.15}),
    6: ("시험 과목 多", {"이온음료": 0.4}),
    18: ("급식 맛없음", {"오꾸밥": 0.3, "포켓몬빵": 0.3}),
    20: ("폭염", {"아이스크림": 0.45}),
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

        new_price = max(500, int(data["price"] * (1 + change)))
        data["price"] = new_price
        data["history"].append(new_price)

def arrow(h):
    if len(h) < 2: return "➖"
    return "▲" if h[-1] > h[-2] else "▼"

# ================== UI ==================
st.title("🏪 매점 모의 주식 게임")
st.write(f"📅 Day {st.session_state.day} / {DAY_LIMIT}")
st.write(f"💰 현금: {st.session_state.cash:,}원")

if st.session_state.day in EVENTS:
    st.info(f"📰 오늘 이벤트: {EVENTS[st.session_state.day][0]}")

# ================== 매수 / 매도 ==================
cols = st.columns(len(ITEMS))
for i, name in enumerate(ITEMS):
    stock = st.session_state.stocks[name]
    with cols[i]:
        st.subheader(name)
        st.write(f"{stock['price']:,}원 {arrow(stock['history'])}")
        st.write(f"보유 {st.session_state.portfolio[name]}개")

        if st.button("매수", key=f"buy_{name}"):
            if st.session_state.cash >= stock["price"]:
                st.session_state.cash -= stock["price"]
                st.session_state.portfolio[name] += 1
                st.session_state.risk += 1

        if st.button("매도", key=f"sell_{name}"):
            if st.session_state.portfolio[name] > 0:
                st.session_state.cash += stock["price"]
                st.session_state.portfolio[name] -= 1
                st.session_state.risk -= 1

st.divider()

# ================== 다음 날 ==================
if st.button("▶ 다음 날"):
    if st.session_state.day < DAY_LIMIT:
        st.session_state.day += 1
        update_prices()

# ================== 그래프 ==================
st.subheader("📈 가격 추이")

# 그래프 위 색상 안내
legend_text = ""
for i, name in enumerate(ITEMS):
    legend_text += f"<span style='color:{COLORS[i]}'>⬛ {name}</span>&nbsp;&nbsp;"
st.markdown(legend_text, unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=120)
for i, name in enumerate(ITEMS):
    ax.plot(st.session_state.stocks[name]["history"], color=COLORS[i], linewidth=2)

ax.set_xlabel("Day", fontsize=9)
ax.set_ylabel("가격", fontsize=9)
ax.grid(alpha=0.3)

st.pyplot(fig)

# ================== 리셋 ==================
if st.button("🔄 처음부터"):
    reset_game()
