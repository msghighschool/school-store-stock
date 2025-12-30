import streamlit as st
import random
import matplotlib.pyplot as plt

# ===== 페이지 설정 =====
st.set_page_config(page_title="🏪 매점 주식 게임", layout="wide")

# ===== 상수 =====
DAY_LIMIT = 30
ITEMS = ["이온음료", "오꾸밥", "아이스크림", "젤리", "포켓몬빵"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

# ===== 초기화 함수 =====
def reset_game():
    st.session_state.day = 1
    st.session_state.cash = 50000
    st.session_state.risk = 0
    st.session_state.portfolio = {k: 0 for k in ITEMS}
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

# ===== 이벤트 =====
EVENTS = {
    3: ("모의고사 → 쉬는 시간 증가", {"이온음료": 0.25}),
    5: ("중간고사 시작 → 매점 이용 감소", {"전체": -0.15}),
    6: ("시험 과목 多 → 음료 폭증", {"이온음료": 0.4}),
    13: ("단축수업", {"오꾸밥": 0.2}),
    14: ("이동수업 많음", {"전체": -0.1}),
    18: ("급식 맛없음", {"오꾸밥": 0.3, "포켓몬빵": 0.3}),
    20: ("폭염", {"아이스크림": 0.45}),
    25: ("급식 맛있음", {"전체": -0.25}),
}

# ===== 가격 변동 함수 =====
def update_prices():
    for name, data in st.session_state.stocks.items():
        change = random.uniform(-data["vol"], data["vol"])
        if st.session_state.day in EVENTS:
            _, effect = EVENTS[st.session_state.day]
            trust = random.randint(50, 100)
            if random.random() < trust / 100:
                if name in effect:
                    change += effect[name]
                elif "전체" in effect:
                    change += effect["전체"]
        if random.random() < 0.15:
            change += random.uniform(-0.3, 0.3)
        new_price = max(500, int(data["price"] * (1 + change)))
        data["price"] = new_price
        data["history"].append(new_price)

def arrow(h):
    if len(h) < 2: return "➖"
    if h[-1] > h[-2]: return "▲"
    if h[-1] < h[-2]: return "▼"
    return "➖"

# ===== UI: 게임 상태 =====
st.title("🏪 매점 모의 주식 게임")
st.write(f"📅 Day {st.session_state.day} / {DAY_LIMIT}")
st.write(f"💰 현금: {st.session_state.cash}원")

if st.session_state.day in EVENTS:
    st.info(f"📰 오늘 이벤트: {EVENTS[st.session_state.day][0]}")
if st.session_state.day + 1 in EVENTS:
    trust = random.randint(50, 100)
    st.warning(f"🔮 사전 뉴스: {EVENTS[st.session_state.day+1][0]} (신뢰도 {trust}%)")

# ===== 매수/매도 버튼 =====
cols = st.columns(len(ITEMS))
for i, name in enumerate(ITEMS):
    stock = st.session_state.stocks[name]
    with cols[i]:
        st.subheader(name)
        st.write(f"{stock['price']}원 {arrow(stock['history'])}")
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

st.divider()


# ===== 다음 날 버튼 =====
if st.button("▶ 다음 날"):
    if st.session_state.day < DAY_LIMIT:
        st.session_state.day += 1
        update_prices()
    else:
        st.session_state.show_result = True


# ================== 그래프 ==================
st.subheader("📈 가격 변화")

# 메뉴 색상 안내 (그래프 바로 위)
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
menu_text = ""
for i, name in enumerate(ITEMS):
    menu_text += f"<span style='color:{colors[i]}'>⬛ {name}</span>&nbsp;&nbsp;"
st.markdown(menu_text, unsafe_allow_html=True)

# 그래프 크기 축소 + 해상도 조정
fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=120)

for i, name in enumerate(ITEMS):
    ax.plot(
        st.session_state.stocks[name]["history"],
        linewidth=2,
        color=colors[i]
    )

ax.set_xlabel("Day", fontsize=9)
ax.set_ylabel("가격", fontsize=9)
ax.grid(alpha=0.3)

st.pyplot(fig)


# ===== 게임 종료 결과 =====
if st.session_state.show_result:
    total = st.session_state.cash
    for name in ITEMS:
        total += st.session_state.stocks[name]["price"] * st.session_state.portfolio[name]
    if st.session_state.risk >= 15:
        style = "공격형 🐯"
    elif st.session_state.risk >= 5:
        style = "균형형 🦊"
    else:
        style = "안정형 🐢"
    st.success(f"🏁 게임 종료\n💰 최종 자산: {total}원\n📊 투자 성향: {style}")
    st.stop()


