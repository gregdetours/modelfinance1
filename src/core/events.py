from src.core.portfolio import Patrimoine

class Evenement:
    """Classe mère générique pour tous les événements de la vie."""
    
    def __init__(self, nom: str, date_declenchement: str, cible: str, valeur: float, duree_mois: int):
        self.nom = nom
        self.date_declenchement = date_declenchement  # Format attendu : MM/YYYY
        self.cible = cible
        self.valeur = float(valeur)
        self.duree_mois = int(duree_mois)
        self.actif = True  # Par défaut, l'événement est actif

    def verifier_et_appliquer(self, patrimoine: Patrimoine, date_actuelle: str):
        """Vérifie si on est à la bonne date pour déclencher le choc."""
        if self.actif and date_actuelle == self.date_declenchement:
            self._appliquer_impact(patrimoine)

    def _appliquer_impact(self, patrimoine: Patrimoine):
        """Méthode vide qui sera écrasée par les classes filles."""
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
    """Applique une baisse ou hausse soudaine (ex: Krach boursier) sur un profil de risque."""
    
    def _appliquer_impact(self, patrimoine: Patrimoine):
        for poche in patrimoine.poches:
            # Si la cible est "Risque" par exemple, on impacte toutes les poches risquées
            if poche.profil_risque == self.cible:
                poche.solde *= (1 + self.valeur) # self.valeur sera négative dans l'Excel (ex: -0.30)