import streamlit as st
import plotly.express as px
from src.utils.loader import DataLoader
from src.core.portfolio import Patrimoine

# Configuration de la page
st.set_page_config(page_title="Simulateur Financier", layout="wide")

st.title("💸 Simulateur Financier - Test du Moteur Mathématique")

try:
    # 1. Chargement des données brutes depuis Excel
    loader = DataLoader()
    df_patrimoine = loader.load_patrimoine()
    
    # 2. Initialisation du moteur orienté objet
    mon_patrimoine = Patrimoine(df_patrimoine)
    
    st.header("1. Photographie à l'Instant T=0")
    
    # Création de deux colonnes pour structurer l'affichage
    col1, col2 = st.columns(2)
    
    with col1:
        # Affichage d'une belle métrique pour le total
        valeur_tot = mon_patrimoine.valeur_totale()
        st.metric(label="Valeur Totale du Patrimoine", value=f"{valeur_tot:,.2f} €".replace(',', ' '))
        
        # Affichage du détail brut
        st.write("Détail des poches :")
        for poche in mon_patrimoine.poches:
            st.write(f"- **{poche.nom}** ({poche.enveloppe}) : {poche.solde:,.2f} €".replace(',', ' '))
    
    with col2:
        # 3. Création du premier camembert (Donut)
        repartition_risque = mon_patrimoine.valeur_par_risque()
        
        fig = px.pie(
            names=list(repartition_risque.keys()), 
            values=list(repartition_risque.values()), 
            title="Répartition par Profil de Risque",
            hole=0.4, # Transforme le camembert en "donut"
            color_discrete_sequence=['#2ecc71', '#e74c3c'] # Vert pour sécurisé, Rouge pour risqué
        )
        st.plotly_chart(fig, use_container_width=True)

    # 4. Test du vieillissement mathématique
    st.header("2. Test de la machine à voyager dans le temps")
    st.info("Clique sur ce bouton pour simuler un mois de rendement sur toutes tes enveloppes simultanément.")
    
    if st.button("Simuler +1 Mois de rendements"):
        # On applique la méthode à chaque objet Poche
        for poche in mon_patrimoine.poches:
            poche.appliquer_rendement_mensuel()
            
        nouvelle_valeur = mon_patrimoine.valeur_totale()
        st.success("Le temps a avancé d'un mois !")
        st.metric(
            label="Nouvelle Valeur Totale (après intérêts)", 
            value=f"{nouvelle_valeur:,.2f} €".replace(',', ' '),
            delta=f"+ {nouvelle_valeur - valeur_tot:,.2f} €" # Affiche la plus-value en vert
        )

except Exception as e:
    st.error(f"❌ Une erreur est survenue : {e}")