import pandas as pd
from datetime import datetime
from src.core.portfolio import Patrimoine
from src.core.events import Evenement, ModificationFlux

class Simulateur:
    
    def __init__(self, patrimoine: Patrimoine, evenements: list[Evenement], parametres: dict, date_debut: str = "08/2026"):
        self.patrimoine = patrimoine
        self.evenements = evenements
        self.parametres = parametres
        self.date_actuelle = datetime.strptime(date_debut, "%m/%Y")
        self.historique = []

    def _calculer_cashflow_mensuel(self) -> float:
        """Calcule la capacité d'épargne du mois (Revenus - Dépenses)."""
        
        # 1. Base : Revenus et Dépenses initiaux
        revenus = float(self.parametres.get('Revenus_Mensuels_Gregoire', 0)) + float(self.parametres.get('Revenus_Mensuels_Solene', 0))
        depenses = float(self.parametres.get('Depense_Mensuelle_Foyer', 2500))
        
        # 2. Impact des événements en cours (ex: Congé sans solde, Loyer, Mensualité crédit)
        for event in self.evenements:
            if isinstance(event, ModificationFlux):
                revenus += event.impact_sur_cashflow(self.date_actuelle, flux_type="Revenu")
                depenses += event.impact_sur_cashflow(self.date_actuelle, flux_type="Depense")
                
        # Capacité d'épargne libre
        return revenus - depenses

    def _repartir_epargne(self, cashflow: float):
        """Distribue le cashflow dans le patrimoine (logique basique pour l'instant)."""
        if cashflow > 0:
            # Pour l'instant, on met tout l'excédent dans la première poche trouvée (On affinera plus tard !)
            self.patrimoine.poches[0].injecter_fonds(cashflow)
        elif cashflow < 0:
            # Si on est dans le rouge (ex: Congé sans solde), on pioche dans la première poche
            try:
                self.patrimoine.poches[0].retirer_fonds(abs(cashflow))
            except ValueError:
                print(f"ALERTE : Faillite ce mois-ci ({self.date_actuelle.strftime('%m/%Y')}) !")

    def _avancer_un_mois(self):
        # 1. Rendements (Intérêts composés)
        for poche in self.patrimoine.poches:
            poche.appliquer_rendement_mensuel()
            
        # 2. Cash-Flow (Nouveau !)
        cashflow = self._calculer_cashflow_mensuel()
        self._repartir_epargne(cashflow)
        
        # 3. Événements ponctuels (One-shot)
        date_str = self.date_actuelle.strftime("%m/%Y")
        for event in self.evenements:
            event.verifier_et_appliquer(self.patrimoine, date_str)
        
        # 4. Horloge
        mois = self.date_actuelle.month
        annee = self.date_actuelle.year
        if mois == 12:
            self.date_actuelle = self.date_actuelle.replace(month=1, year=annee + 1)
        else:
            self.date_actuelle = self.date_actuelle.replace(month=mois + 1)

    def run(self, duree_mois: int = 120) -> pd.DataFrame:
        self.historique.append({"Date": self.date_actuelle.strftime("%m/%Y"), "Valeur_Patrimoine": self.patrimoine.valeur_totale()})
        for _ in range(duree_mois):
            self._avancer_un_mois()
            self.historique.append({"Date": self.date_actuelle.strftime("%m/%Y"), "Valeur_Patrimoine": self.patrimoine.valeur_totale()})
        return pd.DataFrame(self.historique)