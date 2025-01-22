import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def berechne_monatliche_rate(kreditsumme, zinssatz, laufzeit):
    """Berechnet die monatliche Kreditrate nach Annuitätenformel."""
    zinssatz_monatlich = zinssatz / 12 / 100
    monate = laufzeit * 12
    rate = (kreditsumme * zinssatz_monatlich) / (1 - (1 + zinssatz_monatlich) ** -monate)
    return rate

def generiere_annuitaetentabelle(kreditsumme, zinssatz, laufzeit):
    """Erstellt eine Annuitätentabelle mit monatlichen Zins- und Tilgungsanteilen."""
    zinssatz_monatlich = zinssatz / 12 / 100
    monate = laufzeit * 12
    restschuld = kreditsumme
    rate = berechne_monatliche_rate(kreditsumme, zinssatz, laufzeit)

    daten = []
    for monat in range(1, monate + 1):
        zinsanteil = restschuld * zinssatz_monatlich
        tilgungsanteil = rate - zinsanteil
        restschuld -= tilgungsanteil
        daten.append((monat, round(rate, 2), round(zinsanteil, 2), round(tilgungsanteil, 2), round(restschuld, 2)))

    return pd.DataFrame(daten, columns=["Monat", "Rate (€)", "Zinsanteil (€)", "Tilgungsanteil (€)", "Restschuld (€)"])

def plot_finanzierungsverlauf(laufzeit, gesamtkosten_kfw, gesamtkosten_bank):
    """Stellt den finanziellen Verlauf grafisch dar."""
    monate = np.arange(1, laufzeit * 12 + 1)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monate, gesamtkosten_kfw, label="KfW-Finanzierung", linestyle="-")
    ax.plot(monate, gesamtkosten_bank, label="Normale Bankfinanzierung", linestyle="--")
    
    ax.set_xlabel("Monate")
    ax.set_ylabel("Gesamtkosten (€)")
    ax.set_title("Vergleich der Finanzierungsmodelle")
    ax.legend()
    ax.grid()
    
    st.pyplot(fig)

def berechne_gesamtbelastung(rate, laufzeit, investition=0, ersparnis=0):
    """Berechnet die gesamte Belastung am Ende der Laufzeit."""
    monate = laufzeit * 12
    gesamtbelastung = (rate * monate) + investition
    energieersparnis_gesamt = ersparnis * laufzeit
    return gesamtbelastung, energieersparnis_gesamt

st.title("Vergleich der Immobilienfinanzierung")

# Benutzer-Inputs
gesamtfinanzierung = st.number_input("Gesamtkreditsumme (€)", value=750000, step=1000)
kfw_kredit = st.number_input("KfW-Kredit (€)", value=100000, step=1000, max_value=gesamtfinanzierung)
bank_kredit = gesamtfinanzierung - kfw_kredit
zinssatz_kfw = st.number_input("Zinssatz KfW (%)", value=2.4, step=0.1)
zinssatz_bank = st.number_input("Zinssatz Bank (%)", value=2.75, step=0.1)
laufzeit = st.number_input("Laufzeit (Jahre)", value=20, step=1)
investition = st.number_input("Investition für Förderfähigkeit (€)", value=6000, step=1000)
energieersparnis = st.number_input("Jährliche Energieersparnis (€)", value=800, step=100)

# Kreditraten berechnen
rate_kfw = berechne_monatliche_rate(kfw_kredit, zinssatz_kfw, laufzeit)
rate_bank = berechne_monatliche_rate(bank_kredit, zinssatz_bank, laufzeit)
rate_bank_full = berechne_monatliche_rate(gesamtfinanzierung, zinssatz_bank, laufzeit)

gesamtrate_kfw = rate_kfw + rate_bank - (energieersparnis / 12)
gesamtrate_bank = rate_bank_full

# Gesamtbelastungen berechnen
gesamtbelastung_kfw, ersparnis_kfw = berechne_gesamtbelastung(gesamtrate_kfw, laufzeit, investition, energieersparnis)
gesamtbelastung_bank, _ = berechne_gesamtbelastung(gesamtrate_bank, laufzeit)
vorteil_kfw = gesamtbelastung_bank - gesamtbelastung_kfw

# Ergebnisse anzeigen
st.write("### Wirtschaftlichkeit der Modelle")
st.write(f"Gesamtbelastung KfW-Modell: {gesamtbelastung_kfw:.2f} €")
st.write(f"Gesamtbelastung Bankfinanzierung: {gesamtbelastung_bank:.2f} €")
st.write(f"Energieersparnis über die Laufzeit (nur KfW-Modell): {ersparnis_kfw:.2f} €")
if vorteil_kfw > 0:
    st.write(f"Das KfW-Modell ist wirtschaftlicher mit einem Vorteil von {vorteil_kfw:.2f} €.")
else:
    st.write(f"Die Bankfinanzierung ist wirtschaftlicher mit einem Vorteil von {abs(vorteil_kfw):.2f} €.")

# Finanzierungsverlauf plotten
gesamtkosten_kfw = np.cumsum(np.full(laufzeit * 12, gesamtrate_kfw))
gesamtkosten_bank = np.cumsum(np.full(laufzeit * 12, gesamtrate_bank))
plot_finanzierungsverlauf(laufzeit, gesamtkosten_kfw, gesamtkosten_bank)

# Annuitätentabellen anzeigen
col1, col2, col3 = st.columns(3)
with col1:
    st.write("### Annuitätentabelle KfW-Darlehen")
    st.dataframe(generiere_annuitaetentabelle(kfw_kredit, zinssatz_kfw, laufzeit))
with col2:
    st.write("### Annuitätentabelle Bank-Darlehen (Restbetrag)")
    st.dataframe(generiere_annuitaetentabelle(bank_kredit, zinssatz_bank, laufzeit))
with col3:
    st.write("### Annuitätentabelle Bank-Darlehen (Gesamtfinanzierung)")
    st.dataframe(generiere_annuitaetentabelle(gesamtfinanzierung, zinssatz_bank, laufzeit))
