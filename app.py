import math
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Aurinkosähköjärjestelmän Kannattavuusraportti",
    layout="wide"
)

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
    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(MONTHS_SHORT))
    width = 0.38

    ax.bar(
        [i - width / 2 for i in x],
        consumption_data,
        width=width,
        label="Kulutus (kWh)"
    )
    ax.bar(
        [i + width / 2 for i in x],
        production_data,
        width=width,
        label="Tuotanto (kWh)"
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(MONTHS_SHORT)
    ax.set_ylabel("kWh")
    ax.set_title("Kuukausittainen kulutus ja tuotanto")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    st.pyplot(fig)


st.title("Aurinkosähköanalyysi: Energia & Kannattavuus")
st.write(
    "Syötä järjestelmän teho, kustannukset ja energiaprofiilit. "
    "Ohjelma laskee takaisinmaksuajan ja järjestelmän yksikköhinnan."
)

st.subheader("Järjestelmän tiedot ja taloudelliset parametrit")

col1, col2 = st.columns(2)

with col1:
    system_power = st.number_input(
        "Järjestelmän teho (kWp)",
        min_value=0.1,
        value=5.0,
        step=0.1
    )
    initial_investment = st.number_input(
        "Alkuinvestointi (€)",
        min_value=0.0,
        value=7500.0,
        step=100.0
    )
    subsidy = st.number_input(
        "Hankintatuet (€)",
        min_value=0.0,
        value=0.0,
        step=100.0
    )
    system_lifetime = st.number_input(
        "Järjestelmän elinikä (vuotta)",
        min_value=1,
        value=30,
        step=1
    )

with col2:
    buy_price = st.number_input(
        "Ostetun sähkön hinta (€/kWh)",
        min_value=0.0,
        value=0.150,
        step=0.001,
        format="%.3f"
    )
    sell_price = st.number_input(
        "Myydyn sähkön hinta (€/kWh)",
        min_value=0.0,
        value=0.050,
        step=0.001,
        format="%.3f"
    )
    daytime_consumption_percentage = st.number_input(
        "Kulutuksen osuus päiväaikaan (%)",
        min_value=0.0,
        max_value=100.0,
        value=40.0,
        step=1.0
    )

st.subheader("Syöttötiedot")

months_full = [
    "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu",
    "Toukokuu", "Kesäkuu", "Heinäkuu", "Elokuu",
    "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
]

default_consumption = [1500, 1400, 1300, 1000, 800, 700, 600, 750, 900, 1200, 1450, 1600]
default_production = [61, 180, 423, 526, 667, 666, 658, 543, 337, 178, 50, 24]

if "consumption_data" not in st.session_state:
    st.session_state.consumption_data = default_consumption.copy()

if "production_data" not in st.session_state:
    st.session_state.production_data = default_production.copy()

header1, header2, header3 = st.columns([2, 2, 2])
with header1:
    st.markdown("**Kuukausi**")
with header2:
    st.markdown("**Kulutus (kWh)**")
with header3:
    st.markdown("**Tuotanto (kWh)**")

consumption_data = []
production_data = []

for i, month in enumerate(months_full):
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.text_input(
            f"Kuukausi_{i}",
            value=month,
            disabled=True,
            label_visibility="collapsed"
        )

    with col2:
        cons_val = st.number_input(
            f"Kulutus_{i}",
            min_value=0.0,
            value=float(st.session_state.consumption_data[i]),
            step=1.0,
            format="%.0f",
            label_visibility="collapsed"
        )
        consumption_data.append(cons_val)

    with col3:
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

if st.button("Laske ja piirrä kaavio", use_container_width=True):
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

        st.subheader("Tulokset")

        st.markdown("### Järjestelmän kustannustehokkuus")
        st.write(f"Järjestelmän nimellisteho: **{fmt_fi(result['system_power'], 1)} kWp**")
        st.write(f"Nettokustannus (Alkuinvestointi - Tuet): **{fmt_fi(result['net_investment'], 2)} €**")
        st.success(f"Järjestelmän yksikköhinta: {fmt_fi(result['price_per_kwp'], 2)} €/kWp")

        st.markdown("### Energiatase (kWh/a)")
        st.write(
            f"Vuosikulutus: {fmt_fi(result['total_consumption'], 0)} kWh | "
            f"Vuosituotanto: {fmt_fi(result['total_production'], 0)} kWh"
        )
        st.write(
            f"Simuloitu omakäyttö: {fmt_fi(result['total_self_cons'], 0)} kWh "
            f"({fmt_fi(result['self_consumption_rate'], 1)} %)"
        )
        st.write(
            f"Ostettu verkosta: {fmt_fi(result['total_grid_buy'], 0)} kWh | "
            f"Myyty verkkoon: {fmt_fi(result['total_grid_sell'], 0)} kWh"
        )

        st.markdown("### Taloudellinen tuotto")
        st.write(f"Vuotuinen säästö ja myyntitulo yhteensä: **{fmt_fi(result['annual_savings'], 2)} €**")

        if math.isinf(result["payback_time"]):
            st.info("Takaisinmaksuaika: Ei toteudu")
        else:
            st.info(f"Takaisinmaksuaika: {fmt_fi(result['payback_time'], 1)} vuotta")

        st.info(f"Sijoitetun pääoman tuotto (ROI): {fmt_fi(result['roi'], 1)} %")

        st.subheader("Kaavio")
        render_chart(result["consumption_data"], result["production_data"])

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Tapahtui virhe: {e}")
