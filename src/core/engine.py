import pandas as pd
from datetime import datetime
from src.core.portfolio import Patrimoine
from src.core.events import Evenement

class Simulateur:
    """Moteur temporel qui fait avancer le temps et orchestre les événements."""
    
    def __init__(self, patrimoine: Patrimoine, evenements: list[Evenement], date_debut: str = "08/2026"):
        self.patrimoine = patrimoine
        self.evenements = evenements
        self.date_actuelle = datetime.strptime(date_debut, "%m/%Y")
        self.historique = [] # Stocke les points de la timeline

    def _avancer_un_mois(self):
        """Fait vieillir le portefeuille d'un mois et met à jour l'horloge."""
        # 1. Les intérêts composés travaillent
        for poche in self.patrimoine.poches:
            poche.appliquer_rendement_mensuel()
        
        # 2. On avance l'horloge manuellement
        mois = self.date_actuelle.month
        annee = self.date_actuelle.year
        if mois == 12:
            self.date_actuelle = self.date_actuelle.replace(month=1, year=annee + 1)
        else:
            self.date_actuelle = self.date_actuelle.replace(month=mois + 1)

    def _declencher_evenements(self):
        """Vérifie si un événement a lieu ce mois-ci et l'applique si besoin."""
        date_str = self.date_actuelle.strftime("%m/%Y")
        for event in self.evenements:
            event.verifier_et_appliquer(self.patrimoine, date_str)

    def run(self, duree_mois: int = 120) -> pd.DataFrame:
        """Lance la simulation et retourne les données structurées pour le graphique."""
        # Sauvegarde du point de départ
        self.historique.append({
            "Date": self.date_actuelle.strftime("%m/%Y"),
            "Valeur_Patrimoine": self.patrimoine.valeur_totale()
        })

        # Boucle temporelle
        for _ in range(duree_mois):
            self._avancer_un_mois()
            self._declencher_evenements()
            
            # Sauvegarde de la valeur post-rendements et post-événements
            self.historique.append({
                "Date": self.date_actuelle.strftime("%m/%Y"),
                "Valeur_Patrimoine": self.patrimoine.valeur_totale()
            })

        return pd.DataFrame(self.historique)