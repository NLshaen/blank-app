import streamlit as st
import sqlite3
import os
from pathlib import Path
from PIL import Image

# CONFIGURATION
st.set_page_config(
    page_title="Ma Galerie d'Art",
    page_icon="🎨",
    layout="wide"
)

DOSSIER = Path("images")
DOSSIER.mkdir(exist_ok=True)

DB = "galerie.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")

# BASE DE DONNÉES
def connexion():
    return sqlite3.connect(DB)

def initialiser():
    with connexion() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS tableaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT,
                description TEXT,
                technique TEXT,
                dimensions TEXT,
                annee TEXT,
                prix TEXT,
                image TEXT
            )
        """)

def recuperer_tableaux():
    with connexion() as con:
        return con.execute(
            "SELECT * FROM tableaux ORDER BY id DESC"
        ).fetchall()

def ajouter_tableau(titre, description, technique,
                    dimensions, annee, prix, image):
    with connexion() as con:
        con.execute("""
            INSERT INTO tableaux
            (titre, description, technique, dimensions,
             annee, prix, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (titre, description, technique,
              dimensions, annee, prix, image))

def supprimer_tableau(id_tableau):
    with connexion() as con:
        resultat = con.execute(
            "SELECT image FROM tableaux WHERE id = ?",
            (id_tableau,)
        ).fetchone()

        con.execute(
            "DELETE FROM tableaux WHERE id = ?",
            (id_tableau,)
        )

    if resultat:
        chemin = DOSSIER / resultat[0]
        if chemin.exists():
            chemin.unlink()

initialiser()

# STYLE
st.markdown("""
<style>
.stApp {
    background-color: #faf8f5;
}
h1, h2, h3 {
    color: #38302c;
}
.legende {
    color: #897d73;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# MENU
st.sidebar.title("🎨 Ma Galerie")
page = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Galerie", "À propos", "Contact", "Administration"]
)

# ACCUEIL
if page == "Accueil":

    st.title("Bienvenue dans mon univers artistique")
    st.subheader("Des œuvres uniques, créées avec passion.")

    st.markdown("---")

    tableaux = recuperer_tableaux()

    if tableaux:
        st.subheader("Quelques-unes de mes créations")

        cols = st.columns(3)

        for i, tableau in enumerate(tableaux[:3]):
            with cols[i]:
                chemin = DOSSIER / tableau[7]
                if chemin.exists():
                    st.image(str(chemin), use_container_width=True)
                st.markdown(f"**{tableau[1]}**")
                st.caption(tableau[3])

    else:
        st.info("La galerie sera bientôt enrichie de nouvelles œuvres.")

# GALERIE
elif page == "Galerie":

    st.title("Ma collection")
    tableaux = recuperer_tableaux()

    if not tableaux:
        st.info("Aucun tableau disponible pour le moment.")
    else:
        colonnes = st.columns(3)

        for i, tableau in enumerate(tableaux):
            with colonnes[i % 3]:
                chemin = DOSSIER / tableau[7]

                if chemin.exists():
                    st.image(
                        str(chemin),
                        use_container_width=True
                    )

                st.subheader(tableau[1])
                st.write(tableau[2])
                st.caption(
                    f"{tableau[3]} | {tableau[4]} | {tableau[5]}"
                )

                if tableau[6]:
                    st.write(f"Prix : {tableau[6]}")

                with st.expander("Voir les détails"):
                    st.write(tableau[2])
                    st.write(f"Technique : {tableau[3]}")
                    st.write(f"Dimensions : {tableau[4]}")
                    st.write(f"Année : {tableau[5]}")

# À PROPOS
elif page == "À propos":

    st.title("À propos de l'artiste")

    st.write("""
    Bienvenue dans mon univers artistique.

    Je vous invite à découvrir mes peintures,
    mes inspirations et mon travail artistique.

    Chaque tableau est une création unique,
    réalisée avec passion et sensibilité.
    """)

# CONTACT
elif page == "Contact":

    st.title("Me contacter")

    st.write("Une œuvre vous intéresse ? Contactez-moi.")

    if CONTACT_EMAIL:
        st.link_button(
            "M'envoyer un email",
            f"mailto:{CONTACT_EMAIL}"
        )
    else:
        st.info("L'adresse email de contact sera configurée prochainement.")

# ADMINISTRATION
elif page == "Administration":

    st.title("Administration de la galerie")

    if not ADMIN_PASSWORD:
        st.error(
            "Configurez la variable ADMIN_PASSWORD "
            "avant d'utiliser l'administration."
        )
        st.stop()

    mot_de_passe = st.text_input(
        "Mot de passe administrateur",
        type="password"
    )

    if mot_de_passe != ADMIN_PASSWORD:
        st.warning("Accès réservé à l'administrateur.")
        st.stop()

    st.success("Bienvenue dans votre espace administrateur.")

    st.subheader("Ajouter un tableau")

    with st.form("ajout_tableau"):
        titre = st.text_input("Titre du tableau")
        description = st.text_area("Description")
        technique = st.text_input("Technique (huile, acrylique...)")
        dimensions = st.text_input("Dimensions")
        annee = st.text_input("Année de création")
        prix = st.text_input("Prix")

        fichier = st.file_uploader(
            "Photographie du tableau",
            type=["jpg", "jpeg", "png", "webp"]
        )

        envoyer = st.form_submit_button("Ajouter à la galerie")

        if envoyer:
            if not titre or not fichier:
                st.error("Le titre et la photographie sont obligatoires.")
            else:
                try:
                    image = Image.open(fichier)
                    image.verify()

                    extension = fichier.type.split("/")[-1]
                    if extension == "jpeg":
                        extension = "jpg"

                    nom_image = f"{os.urandom(12).hex()}.{extension}"

                    fichier.seek(0)
                    image = Image.open(fichier).convert("RGB")
                    image.thumbnail((2400, 2400))
                    image.save(DOSSIER / nom_image, quality=90)

                    ajouter_tableau(
                        titre, description, technique,
                        dimensions, annee, prix, nom_image
                    )

                    st.success("Tableau ajouté avec succès !")
                    st.rerun()

                except Exception:
                    st.error("Impossible de traiter cette image.")

    st.markdown("---")
    st.subheader("Gérer les tableaux")

    for tableau in recuperer_tableaux():
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"**{tableau[1]}**")

        with col2:
            if st.button("Supprimer", key=f"sup_{tableau[0]}"):
                supprimer_tableau(tableau[0])
                st.rerun()
