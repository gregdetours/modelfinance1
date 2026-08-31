import streamlit as st
import plotly.express as px
from src.utils.loader import DataLoader
from src.core.portfolio import Patrimoine
from src.core.events import DepenseExceptionnelle # On importe la classe fille
from src.core.engine import Simulateur

st.set_page_config(page_title="Simulateur Financier", layout="wide")
st.title("💸 Simulateur Financier - La Timeline")

try:
    # 1. Chargement des données
    loader = DataLoader()
    df_patrimoine = loader.load_patrimoine()
    df_evenements = loader.load_evenements()
    
    # 2. Initialisation des objets
    mon_patrimoine = Patrimoine(df_patrimoine)
    
    # Transformation des lignes Excel en objets d'événements Python
    liste_evenements = []
    for _, row in df_evenements.iterrows():
        if row['Type_Action'] == 'Depense_Exceptionnelle':
            nouvel_event = DepenseExceptionnelle(
                nom=row['Nom_Evenement'],
                date_declenchement=row['Date_Declenchement'],
                cible=row['Cible'],
                valeur=row['Valeur'],
                duree_mois=row['Duree_Mois']
            )
            liste_evenements.append(nouvel_event)

    # 3. Lancement du Moteur sur 10 ans (120 mois)
    moteur = Simulateur(mon_patrimoine, liste_evenements, date_debut="08/2026")
    df_timeline = moteur.run(duree_mois=120)

    # 4. Affichage du Graphique
    st.header("Projection du Patrimoine Global")
    
    fig = px.line(
        df_timeline, 
        x="Date", 
        y="Valeur_Patrimoine", 
        title="Évolution du patrimoine sur 10 ans",
        markers=True # Ajoute des points sur la courbe pour plus de lisibilité
    )
    
    # On force l'axe Y à commencer à zéro pour éviter un effet de loupe trompeur
    fig.update_layout(yaxis=dict(rangemode='tozero'))
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur : {e}")