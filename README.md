### ENGLISH ###

# Option Pricing Engine

**A comprehensive European options pricing tool in Python**

Implementation of three main option pricing methods + Greeks calculation,
delta-hedging simulation and professional PDF report with graphs.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
---

### ✨ Main features

- **Black-Scholes** – analytical solution
- **Monte Carlo simulation** (Geometric Brownian Motion, 100,000+ paths)
- **Binomial Tree** (Cox-Ross-Rubinstein model)
- **Greeks** calculation (Delta, Gamma, Vega, Theta, Rho)
- Basic **delta-hedging** simulation
- Generation of professional **PDF report** including graphs
- Interactive parameter entry at startup

### 📊 Generated outputs
- `option_report_YYYYMMDD_HHMMSS.pdf` (complete report)
- 4 graphs in PNG format:
- Payoff distribution
- Monte Carlo convergence
- Sample price paths
- Delta-hedging error distribution

---

### 🛠 Technology

- Python 3.10+
- NumPy, SciPy, Matplotlib, Seaborn
- fpdf2 (PDF generation)

---

### 🚀 How to run

```bash
# 1. Clone the repository
git clone https://github.com/koldasquare/option-pricing-engine.git
cd option-pricing-engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the program
python option_pricing_engine.py

When running, you can either use the default parameters
or enter your own values ​​(S0, K, T, r, sigma, call/put).

Example output (default parameters)Underlying price (S0): 100
Strike (K): 100
Time to expiration: 1 year
Volatility: 20%
Risk-free rate: 5%

Result prices:Black-Scholes ≈ 10.45
Monte Carlo ≈ 10.4x
Binomial Tree ≈ 10.4x

### Practical use

This tool is suitable for:
- Better understanding of derivatives and quantitative methods
- Quickly testing different options pricing scenarios
- Demonstration of programming and analytical skills in the field of finance / energy trading.

Author: Ing. Lukáš Kolík
LinkedIn: https://www.linkedin.com/in/lukaskolik/
Email: lukaskolik@gmail.com

License: MIT

### Note

The project is still under development.

The plan is to further improve the delta-hedging simulation,
add American options and the ability to save results to Excel.

------------------

### ČESKY ###

# Option Pricing Engine

**Komplexní nástroj pro oceňování evropských opcí v Pythonu**

Implementace tří hlavních metod oceňování opcí + výpočet Greeks,
simulace delta-hedgingu a profesionální PDF report s grafy.

---

### ✨ Hlavní funkce

- **Black-Scholes** – analytické řešení
- **Monte Carlo simulace** (Geometric Brownian Motion, 100 000+ cest)
- **Binomial Tree** (Cox-Ross-Rubinstein model)
- Výpočet **Greeks** (Delta, Gamma, Vega, Theta, Rho)
- Základní simulace **delta-hedgingu**
- Generování profesionálního **PDF reportu** včetně grafů
- Interaktivní zadání parametrů při spuštění

### 📊 Vytvářené výstupy
- `option_report_YYYYMMDD_HHMMSS.pdf` (kompletní report)
- 4 grafy ve formátu PNG:
  - Distribuce payoffů
  - Konvergence Monte Carlo
  - Ukázkové cenové cesty
  - Distribuce chyb delta-hedgingu

---

### 🛠 Technologie

- Python 3.10+
- NumPy, SciPy, Matplotlib, Seaborn
- fpdf2 (PDF generování)

---

### 🚀 Jak spustit

```bash
# 1. Naklonuj repozitář
git clone https://github.com/koldasquare/option-pricing-engine.git
cd option-pricing-engine

# 2. Nainstaluj závislosti
pip install -r requirements.txt

# 3. Spusť program
python option_pricing_engine.py

Při spuštění můžeš buď použít výchozí parametry,
nebo zadat vlastní hodnoty (S0, K, T, r, sigma, call/put).


 Příklad výstupu (výchozí parametry)Podkladová cena (S0): 100
Strike (K): 100
Doba do expirace: 1 rok
Volatilita: 20 %
Bezriziková sazba: 5 %

Výsledné ceny:Black-Scholes ≈ 10.45
Monte Carlo ≈ 10.4x
Binomial Tree ≈ 10.4x

### Praktické využití

Tento nástroj je vhodný pro:
- Lepší porozumění derivátům a kvantitativním metodám
- Rychlé testování různých scénářů oceňování opcí
- Ukázku programovacích a analytických schopností v oblasti financí / energetického tradingu.

Autor: Ing. Lukáš Kolík
LinkedIn: https://www.linkedin.com/in/lukaskolik/
Email: lukaskolik@gmail.com

Licence: MIT


### Poznámka

Projekt je stále ve vývoji.

 V plánu je další vylepšení simulace delta-hedgingu,
přidání amerických opcí a možnost ukládání výsledků do Excelu.


