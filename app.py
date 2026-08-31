import streamlit as st
import plotly.express as px
from src.utils.loader import DataLoader
from src.core.portfolio import Patrimoine
# 1. On ajoute ModificationFlux ici :
from src.core.events import DepenseExceptionnelle, ChocDeMarche, ModificationFlux
from src.core.engine import Simulateur
from src.ui.sidebar import render_sidebar

st.set_page_config(page_title="Simulateur Financier", layout="wide")
st.title("💸 Simulateur Financier Interactif")

try:
    loader = DataLoader()
    df_patrimoine = loader.load_patrimoine()
    parametres_bruts = loader.load_parametres()
    df_evenements_bruts = loader.load_evenements(filtrer_actifs=False)
    
    parametres_finaux, df_evenements_finaux = render_sidebar(parametres_bruts, df_evenements_bruts)
    df_evenements_actifs = df_evenements_finaux[df_evenements_finaux['Actif'] == True]

    mon_patrimoine = Patrimoine(df_patrimoine)
    
    liste_evenements = []
    for _, row in df_evenements_actifs.iterrows():
        # Les chocs ponctuels
        if row['Type_Action'] == 'Depense_Exceptionnelle':
            liste_evenements.append(DepenseExceptionnelle(
                nom=row['Nom_Evenement'], date_declenchement=row['Date_Declenchement'],
                cible=row['Cible'], valeur=row['Valeur'], duree_mois=row['Duree_Mois']
            ))
        elif row['Type_Action'] == 'Choc_Marche':
            liste_evenements.append(ChocDeMarche(
                nom=row['Nom_Evenement'], date_declenchement=row['Date_Declenchement'],
                cible=row['Cible'], valeur=row['Valeur'], duree_mois=row['Duree_Mois']
            ))
        # 2. Les nouveaux chocs continus (Revenus / Dépenses)
        elif row['Type_Action'] in ['Modification_Revenu', 'Modification_Depense']:
            liste_evenements.append(ModificationFlux(
                nom=row['Nom_Evenement'], date_declenchement=row['Date_Declenchement'],
                cible=row['Cible'], valeur=row['Valeur'], duree_mois=row['Duree_Mois']
            ))

    # 3. On injecte les parametres_finaux dans le moteur !
    moteur = Simulateur(mon_patrimoine, liste_evenements, parametres_finaux, date_debut="08/2026")
    df_timeline = moteur.run(duree_mois=120)

    # --- AFFICHAGE ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Projection du Patrimoine")
        fig_line = px.line(df_timeline, x="Date", y="Valeur_Patrimoine", markers=True)
        fig_line.update_layout(yaxis=dict(rangemode='tozero'))
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col2:
        st.subheader("Répartition Initiale")
        repartition = mon_patrimoine.valeur_par_risque()
        fig_pie = px.pie(names=list(repartition.keys()), values=list(repartition.values()), hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur : {e}")