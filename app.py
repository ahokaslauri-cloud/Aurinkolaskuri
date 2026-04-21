import re
import math
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Aurinkosähköjärjestelmän Kannattavuusraportti", layout="wide")

MONTHS = ['Tammi', 'Helmi', 'Maalis', 'Huhti', 'Touko', 'Kesä', 'Heinä', 'Elo', 'Syys', 'Loka', 'Marras', 'Joulu']


def parse_input(text: str) -> list[float]:
    lines = text.strip().split('\n') if text.strip() else []
    data = []
    number_regex = r'([0-9]+([,\.][0-9]+)?)'

    for line in lines:
        match = re.search(number_regex, line)
        if match:
            number = float(match.group(1).replace(',', '.'))
            data.append(number)
        else:
            data.append(0.0)

    return data


def fmt_fi(value: float, decimals: int = 0) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", " ")


def analyze(consumption_data, production_data, system_power, initial_investment, subsidy,
            buy_price, sell_price, daytime_consumption_percentage):
    if len(consumption_data) < 12 or len(production_data) < 12:
        raise ValueError("Syötä 12 kuukauden tiedot.")

    consumption_data = consumption_data[:12]
    production_data = production_data[:12]

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
    df = pd.DataFrame({
        "Kuukausi": MONTHS,
        "Kulutus (kWh)": consumption_data,
        "Tuotanto (kWh)": production_data,
    })

    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(MONTHS))
    width = 0.38

    ax.bar([i - width / 2 for i in x], df["Kulutus (kWh)"], width=width, label="Kulutus (kWh)")
    ax.bar([i + width / 2 for i in x], df["Tuotanto (kWh)"], width=width, label="Tuotanto (kWh)")

    ax.set_xticks(list(x))
    ax.set_xticklabels(MONTHS)
    ax.set_ylabel("kWh")
    ax.set_title("Kuukausittainen kulutus ja tuotanto")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    st.pyplot(fig)


st.title("Aurinkosähköanalyysi: Energia & Kannattavuus")
st.write("Syötä järjestelmän teho, kustannukset ja energiaprofiilit. Ohjelma laskee takaisinmaksuajan ja järjestelmän yksikköhinnan.")

st.subheader("Järjestelmän tiedot ja taloudelliset parametrit")

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

st.subheader("Syöttötiedot")

default_consumption = "1500\n1400\n1300\n1000\n800\n700\n600\n750\n900\n1200\n1450\n1600"
default_production = "61\n180\n423\n526\n667\n666\n658\n543\n337\n178\n50\n24"

st.subheader("Syöttötiedot")

months_full = [
    "Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu",
    "Toukokuu", "Kesäkuu", "Heinäkuu", "Elokuu",
    "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"
]

default_consumption = [1500,1400,1300,1000,800,700,600,750,900,1200,1450,1600]
default_production = [61,180,423,526,667,666,658,543,337,178,50,24]

df = pd.DataFrame({
    "Kuukausi": months_full,
    "Kulutus (kWh)": default_consumption,
    "Tuotanto (kWh)": default_production
})

edited_df = st.data_editor(
    df,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        "Kuukausi": st.column_config.TextColumn(disabled=True),
        "Kulutus (kWh)": st.column_config.NumberColumn(),
        "Tuotanto (kWh)": st.column_config.NumberColumn()
    }
)

consumption_data = edited_df["Kulutus (kWh)"].tolist()
production_data = edited_df["Tuotanto (kWh)"].tolist()

if st.button("Laske ja piirrä kaavio", use_container_width=True):
    try:
        consumption_data = parse_input(consumption_input)
        production_data = parse_input(production_input)

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
