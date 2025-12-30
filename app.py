import streamlit as st
import random
import matplotlib.pyplot as plt

# ================== 기본 설정 ==================
st.set_page_config(page_title="🏪 매점 주식 게임", layout="wide")

DAY_LIMIT = 30
ITEMS = ["이온음료", "오꾸밥", "아이스크림", "젤리", "포켓몬빵"]

# ================== 게임 초기화 ==================
def reset_game():
    st.session_state.day = 1
    st.session_state.cash = 50000
    st.session_state.portfolio = {item: 0 for item in ITEMS}
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
    5: ("중간고사 시작 → 매점 이용 감소", {"전체": -0.15}),
    6: ("시험 과목 多 → 음료 폭증", {"이온음료": 0.4}),
    13: ("단축수업", {"오꾸밥": 0.2}),
    18: ("급식 맛없음", {"오꾸밥": 0.3, "포켓몬빵": 0.3}),
    20: ("폭염", {"아이스크림": 0.45}),
}

# ================== 가격 업데이트 (다음날 전용) ==================
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

# ================== 화살표 ==================
def arrow(history):
    if len(history) < 2:
        return "➖"
    if history[-1] > history[-2]:
        return "▲"
    if history[-1] < history[-2]:
        return "▼"
    return "➖"

# ================== UI ==================
st.title("🏪 매점 모의 주식 게임")
st.write(f"📅 Day {st.session_state.day} / {DAY_LIMIT}")
st.write(f"💰 현금: {st.session_state.cash}원")

# 오늘 뉴스
if st.session_state.day in EVENTS:
    st.info(f"📰 오늘 뉴스: {EVENTS[st.session_state.day][0]}")

# 내일 예측 뉴스
if st.session_state.day + 1 in EVENTS:
    trust = random.randint(50, 100)
    st.warning(f"🔮 내일 예측: {EVENTS[st.session_state.day+1][0]} (신뢰도 {trust}%)")

# ================== 종목 UI ==================
cols = st.columns(len(ITEMS))

for i, name in enumerate(ITEMS):
    stock = st.session_state.stocks[name]

    with cols[i]:
        st.subheader(name)
        st.write(f"{stock['price']}원 {arrow(stock['history'])}")
        st.write(f"보유: {st.session_state.portfolio[name]}개")

        # 매수
        if st.button(f"매수", key=f"buy_{name}"):
            if st.session_state.cash >= stock["price"]:
                st.session_state.cash -= stock["price"]
                st.session_state.portfolio[name] += 1
                st.session_state.risk += 1

        # 매도
        if st.button(f"매도", key=f"sell_{name}"):
            if st.session_state.portfolio[name] > 0:
                st.session_state.cash += stock["price"]
                st.session_state.portfolio[name] -= 1
                st.session_state.risk -= 1

st.divider()

# ================== 다음날 ==================
if st.button("▶ 다음 날"):
    if st.session_state.day < DAY_LIMIT:
        st.session_state.day += 1
        update_prices()
    else:
        st.session_state.show_result = True

# ================== 그래프 ==================
st.subheader("📈 가격 변화")
fig, ax = plt.subplots(figsize=(6, 4))

for name in ITEMS:
    ax.plot(st.session_state.stocks[name]["history"], label=name)

ax.legend(fontsize=8)
ax.set_xlabel("Day")
ax.set_ylabel("가격")
st.pyplot(fig)

# ================== 결과 ==================
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

    st.success(f"🏁 게임 종료\n\n💰 최종 자산: {total}원\n📊 투자 성향: {style}")
    st.stop()
