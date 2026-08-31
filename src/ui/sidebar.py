import streamlit as st
import pandas as pd

def render_sidebar(parametres_initiaux: dict, df_evenements: pd.DataFrame):
    """
    Affiche le panneau latéral interactif.
    Retourne les paramètres et événements modifiés par l'utilisateur.
    """
    st.sidebar.header("⚙️ Paramètres du Scénario")

    # 1. Ajustement dynamique des paramètres globaux
    st.sidebar.subheader("Revenus & Dépenses")
    
    # On crée des curseurs (sliders) pré-remplis avec les valeurs de l'Excel
    nouvelles_depenses = st.sidebar.slider(
        "Dépense Mensuelle Foyer (€)", 
        min_value=1500, max_value=6000, step=100,
        value=int(parametres_initiaux.get('Depense_Mensuelle_Foyer', 2500))
    )
    
    # 2. Gestion interactive des Événements
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Événements de Vie")
    st.sidebar.caption("Cochez pour activer un scénario (ex: Le voyage d'avril 2027 ou une crise)")
    
    evenements_modifies = df_evenements.copy()
    
    # Pour chaque événement dans l'Excel, on crée une case à cocher
    for index, row in evenements_modifies.iterrows():
        nom = row['Nom_Evenement']
        etat_initial = str(row['Actif']).strip().upper() in ['TRUE', 'VRAI', '1', 'OUI']
        
        # Le composant Streamlit : une case à cocher qui renvoie True ou False
        est_coche = st.sidebar.checkbox(nom, value=etat_initial)
        
        # On met à jour le tableau en direct
        evenements_modifies.at[index, 'Actif'] = est_coche

    # On met à jour notre dictionnaire de paramètres avec les nouvelles valeurs de la sidebar
    parametres_modifies = parametres_initiaux.copy()
    parametres_modifies['Depense_Mensuelle_Foyer'] = nouvelles_depenses

    return parametres_modifies, evenements_modifies