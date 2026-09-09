import streamlit as st
from pypdf import PdfReader
import docx

# Configuration de la page
st.set_page_config(page_title="Adaptateur CV & Personnalité (Claude)", page_icon="🎯", layout="wide")

st.title("🎯 Adaptateur de CV & Profil Comportemental")
st.write("Cet outil prépare ton analyse pour l'IA **Claude**.")

# Fonction pour extraire le texte des fichiers importés
def extraire_texte(fichier_importe):
    texte = ""
    try:
        if fichier_importe.name.endswith(".pdf"):
            reader = PdfReader(fichier_importe)
            for page in reader.pages:
                texte += page.extract_text() + "\n"
        elif fichier_importe.name.endswith(".docx"):
            doc = docx.Document(fichier_importe)
            for p in doc.paragraphs:
                texte += p.text + "\n"
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
    return texte

# Sidebar : Choix du mode
with st.sidebar:
    st.header("Méthode d'analyse")
    mode = st.radio(
        "Choisissez votre mode :",
        ["Mode Manuel (Claude.ai - 100% Gratuit)", "Mode Automatique (API Anthropic)"]
    )
    
    api_key = ""
    if mode == "Mode Automatique (API Anthropic)":
        api_key = st.text_input("Clé API Anthropic (sk-ant-...)", type="password")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Ton profil de personnalité")
    profil = st.selectbox(
        "Sélectionne ton profil dominant (DISC) :",
        [
            "Dominant (Orienté résultats, action, défis, métriques)",
            "Influent (Orienté relationnel, communication, réseau, équipe)",
            "Stable (Orienté méthode, organisation, écoute, rigueur)",
            "Conforme (Orienté analyse, précision, normes, données)"
        ]
    )

    st.subheader("2. Ton CV")
    fichier_cv = st.file_uploader("Importe ton CV (format PDF ou DOCX) :", type=["pdf", "docx"])
    
    cv_texte = ""
    if fichier_cv is not None:
        cv_texte = extraire_texte(fichier_cv)
        st.success("CV chargé avec succès !")
    else:
        cv_texte = st.text_area("Ou colle le texte brut de ton CV ici :", height=150)

with col2:
    st.subheader("3. L'offre d'emploi visée")
    offre_texte = st.text_area("Colle la description de l'offre d'emploi :", height=350)

# Génération
if st.button("🚀 Préparer l'adaptation pour Claude", type="primary", use_container_width=True):
    if not cv_texte or not offre_texte:
        st.warning("Veuillez charger/coller un CV et l'offre d'emploi.")
    else:
        prompt_final = f"""Tu es un expert RH et spécialiste en recrutement.

[PROFIL COMPORTEMENTAL CANDIDAT - DISC]
{profil}

[TEXTE DU CV DU CANDIDAT]
{cv_texte}

[OFFRE D'EMPLOI VISÉE]
{offre_texte}

[MISSION]
1. Analyse les compétences clés et les mots-clés ATS essentiels de l'offre d'emploi.
2. Rédige une accroche de CV percutante (3-4 lignes) parfaitement alignée sur le profil comportemental du candidat et les besoins du poste.
3. Reformule et réorganise les expériences du CV pour valoriser la personnalité du candidat tout en optimisant le score ATS.
4. Rends le CV optimisé complet sous forme de texte clair en Markdown.
"""

        if mode == "Mode Manuel (Claude.ai - 100% Gratuit)":
            st.success("✅ Ton prompt est prêt ! Copie le texte dans l'encadré ci-dessous et colle-le directement dans **[claude.ai](https://claude.ai)** :")
            st.code(prompt_final, language="markdown")
            
        else:
            if not api_key:
                st.error("Veuillez saisir votre clé API Anthropic dans le panneau latéral gauche.")
            else:
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    with st.spinner("Claude analyse et réécrit ton CV..."):
                        message = client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=4000,
                            messages=[{"role": "user", "content": prompt_final}]
                        )
                        st.success("Adaptation terminée !")
                        st.markdown("---")
                        st.markdown(message.content[0].text)
                except Exception as e:
                    st.error(f"Une erreur est survenue avec l'API Anthropic : {e}")