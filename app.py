import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ===== 한글 폰트 설정 =====
font_path = "NanumGothic-Regular.ttf"  # NanumGothic.ttf 파일 필요
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = font_prop.get_name()
plt.rcParams["axes.unicode_minus"] = False

# ===== 초기 설정 =====
st.set_page_config(
    page_title="🏪 매점 주식 게임",
    layout="wide",
)

ITEMS = ["이온음료", "오꾸밥", "아이스크림", "젤리", "포켓몬빵"]
DAY_LIMIT = 30

def reset_game():
    st.session_state.page = "game"
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

if "page" not in st.session_state:
    reset_game()

# ===== 이벤트 =====
EVENTS = {
    3: ("모의고사 → 쉬는 시간 증가", {"이온음료": 0.25}),
    5: ("중간고사 → 이용 감소", {"전체": -0.15}),
    6: ("시험 과목 多 → 음료 폭증", {"이온음료": 0.4}),
    13: ("단축수업", {"오꾸밥": 0.2}),
    14: ("이동수업 多", {"전체": -0.1}),
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

def arrow(h):
    if len(h) < 2: return "➖"
    return "▲" if h[-1] > h[-2] else "▼" if h[-1] < h[-2] else "➖"

# ===== 결과 페이지 =====
if st.session_state.page == "result":
    st.title("🏁 모의 투자 결과")

    total = st.session_state.cash
    for name in ITEMS:
        total += st.session_state.stocks[name]["price"] * st.session_state.portfolio[name]

    if st.session_state.risk >= 15:
        style = "공격형 🐯"
    elif st.session_state.risk >= 5:
        style = "균형형 🦊"
    else:
        style = "안정형 🐢"

    st.metric("💰 최종 자산", f"{total:,}원")
    st.metric("📊 투자 성향", style)

    st.subheader("📦 보유 자산")
    for k, v in st.session_state.portfolio.items():
        st.write(f"{k}: {v}개")

    if st.button("🔄 다시 하기"):
        reset_game()
        st.experimental_rerun()

    st.stop()

# ===== 게임 페이지 =====
st.title("🏪 매점 모의 주식 게임")
st.caption("운빨 + 뉴스 + 이벤트 기반 모의 투자")

st.write(f"📅 Day {st.session_state.day} / {DAY_LIMIT}")
st.write(f"💰 현금: {st.session_state.cash:,}원")

if st.session_state.day in EVENTS:
    st.info(f"📰 오늘 이벤트: {EVENTS[st.session_state.day][0]}")

if st.session_state.day + 1 in EVENTS:
    trust = random.randint(50, 100)
    st.warning(f"🔮 사전 뉴스: {EVENTS[st.session_state.day+1][0]} (신뢰도 {trust}%)")

cols = st.columns(len(ITEMS))
for i, name in enumerate(ITEMS):
    stock = st.session_state.stocks[name]
    with cols[i]:
        st.subheader(name)
        st.write(f"{stock['price']:,}원 {arrow(stock['history'])}")
        st.write(f"보유 {st.session_state.portfolio[name]}개")

        if st.button("매수", key=f"b_{name}"):
            if st.session_state.cash >= stock["price"]:
                st.session_state.cash -= stock["price"]
                st.session_state.portfolio[name] += 1
                st.session_state.risk += 1

        if st.button("매도", key=f"s_{name}"):
            if st.session_state.portfolio[name] > 0:
                st.session_state.cash += stock["price"]
                st.session_state.portfolio[name] -= 1
                st.session_state.risk -= 1

st.divider()

if st.button("▶ 다음 날"):
    if st.session_state.day < DAY_LIMIT:
        st.session_state.day += 1
        update_prices()
        st.experimental_rerun()
    else:
        st.session_state.page = "result"
        st.experimental_rerun()

# ===== 그래프 =====
st.subheader("📈 가격 추이")
fig, ax = plt.subplots(figsize=(6, 3))  # 작고 선명하게

for name in ITEMS:
    ax.plot(st.session_state.stocks[name]["history"], linewidth=2, label=name)

ax.legend(fontsize=8, ncol=3, loc="upper center")
ax.grid(alpha=0.3)
ax.set_xlabel("Day")
ax.set_ylabel("Price")

st.pyplot(fig)
