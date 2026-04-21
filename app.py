import math
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Aurinkosähköanalyysi",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0b0c10 0%, #111318 100%);
}

.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hero */
.hero-wrap {
    text-align: center;
    margin-bottom: 2rem;
}

.hero-title {
    color: #F2C94C;
    font-size: 2.9rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin-bottom: 0.35rem;
}

.hero-subtitle {
    color: #F2C94C;
    font-size: 1.12rem;
    font-weight: 500;
    opacity: 0.88;
    margin-bottom: 0.9rem;
}

.hero-line {
    width: 140px;
    height: 3px;
    background: linear-gradient(90deg, rgba(242,201,76,0.15), #F2C94C, rgba(242,201,76,0.15));
    border-radius: 999px;
    margin: 0 auto;
}

/* Headings */
h1, h2, h3 {
    color: #F2C94C !important;
    font-weight: 700;
    letter-spacing: -0.01em;
}

/* General text */
p, label, span, div {
    color: #EAEAEA;
}

/* Cards */
.custom-card {
    background: rgba(26, 29, 33, 0.96);
    border: 1px solid #2B2F36;
    border-radius: 18px;
    padding: 1.35rem 1.35rem 1.15rem 1.35rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
}

.card-divider {
    border: none;
    border-top: 1px solid #343942;
    margin: 0.45rem 0 1rem 0;
}

/* Inputs */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background-color: #121417 !important;
    color: #FFFFFF !important;
    border: 1px solid #2A2E33 !important;
    border-radius: 10px !important;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label {
    color: #DADDE2 !important;
    font-weight: 500;
}

.month-header {
    color: #DADDE2;
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.month-label input {
    font-weight: 600 !important;
    background-color: #171A1F !important;
    color: #FFFFFF !important;
    border: 1px solid #30343B !important;
}

/* Button */
div[data-testid="stButton"] button {
    background: #F2C94C;
    color: #111111 !important;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.72rem 1.25rem;
    box-shadow: 0 6px 18px rgba(242, 201, 76, 0.28);
}

div[data-testid="stButton"] button:hover {
    background: #E0B93F;
    color: #111111 !important;
}

/* Result cards */
.results-title {
    color: #F2C94C;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

.metric-card {
    background: #181B20;
    border: 1px solid #2C3139;
    border-radius: 16px;
    padding: 1rem 1rem 0.9rem 1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    height: 100%;
}

.metric-label {
    color: #C7CBD1 !important;
    font-size: 0.95rem;
    margin-bottom: 0.45rem;
}

.metric-value {
    color: #F2C94C !important;
    font-size: 1.95rem;
    font-weight: 750;
    line-height: 1.1;
}

.sub-metric-value {
    color: #F3F4F6 !important;
    font-size: 1.75rem;
    font-weight: 720;
    line-height: 1.1;
}

.metric-unit {
    color: #D8DADF !important;
    font-size: 1rem;
    font-weight: 500;
    margin-left: 0.25rem;
}

.subtle-line {
    border: none;
    border-top: 1px solid #343942;
    margin-top: 1.1rem;
    margin-bottom: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

/* ===== POISTA STREAMLIT YLÄPALKKI ===== */
header {
    visibility: hidden;
    height: 0px;
}

/* poistaa ylimääräisen tyhjän tilan */
.block-container {
    padding-top: 1rem !important;
}

MONTHS_SHORT = [
    "Tammi", "Helmi", "Maalis", "Huhti", "Touko", "Kesä",
    "Heinä", "Elo", "Syys", "Loka", "Marras", "Joulu"
]

MONTHS_FULL = [
    "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu",
    "Toukokuu", "Kesäkuu", "Heinäkuu", "Elokuu",
    "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
]


def fmt_fi(value: float, decimals: int = 0) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", " ")


def clean_numeric_list(values, expected_len=12):
    cleaned = []
    for v in values[:expected_len]:
        if pd.isna(v):
            cleaned.append(0.0)
        else:
            cleaned.append(float(v))
    while len(cleaned) < expected_len:
        cleaned.append(0.0)
    return cleaned


def analyze(
    consumption_data,
    production_data,
    system_power,
    initial_investment,
    subsidy,
    buy_price,
    sell_price,
    daytime_consumption_percentage
):
    if len(consumption_data) < 12 or len(production_data) < 12:
        raise ValueError("Syötä 12 kuukauden tiedot.")

    consumption_data = clean_numeric_list(consumption_data, 12)
    production_data = clean_numeric_list(production_data, 12)

    day_use_percentage = daytime_consumption_percentage / 100.0
    net_investment = initial_investment - subsidy

    total_consumption = sum(consumption_data)
    total_production = sum(production_data)

    total_self_cons = 0.0
    total_grid_buy = 0.0
    total_grid_sell = 0.0

    for i in range(12):
        day_cons = consumption_data[i] * day_use_percentage
        night_cons = consumption_data[i] * (1 - day_use_percentage)
        self_cons = min(day_cons, production_data[i])

        total_self_cons += self_cons
        total_grid_sell += max(0.0, production_data[i] - day_cons)
        total_grid_buy += night_cons + max(0.0, day_cons - production_data[i])

    annual_savings = (total_self_cons * buy_price) + (total_grid_sell * sell_price)
    payback_time = (net_investment / annual_savings) if annual_savings > 0 else math.inf
    roi = ((annual_savings / net_investment) * 100) if net_investment > 0 else 0.0
    price_per_kwp = (net_investment / system_power) if system_power > 0 else 0.0
    self_consumption_rate = ((total_self_cons / total_production) * 100) if total_production > 0 else 0.0

    return {
        "consumption_data": consumption_data,
        "production_data": production_data,
        "net_investment": net_investment,
        "total_consumption": total_consumption,
        "total_production": total_production,
        "total_self_cons": total_self_cons,
        "total_grid_buy": total_grid_buy,
        "total_grid_sell": total_grid_sell,
        "annual_savings": annual_savings,
        "payback_time": payback_time,
        "roi": roi,
        "price_per_kwp": price_per_kwp,
        "self_consumption_rate": self_consumption_rate,
        "system_power": system_power,
    }


def render_chart(consumption_data, production_data):
    fig, ax = plt.subplots(figsize=(12, 4.8))
    fig.patch.set_facecolor("#1A1D21")
    ax.set_facecolor("#1A1D21")

    x = range(len(MONTHS_SHORT))
    width = 0.36

    ax.bar(
        [i - width / 2 for i in x],
        consumption_data,
        width=width,
        label="Kulutus",
        color="#F2C94C",
        edgecolor="#E0B93F"
    )
    ax.bar(
        [i + width / 2 for i in x],
        production_data,
        width=width,
        label="Tuotanto",
        color="#4B5563",
        edgecolor="#6B7280"
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(MONTHS_SHORT, color="#DADDE2")
    ax.set_ylabel("kWh", color="#DADDE2")
    ax.set_title("Kuukausittainen kulutus ja tuotanto", color="#F2C94C", pad=14)
    ax.tick_params(axis="y", colors="#DADDE2")
    ax.spines["bottom"].set_color("#3A3F47")
    ax.spines["left"].set_color("#3A3F47")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#31353C", alpha=0.9, linestyle="-", linewidth=0.8)

    legend = ax.legend(frameon=False)
    for text in legend.get_texts():
        text.set_color("#EAEAEA")

    st.pyplot(fig)


def metric_card(label, value, unit="", highlight=False):
    value_class = "metric-value" if highlight else "sub-metric-value"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="{value_class}">{value}<span class="metric-unit">{unit}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-title">Aurinkosähköanalyysi</div>
        <div class="hero-subtitle">Energia, omakäyttö ja kannattavuus yhdellä näkymällä.</div>
        <div class="hero-line"></div>
    </div>
    """,
    unsafe_allow_html=True
)

default_consumption = [1500, 1400, 1300, 1000, 800, 700, 600, 750, 900, 1200, 1450, 1600]
default_production = [61, 180, 423, 526, 667, 666, 658, 543, 337, 178, 50, 24]

if "consumption_data" not in st.session_state:
    st.session_state.consumption_data = default_consumption.copy()

if "production_data" not in st.session_state:
    st.session_state.production_data = default_production.copy()

st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.subheader("Järjestelmä ja hinnat")
st.markdown('<hr class="card-divider">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    system_power = st.number_input("Järjestelmän teho (kWp)", min_value=0.1, value=5.0, step=0.1)
    initial_investment = st.number_input("Alkuinvestointi (€)", min_value=0.0, value=7500.0, step=100.0)
    subsidy = st.number_input("Hankintatuet (€)", min_value=0.0, value=0.0, step=100.0)
    system_lifetime = st.number_input("Järjestelmän elinikä (vuotta)", min_value=1, value=30, step=1)

with col2:
    buy_price = st.number_input("Ostetun sähkön hinta (€/kWh)", min_value=0.0, value=0.150, step=0.001, format="%.3f")
    sell_price = st.number_input("Myydyn sähkön hinta (€/kWh)", min_value=0.0, value=0.050, step=0.001, format="%.3f")
    daytime_consumption_percentage = st.number_input("Kulutuksen osuus päiväaikaan (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.subheader("Kuukausitiedot")
st.markdown('<hr class="card-divider">', unsafe_allow_html=True)

h1, h2, h3 = st.columns([2, 2, 2])
with h1:
    st.markdown('<div class="month-header">Kuukausi</div>', unsafe_allow_html=True)
with h2:
    st.markdown('<div class="month-header">Kulutus (kWh)</div>', unsafe_allow_html=True)
with h3:
    st.markdown('<div class="month-header">Tuotanto (kWh)</div>', unsafe_allow_html=True)

consumption_data = []
production_data = []

for i, month in enumerate(MONTHS_FULL):
    c1, c2, c3 = st.columns([2, 2, 2])

    with c1:
        st.markdown('<div class="month-label">', unsafe_allow_html=True)
        st.text_input(
            f"Kuukausi_{i}",
            value=month,
            disabled=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        cons_val = st.number_input(
            f"Kulutus_{i}",
            min_value=0.0,
            value=float(st.session_state.consumption_data[i]),
            step=1.0,
            format="%.0f",
            label_visibility="collapsed"
        )
        consumption_data.append(cons_val)

    with c3:
        prod_val = st.number_input(
            f"Tuotanto_{i}",
            min_value=0.0,
            value=float(st.session_state.production_data[i]),
            step=1.0,
            format="%.0f",
            label_visibility="collapsed"
        )
        production_data.append(prod_val)

st.session_state.consumption_data = consumption_data
st.session_state.production_data = production_data

st.markdown("<div style='margin-top: 0.9rem;'></div>", unsafe_allow_html=True)
calculate = st.button("Laske ja piirrä kaavio", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

if calculate:
    try:
        result = analyze(
            consumption_data=consumption_data,
            production_data=production_data,
            system_power=system_power,
            initial_investment=initial_investment,
            subsidy=subsidy,
            buy_price=buy_price,
            sell_price=sell_price,
            daytime_consumption_percentage=daytime_consumption_percentage,
        )

        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-title">Tulokset</div>', unsafe_allow_html=True)
        st.markdown('<hr class="card-divider">', unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            metric_card("Vuosikulutus", fmt_fi(result["total_consumption"], 0), "kWh", highlight=True)
        with r2:
            metric_card("Vuosituotanto", fmt_fi(result["total_production"], 0), "kWh", highlight=True)
        with r3:
            metric_card("Omakäyttö", fmt_fi(result["total_self_cons"], 0), "kWh", highlight=True)

        r4, r5, r6 = st.columns(3)
        with r4:
            metric_card("Nettokustannus", fmt_fi(result["net_investment"], 2), "€")
        with r5:
            metric_card("Yksikköhinta", fmt_fi(result["price_per_kwp"], 2), "€/kWp")
        with r6:
            metric_card("Vuotuinen tuotto", fmt_fi(result["annual_savings"], 2), "€")

        r7, r8, r9 = st.columns(3)
        with r7:
            if math.isinf(result["payback_time"]):
                metric_card("Takaisinmaksuaika", "Ei toteudu", "")
            else:
                metric_card("Takaisinmaksuaika", fmt_fi(result["payback_time"], 1), "vuotta")
        with r8:
            metric_card("ROI", fmt_fi(result["roi"], 1), "%")
        with r9:
            metric_card("Omakäyttöaste", fmt_fi(result["self_consumption_rate"], 1), "%")

        st.markdown('<hr class="subtle-line">', unsafe_allow_html=True)
        render_chart(result["consumption_data"], result["production_data"])
        st.markdown('</div>', unsafe_allow_html=True)

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Tapahtui virhe: {e}")
