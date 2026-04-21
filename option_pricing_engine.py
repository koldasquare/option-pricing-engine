# %%
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import tempfile
import os
import platform
import subprocess
from typing import Dict, Tuple


class OptionPricingEngine:
    """
    Option Pricing Engine - kompletní nástroj pro oceňování evropských opcí.
    
    Podporuje:
    - Black-Scholes (analytické řešení)
    - Monte Carlo simulace (100 000+ cest)
    - Binomial Tree (CRR model)
    - Výpočet Greeks (Delta, Gamma, Vega, Theta, Rho)
    - Jednoduchou simulaci delta-hedgingu
    - Vizualizace (payoff distribuce, konvergence MC, stock paths)
    
    Parametry opce jsou zadávány při inicializaci třídy.
    Autor: Ing. Lukáš Kolík
    """

    def __init__(self, S0: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"):
        """
        Inicializace parametrů opce.
        
        Parametry:
            S0 (float): Aktuální cena podkladového aktiva
            K (float): Strike cena
            T (float): Čas do expirace v letech
            r (float): Bezriziková úroková sazba
            sigma (float): Volatilita (roční)
            option_type (str): 'call' nebo 'put'
        """
        if option_type not in ["call", "put"]:
            raise ValueError("option_type musí být 'call' nebo 'put'")
        
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.option_type = option_type.lower()
        
        # Precompute d1 and d2 pro Black-Scholes a Greeks
        self.d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        self.d2 = self.d1 - sigma * np.sqrt(T)

    def black_scholes_price(self) -> float:
        """Analytické řešení podle Black-Scholes modelu."""
        if self.option_type == "call":
            price = self.S0 * norm.cdf(self.d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        else:
            price = self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2) - self.S0 * norm.cdf(-self.d1)
        return price

    def monte_carlo_price(self, num_paths: int = 100_000, num_steps: int = 252, seed: int = 42) -> Tuple[float, np.ndarray]:
        """
        Monte Carlo simulace pomocí Geometric Brownian Motion.
        Vrátí cenu opce a pole všech payoffů (pro grafy).
        """
        np.random.seed(seed)
        dt = self.T / num_steps
        Z = np.random.standard_normal((num_paths, num_steps))
        
        # Simulace cenových cest
        log_S = np.cumsum((self.r - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * Z, axis=1)
        S_T = self.S0 * np.exp(log_S[:, -1])
        
        if self.option_type == "call":
            payoffs = np.maximum(S_T - self.K, 0)
        else:
            payoffs = np.maximum(self.K - S_T, 0)
        
        price = np.exp(-self.r * self.T) * np.mean(payoffs)
        return price, payoffs

    def binomial_tree_price(self, num_steps: int = 1000) -> float:
        """Binomial Tree model (Cox-Ross-Rubinstein)."""
        dt = self.T / num_steps
        u = np.exp(self.sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(self.r * dt) - d) / (u - d)
        
        # Cena podkladu na expiraci
        stock_prices = self.S0 * (u ** np.arange(num_steps, -1, -1)) * (d ** np.arange(0, num_steps + 1))
        
        if self.option_type == "call":
            option_values = np.maximum(stock_prices - self.K, 0)
        else:
            option_values = np.maximum(self.K - stock_prices, 0)
        
        # Backward induction
        for i in range(num_steps - 1, -1, -1):
            option_values = np.exp(-self.r * dt) * (p * option_values[:-1] + (1 - p) * option_values[1:])
        
        return option_values[0]

    def calculate_greeks(self) -> Dict[str, float]:
        """Výpočet citlivostí (Greeks) pomocí uzavřených vzorců Black-Scholes."""
        N_d1 = norm.cdf(self.d1)
        n_d1 = norm.pdf(self.d1)
        
        if self.option_type == "call":
            delta = N_d1
            rho = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2)
            theta = - (self.S0 * n_d1 * self.sigma) / (2 * np.sqrt(self.T)) - self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        else:
            delta = N_d1 - 1
            rho = -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
            theta = - (self.S0 * n_d1 * self.sigma) / (2 * np.sqrt(self.T)) + self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2)
        
        gamma = n_d1 / (self.S0 * self.sigma * np.sqrt(self.T))
        vega = self.S0 * n_d1 * np.sqrt(self.T)
        
        return {
            "Delta": round(delta, 6),
            "Gamma": round(gamma, 6),
            "Vega": round(vega, 6),
            "Theta": round(theta, 6),
            "Rho": round(rho, 6)
        }

    def simulate_delta_hedging(self, num_paths: int = 3000, rebalance_freq: int = 21) -> np.ndarray:
        """
        Jednoduchá simulace delta-hedgingu.
        Vrátí distribuci hedging errorů (rozdíl mezi payoffem a portfoliem).
        """
        np.random.seed(42)
        num_steps = 252
        dt = self.T / num_steps
        rebalance_steps = rebalance_freq
        
        Z = np.random.standard_normal((num_paths, num_steps))
        log_S = np.cumsum((self.r - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * Z, axis=1)
        S_paths = self.S0 * np.exp(log_S)
        
        hedging_errors = np.zeros(num_paths)
        
        for i in range(num_paths):
            S = S_paths[i]
            initial_option_price = self.black_scholes_price()
            
            # Rebalancing (zjednodušené)
            for step in range(0, num_steps, rebalance_steps):
                remaining_T = max(self.T * (1 - step / num_steps), 1e-6)
                if remaining_T <= 0:
                    break
                d1_curr = (np.log(S[step] / self.K) + (self.r + 0.5 * self.sigma**2) * remaining_T) / \
                          (self.sigma * np.sqrt(remaining_T))
                delta = norm.cdf(d1_curr) if self.option_type == "call" else norm.cdf(d1_curr) - 1
            
            final_S = S[-1]
            payoff = max(final_S - self.K, 0) if self.option_type == "call" else max(self.K - final_S, 0)
            hedging_errors[i] = payoff - initial_option_price
        
        return hedging_errors

    # ====================== VIZUALIZACE ======================
    def plot_payoff_distribution(self, num_paths: int = 50000, save_path: str = None):
        """Graf distribuce payoffů z Monte Carlo simulace."""
        _, payoffs = self.monte_carlo_price(num_paths=num_paths)
        plt.figure(figsize=(10, 6))
        sns.histplot(payoffs, bins=100, kde=True, color="skyblue")
        plt.axvline(np.mean(payoffs), color="red", linestyle="--", label=f"Průměr = {np.mean(payoffs):.2f}")
        plt.title(f"Distribuce payoffů – {self.option_type.upper()} opce")
        plt.xlabel("Payoff")
        plt.ylabel("Frekvence")
        plt.legend()
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            plt.close()

    def plot_mc_convergence(self, max_paths: int = 100000, step: int = 5000, save_path: str = None):
        """Graf konvergence Monte Carlo odhadu ceny."""
        paths_list = np.arange(step, max_paths + 1, step)
        prices = [self.monte_carlo_price(num_paths=p)[0] for p in paths_list]
        bs_price = self.black_scholes_price()
        
        plt.figure(figsize=(10, 6))
        plt.plot(paths_list, prices, label="Monte Carlo", color="blue")
        plt.axhline(bs_price, color="red", linestyle="--", label=f"Black-Scholes = {bs_price:.4f}")
        plt.title("Konvergence Monte Carlo simulace")
        plt.xlabel("Počet simulací")
        plt.ylabel("Cena opce")
        plt.legend()
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            plt.close()

    def plot_sample_paths(self, num_paths: int = 8, save_path: str = None):
        """Ukázka několika simulovaných cenových cest podkladu."""
        np.random.seed(42)
        num_steps = 252
        dt = self.T / num_steps
        Z = np.random.standard_normal((num_paths, num_steps))
        log_S = np.cumsum((self.r - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * Z, axis=1)
        S_paths = self.S0 * np.exp(log_S)
        
        plt.figure(figsize=(10, 6))
        time = np.linspace(0, self.T, num_steps)
        for path in S_paths:
            plt.plot(time, path, alpha=0.7)
        plt.axhline(self.K, color="red", linestyle="--", label="Strike")
        plt.title("Simulované cenové cesty (GBM)")
        plt.xlabel("Čas (roky)")
        plt.ylabel("Cena podkladu")
        plt.legend()
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            plt.close()

    def plot_hedging_error(self, hedging_errors: np.ndarray, save_path: str = None):
        """Graf distribuce chyb delta-hedgingu."""
        plt.figure(figsize=(10, 6))
        sns.histplot(hedging_errors, bins=80, kde=True, color="purple")
        plt.axvline(np.mean(hedging_errors), color="red", linestyle="--", 
                    label=f"Průměr = {np.mean(hedging_errors):.4f}")
        plt.title("Distribuce Delta-Hedging Erroru")
        plt.xlabel("Hedging Error")
        plt.ylabel("Frekvence")
        plt.legend()
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            plt.close()

    # ====================== PDF EXPORT ======================
    def export_to_pdf(self, filename: str = None, author: str = "Lukas Kolik") -> str:
        """
        Vytvoří profesionální PDF report + uloží grafy jako samostatné PNG soubory.
        """
        if filename is None:
            filename = f"option_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        full_path = os.path.join(os.getcwd(), filename)
        report_dir = os.getcwd()

        # Výpočty
        bs_price = self.black_scholes_price()
        mc_price, _ = self.monte_carlo_price()
        bin_price = self.binomial_tree_price()
        greeks = self.calculate_greeks()
        hedging_errors = self.simulate_delta_hedging()

        pdf = FPDF()
        pdf.add_page()
        
        # Hlavička
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Option Pricing Engine Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 8, f"Autor: {author}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"Generováno: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Obsah reportu
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Parametry opce", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 8, f"Typ: {self.option_type.upper()} | S0 = {self.S0} | K = {self.K} | T = {self.T}", 
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"r = {self.r} | volatilita = {self.sigma}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Ocenovani", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 8, f"Black-Scholes: ${bs_price:.4f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"Monte Carlo:   ${mc_price:.4f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"Binomial Tree: ${bin_price:.4f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Greeks", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=11)
        for k, v in greeks.items():
            pdf.cell(0, 8, f"  {k:6} = {v}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Delta Hedging Simulace", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 8, f"Pocet simulaci: {len(hedging_errors)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"Prumerny hedging error: {np.mean(hedging_errors):.4f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"Std. odchylka: {np.std(hedging_errors):.4f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Uložení grafů jako PNG + přidání do PDF
        print("Ukládám grafy jako samostatné PNG soubory...")
        payoff_path = os.path.join(report_dir, "payoff_distribution.png")
        convergence_path = os.path.join(report_dir, "mc_convergence.png")
        paths_path = os.path.join(report_dir, "price_paths.png")
        hedging_path = os.path.join(report_dir, "delta_hedging_error.png")

        self.plot_payoff_distribution(save_path=payoff_path)
        self.plot_mc_convergence(save_path=convergence_path)
        self.plot_sample_paths(save_path=paths_path)
        self.plot_hedging_error(hedging_errors, save_path=hedging_path)

        for title, img_path in [
            ("Distribuce Payoffu", payoff_path),
            ("Konvergence Monte Carlo", convergence_path),
            ("Simulovane cenove cesty", paths_path),
            ("Delta-Hedging Error", hedging_path)
        ]:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(img_path, x=10, w=190)

        pdf.output(full_path)
        
        print(f"✅ PDF report úspěšně vytvořen: {full_path}")
        print(f"📊 Grafy uloženy jako PNG v aktuální složce.")
        
        # Automatické otevření PDF
        try:
            if platform.system() == "Windows":
                os.startfile(full_path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", full_path])
            else:
                subprocess.call(["xdg-open", full_path])
            print("📄 PDF byl automaticky otevřen.")
        except:
            print("PDF vytvořen.")
        
        return full_path


# ====================== Hlavní spuštění ======================
if __name__ == "__main__":
    print("=== Option Pricing Engine ===\n")
    
    # === Možnost zadat vlastní parametry ===
    use_default = input("Chceš použít výchozí parametry? (ano/ne): ").strip().lower()
    
    if use_default in ["ano", "a", "yes", "y", ""]:
        S0 = 100.0
        K = 100.0
        T = 1.0
        r = 0.05
        sigma = 0.20
        option_type = "call"
    else:
        print("\nZadej parametry:")
        S0 = float(input("Aktuální cena podkladu (S0) [100]: ") or 100)
        K = float(input("Strike cena (K) [100]: ") or 100)
        T = float(input("Doba do expirace v letech (T) [1]: ") or 1)
        r = float(input("Bezriziková sazba (r) [0.05]: ") or 0.05)
        sigma = float(input("Volatilita (sigma) [0.20]: ") or 0.20)
        option_type = input("Typ opce (call/put) [call]: ").strip().lower() or "call"

    # Vytvoření enginu
    engine = OptionPricingEngine(S0=S0, K=K, T=T, r=r, sigma=sigma, option_type=option_type)
    
    # Výpis parametrů
    print("\n" + "="*50)
    print("POUŽITÉ PARAMETRY")
    print("="*50)
    print(f"Typ opce          : {engine.option_type.upper()}")
    print(f"S0 (podklad)      : {engine.S0}")
    print(f"K (strike)        : {engine.K}")
    print(f"T (expirace)      : {engine.T} roků")
    print(f"r (sazba)         : {engine.r*100:.2f} %")
    print(f"sigma (volatilita): {engine.sigma*100:.2f} %")
    print("="*50 + "\n")

    # Výpočty
    bs_price = engine.black_scholes_price()
    mc_price, _ = engine.monte_carlo_price()
    bin_price = engine.binomial_tree_price()

    print(f"Black-Scholes cena   : {bs_price:.4f}")
    print(f"Monte Carlo cena     : {mc_price:.4f}")
    print(f"Binomial Tree cena   : {bin_price:.4f}\n")

    # Generování PDF reportu (vše včetně grafů)
    print("Generuji PDF report a grafy...")
    engine.export_to_pdf()
    
    print("\n🎉 Hotovo! Všechny soubory byly vytvořeny v aktuální složce.")
