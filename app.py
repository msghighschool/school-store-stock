import streamlit as st
import random
import matplotlib.pyplot as plt

# ===== 초기 설정 =====
st.set_page_config(page_title="🏪 매점 주식 게임", layout="wide")

DAY_LIMIT = 30
ITEMS = ["이온음료", "오꾸밥", "아이스크림", "젤리", "포켓몬빵"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

def reset_game():
    st.session_state.day = 1
    st.session_state.cash = 50000
    st.session_state.portfolio = {k: 0 for k in ITEMS}
    st.session_state.risk = 0
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
    5: ("중간고사 → 이용 감소", {"전체": -0.15}),
    6: ("시험 과목 多 → 음료 폭증", {"이온음료": 0.4}),
    13: ("단축수업", {"오꾸밥": 0.2}),
    14: ("이동수업 많음", {"전체": -0.1}),
    18: ("급식 맛없음", {"오꾸밥": 0.3, "포켓몬빵": 0.3}),
    20: ("폭염", {"아이스크림": 0.45}),
    25: ("급식 맛있음", {"전체": -0.25}),
}

# ===== 가격 변동 =====
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
            change += random.uniform(-0.25, 0.25)
        new_price = max(500, int(data["price"] * (1 + change)))
        data["price"] = new_price
        data["history"].append(new_price)

# ===== 화살표 표시 =====
def arrow(h):
    if len(h) < 2: return "➖"
    return "▲" if h[-1] > h[-2] else "▼" if h[-1] < h[-2] else "➖"

# ===== UI =====
st.title("🏪 매점 모의 주식 게임")
st.write(f"📅 Day {st.session_state.day} / {DAY_LIMIT}")
st.write(f"💰 현금: {st.session_state.cash:,}원")

if st.session_state.day in EVENTS:
    st.info(f"📰 오늘 이벤트: {EVENTS[st.session_state.day][0]}")
if st.session_state.day + 1 in EVENTS:
    trust = random.randint(50, 100)
    st.warning(f"🔮 사전 뉴스: {EVENTS[st.session_state.day+1][0]} (신뢰도 {trust}%)")

# ===== 매수/매도 버튼 (그래프 갱신 X) =====
cols = st.columns(len(ITEMS))
for i, name in enumerate(ITEMS):
    stock = st.session_state.stocks[name]
    with cols[i]:
        st.subheader(name)
        st.write(f"{stock['price']:,}원 {arrow(stock['history'])}")
        st.write(f"보유 {st.session_state.portfolio[name]}개")
        if st.button(f"매수", key=f"buy_{name}"):
            if st.session_state.cash >= stock["price"]:
                st.session_state.cash -= stock["price"]
                st.session_state.portfolio[name] += 1
                st.session_state.risk += 1
        if st.button(f"매도", key=f"sell_{name}"):
            if st.session_state.portfolio[name] > 0:
                st.session_state.cash += stock["price"]
                st.session_state.portfolio[name] -= 1
                st.session_state.risk -= 1

st.divider()

# ===== 다음 날 버튼 + 메뉴 색 블록 (그래프 위) =====
menu_display = ""
for i, name in enumerate(ITEMS):
    menu_display += f"<span style='color:{colors[i]}'>⬛ {name}</span>  "
st.markdown(menu_display, unsafe_allow_html=True)

if st.button("▶ 다음 날"):
    if st.session_state.day < DAY_LIMIT:
        st.session_state.day += 1
        update_prices()
    else:
        st.session_state.show_result = True
    st.experimental_rerun()  # 오직 다음 날 버튼 클릭 시만 rerun

# ===== 그래프 =====
st.subheader("📈 가격 추이")
fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
for i, name in enumerate(ITEMS):
    ax.plot(st.session_state.stocks[name]["history"], linewidth=2, color=colors[i])
ax.set_xlabel("Day")
ax.set_ylabel("Price")
ax.grid(alpha=0.3)
st.pyplot(fig)

# ===== 결과 페이지 =====
if "show_result" in st.session_state and st.session_state.show_result:
    total = st.session_state.cash
    for name in ITEMS:
        total += st.session_state.stocks[name]["price"] * st.session_state.portfolio[name]

    if st.session_state.risk >= 15:
        style = "공격형 🐯"
    elif st.session_state.risk >= 5:
        style = "균형형 🦊"
    else:
        style = "안정형 🐢"

    st.success(f"🏁 게임 종료\n\n💰 최종 자산: {total:,}원\n📊 투자 성향: {style}")
