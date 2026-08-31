import pandas as pd

class Poche:
    """Représente une ligne d'investissement unique (ex: MSCI World de Solène)."""
    
    def __init__(self, nom: str, enveloppe: str, titulaire: str, profil_risque: str, montant_initial: float, rendement_cible: float):
        self.nom = nom
        self.enveloppe = enveloppe
        self.titulaire = titulaire
        self.profil_risque = profil_risque
        self.solde = float(montant_initial)
        self.rendement_cible = float(rendement_cible)

    def appliquer_rendement_mensuel(self):
        """Fait grossir le solde selon la formule des intérêts composés."""
        if self.solde > 0:
            taux_mensuel = (1 + self.rendement_cible) ** (1/12) - 1
            self.solde *= (1 + taux_mensuel)

    def injecter_fonds(self, montant: float):
        """Ajoute de l'argent (DCA ou apport exceptionnel)."""
        self.solde += montant

    def retirer_fonds(self, montant: float):
        """Retire de l'argent (en cas de coup dur ou projet)."""
        if montant <= self.solde:
            self.solde -= montant
        else:
            raise ValueError(f"Fonds insuffisants dans la poche {self.nom}.")

    def __repr__(self):
        return f"{self.enveloppe} {self.nom} ({self.titulaire}): {self.solde:.2f} €"


class Patrimoine:
    """Représente l'ensemble de la richesse du foyer à un instant T."""
    
    def __init__(self, df_patrimoine: pd.DataFrame):
        self.poches = []
        self._initialiser_poches(df_patrimoine)

    def _initialiser_poches(self, df: pd.DataFrame):
        """Transforme le tableau Pandas en objets 'Poche'."""
        for index, row in df.iterrows():
            nouvelle_poche = Poche(
                nom=row['Actif'],
                enveloppe=row['Enveloppe'],
                titulaire=row['Titulaire'],
                profil_risque=row['Profil_Risque'],
                montant_initial=row['Montant_EUR'],
                rendement_cible=row['Rendement_Cible']
            )
            self.poches.append(nouvelle_poche)

    def valeur_totale(self) -> float:
        """Calcule la valeur totale de tout le patrimoine."""
        return sum(poche.solde for poche in self.poches)

    def valeur_par_risque(self) -> dict:
        """Prépare les données pour le camembert Streamlit (Sécurisé vs Risqué)."""
        repartition = {}
        for poche in self.poches:
            repartition[poche.profil_risque] = repartition.get(poche.profil_risque, 0) + poche.solde
        return repartition