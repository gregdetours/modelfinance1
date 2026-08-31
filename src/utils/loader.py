import pandas as pd
from pathlib import Path

class DataLoader:
    """
    Classe responsable du chargement et du nettoyage des données Excel.
    Elle isole la lecture des fichiers de la logique mathématique du moteur.
    """
    
    def __init__(self, file_path: str = "data/inputs.xlsx"):
        # Utilisation de Path pour garantir que le chemin fonctionne sur Mac et Windows
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Le fichier Excel est introuvable au chemin : {self.file_path}")

    def load_patrimoine(self) -> pd.DataFrame:
        """Charge l'onglet Patrimoine_Initial en ignorant les notes textuelles."""
        df = pd.read_excel(self.file_path, sheet_name="Patrimoine_Initial")
        df = df.dropna(how='all')  # Supprime les lignes 100% vides
        
        # Remplacer les valeurs manquantes par 0 pour éviter les bugs de calcul
        if 'Versement_Mensuel_DCA' in df.columns:
            df['Versement_Mensuel_DCA'] = df['Versement_Mensuel_DCA'].fillna(0)
            
        return df

    def load_parametres(self) -> dict:
        """Charge les paramètres et les transforme en dictionnaire pour un accès rapide."""
        df = pd.read_excel(self.file_path, sheet_name="Parametres_Globaux")
        df = df.dropna(subset=['Parametre', 'Valeur'])
        
        # Transformation magique en dictionnaire : {'Revenus_Mensuels_Gregoire': 3000, ...}
        parametres_dict = pd.Series(df.Valeur.values, index=df.Parametre).to_dict()
        return parametres_dict

    def load_evenements(self, filtrer_actifs: bool = True) -> pd.DataFrame:
            """Charge l'onglet Evenements et nettoie les formats capricieux d'Excel."""
            df = pd.read_excel(self.file_path, sheet_name="Evenements")
            df = df.dropna(how='all')
            
            # 1. Blindage de la colonne Actif et conversion en vrai Booléen
            if 'Actif' in df.columns:
                mots_clefs = ['TRUE', 'VRAI', '1', '1.0', 'OUI']
                # On force la conversion en True/False pour Streamlit
                df['Actif'] = df['Actif'].astype(str).str.strip().str.upper().isin(mots_clefs)
                
                # On filtre uniquement si on le demande
                if filtrer_actifs:
                    df = df[df['Actif'] == True]
                
            # 2. Blindage de la colonne Date (Force le format texte MM/YYYY)
            if 'Date_Declenchement' in df.columns:
                def nettoyer_date(d):
                    # Si Excel a envoyé un objet Date, on le force en texte
                    if isinstance(d, pd.Timestamp) or "datetime" in str(type(d)):
                        return d.strftime("%m/%Y")
                    return str(d).strip()
                    
                df['Date_Declenchement'] = df['Date_Declenchement'].apply(nettoyer_date)
                
            return df