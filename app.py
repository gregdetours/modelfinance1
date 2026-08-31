import streamlit as st
from src.utils.loader import DataLoader

# Configuration basique de la page web
st.set_page_config(page_title="Simulateur Financier", layout="wide")

st.title("💸 Simulateur Financier - Test de chargement")

# Bloc de test sécurisé (try/except) pour attraper les erreurs élégamment
try:
    # 1. On initialise notre chargeur
    loader = DataLoader()
    
    # 2. On lance l'extraction des 3 onglets
    df_patrimoine = loader.load_patrimoine()
    parametres = loader.load_parametres()
    df_evenements = loader.load_evenements()
    
    # 3. On affiche le tout sur l'interface Streamlit
    st.header("1. Patrimoine Initial")
    st.dataframe(df_patrimoine, use_container_width=True)
    
    st.header("2. Paramètres Globaux (Dictionnaire Python)")
    st.write(parametres)
    
    st.header("3. Événements Actifs")
    st.dataframe(df_evenements, use_container_width=True)
    
    st.success("✅ Bravo ! La connexion entre Excel, Pandas et Streamlit fonctionne parfaitement.")
    
except Exception as e:
    st.error(f"❌ Une erreur est survenue lors de la lecture du fichier : {e}")