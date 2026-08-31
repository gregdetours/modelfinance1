from src.core.portfolio import Patrimoine
from datetime import datetime
from src.core.portfolio import Patrimoine

class Evenement:
    """Classe mère générique pour tous les événements de la vie."""
    
    def __init__(self, nom: str, date_declenchement: str, cible: str, valeur: float, duree_mois: int):
        self.nom = nom
        self.date_declenchement = date_declenchement  # Format MM/YYYY
        self.cible = cible
        self.valeur = float(valeur)
        self.duree_mois = int(duree_mois)
        self.actif = True

    def verifier_et_appliquer(self, patrimoine: Patrimoine, date_actuelle_str: str):
        """Déclenche les événements ponctuels (One-Shot)."""
        if self.actif and date_actuelle_str == self.date_declenchement:
            self._appliquer_impact(patrimoine)

    def est_en_cours(self, date_actuelle: datetime) -> bool:
        """Détermine si un événement continu est actif à cette date précise."""
        if not self.actif:
            return False
            
        date_debut = datetime.strptime(self.date_declenchement, "%m/%Y")
        
        # Calcul de la différence en mois entre aujourd'hui et le début de l'événement
        diff_mois = (date_actuelle.year - date_debut.year) * 12 + (date_actuelle.month - date_debut.month)
        
        # L'événement est en cours si on a dépassé la date de début et qu'on n'a pas dépassé la durée
        return 0 <= diff_mois < self.duree_mois

    def _appliquer_impact(self, patrimoine: Patrimoine):
        pass


class DepenseExceptionnelle(Evenement):
    """Retire un montant d'une poche spécifique à un instant T."""
    
    def _appliquer_impact(self, patrimoine: Patrimoine):
        for poche in patrimoine.poches:
            # On cherche la poche qui correspond au nom de la cible dans l'Excel
            if poche.nom == self.cible:
                try:
                    poche.retirer_fonds(abs(self.valeur))
                except ValueError:
                    # Plus tard, on pourra coder une logique en cascade pour piocher ailleurs
                    print(f"Attention : Fonds insuffisants dans {poche.nom} pour {self.nom}")


class ChocDeMarche(Evenement):
    """Applique une baisse ou hausse soudaine sur une cible précise ou un groupe (ex: profil_risque=Risque)."""
    
    def _appliquer_impact(self, patrimoine: Patrimoine):
        for poche in patrimoine.poches:
            doit_etre_impacte = False
            
            # Cas 1 : La cible Excel contient un "=" (ex: "profil_risque=Risque")
            if "=" in self.cible:
                # On sépare le critère et la valeur attendue
                critere, valeur_cible = self.cible.split("=")
                critere = critere.strip().lower() # ex: "profil_risque"
                valeur_cible = valeur_cible.strip().lower() # ex: "risque"
                
                # getattr permet de lire dynamiquement l'attribut de l'objet Poche
                valeur_poche = str(getattr(poche, critere, "")).lower()
                
                if valeur_poche == valeur_cible:
                    doit_etre_impacte = True
                    
            # Cas 2 : La cible Excel est directement le nom de la poche (ex: "MSCI World")
            elif poche.nom.lower() == self.cible.strip().lower():
                doit_etre_impacte = True
                
            # Application du krach boursier ou du boom
            if doit_etre_impacte:
                poche.solde *= (1 + self.valeur)

class ModificationFlux(Evenement):
    """Modifie les revenus ou les dépenses de manière continue pendant X mois."""
    
    def impact_sur_cashflow(self, date_actuelle: datetime, flux_type: str) -> float:
        """
        Renvoie la valeur à ajouter ou soustraire ce mois-ci.
        flux_type permet de filtrer (ex: on ne veut que les "Revenus" ou que les "Depenses").
        """
        if self.est_en_cours(date_actuelle):
            # Si le nom de la cible contient le mot recherché (ex: 'Revenu' dans 'Revenus_Mensuels_Gregoire')
            if flux_type.lower() in self.cible.lower():
                return self.valeur
        return 0.0