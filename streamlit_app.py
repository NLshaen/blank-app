import streamlit as st
import sqlite3
import os
import uuid
import html
from pathlib import Path
from urllib.parse import quote
from PIL import Image

# ==========================================
# LUCAS ART - GALERIE DE PEINTURE
# ==========================================

st.set_page_config(
    page_title="LUCAS ART | Galerie de peinture",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DOSSIER = Path("images")
DOSSIER.mkdir(exist_ok=True)
DB = "lucas_art.db"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "test123")
EMAIL = os.environ.get("CONTACT_EMAIL", "admin@gmail.com")

# ==========================================
# BASE DE DONNEES
# ==========================================

def db():
    return sqlite3.connect(DB)

def initialiser():
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS oeuvres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT,
            technique TEXT,
            dimensions TEXT,
            annee TEXT,
            prix TEXT,
            image TEXT NOT NULL
        )
        """)

def liste_oeuvres():
    with db() as con:
        return con.execute(
            "SELECT * FROM oeuvres ORDER BY id DESC"
        ).fetchall()

def ajouter_oeuvre(data):
    with db() as con:
        con.execute("""
        INSERT INTO oeuvres
        (titre, description, technique,
         dimensions, annee, prix, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)

def supprimer_oeuvre(identifiant):
    with db() as con:
        result = con.execute(
            "SELECT image FROM oeuvres WHERE id=?",
            (identifiant,)
        ).fetchone()

        con.execute(
            "DELETE FROM oeuvres WHERE id=?",
            (identifiant,)
        )

    if result:
        fichier = DOSSIER / result[0]
        if fichier.exists():
            fichier.unlink()

initialiser()

# ==========================================
# STYLE GRAPHIQUE
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@600;700&display=swap');

.stApp {
    background: #faf9f6;
    color: #22232a;
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
}
.hero {
    background: linear-gradient(120deg,#171923,#37304b);
    color: white;
    padding: 55px 35px;
    border-radius: 18px;
    margin-bottom: 25px;
}
.hero h1 {
    color: white !important;
    font-size: 52px !important;
}
.hero p {
    color: #e4d9f0;
    font-size: 18px;
}
.oeuvre {
    background: white;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid #ece8e1;
}
.prix {
    color: #c34e37;
    font-weight: bold;
}
footer {
    visibility: hidden;
}
.stButton button {
    border-radius: 10px;
    background: #25263a;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# NAVIGATION
# ==========================================

st.markdown("""
<div style="display:flex;justify-content:space-between;
align-items:center;padding:12px 0;">
<h2 style="margin:0;color:#22232a;">LUCAS ART.</h2>
<span style="color:#8b8178;font-size:12px;">
GALERIE D'ART CONTEMPORAIN
</span>
</div>
""", unsafe_allow_html=True)

page = st.radio(
    "Navigation",
    ["Accueil", "Mes œuvres", "À propos", "Contact"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# ==========================================
# ACCUEIL
# ==========================================

if page == "Accueil":

    st.markdown("""
    <div class="hero">
        <p>BIENVENUE DANS MON UNIVERS</p>
        <h1>LUCAS ART.</h1>
        <p>L'art est une émotion.<br>
        Découvrez mes peintures et mes créations originales.</p>
    </div>
    """, unsafe_allow_html=True)

    st.title("Les dernières créations")

    oeuvres = liste_oeuvres()

    if oeuvres:
        colonnes = st.columns(3)

        for i, o in enumerate(oeuvres[:3]):
            with colonnes[i]:
                chemin = DOSSIER / o[7]
                if chemin.exists():
                    st.image(str(chemin), use_container_width=True)
                st.subheader(o[1])
                st.caption(o[3])
                if o[6]:
                    st.markdown(
                        f'<p class="prix">{html.escape(o[6])}</p>',
                        unsafe_allow_html=True
                    )
    else:
        st.info("Les premières œuvres seront bientôt exposées.")

    st.markdown("---")
    st.title("L'art sous toutes ses couleurs")
    st.write(
        "Chaque création possède son histoire, "
        "sa personnalité et son émotion."
    )

    if st.button("Découvrir toute la galerie"):
        st.session_state["page"] = "Mes œuvres"
        st.rerun()

# ==========================================
# GALERIE
# ==========================================

elif page == "Mes œuvres":

    st.title("Ma galerie")
    st.write("Découvrez toutes mes créations.")

    oeuvres = liste_oeuvres()

    if not oeuvres:
        st.info("La galerie est actuellement en préparation.")

    for debut in range(0, len(oeuvres), 3):
        colonnes = st.columns(3)

        for col, o in zip(colonnes, oeuvres[debut:debut+3]):
            with col:
                chemin = DOSSIER / o[7]

                if chemin.exists():
                    st.image(str(chemin), use_container_width=True)

                st.subheader(o[1])

                if o[6]:
                    st.markdown(
                        f'<p class="prix">{html.escape(o[6])}</p>',
                        unsafe_allow_html=True
                    )

                with st.expander("Découvrir cette œuvre"):
                    st.write(o[2])
                    st.write("Technique :", o[3])
                    st.write("Dimensions :", o[4])
                    st.write("Année :", o[5])

                    if EMAIL:
                        sujet = quote("Demande concernant : " + o[1])
                        message = quote(
                            "Bonjour, je souhaite obtenir "
                            "des renseignements sur cette œuvre."
                        )
                        st.link_button(
                            "Demander des renseignements",
                            f"mailto:{EMAIL}?subject={sujet}&body={message}"
                        )

# ==========================================
# A PROPOS
# ==========================================

elif page == "À propos":

    st.title("À propos de LUCAS ART")

    st.markdown("""
    ### Un univers artistique personnel

    Bienvenue dans mon univers.

    À travers mes peintures, je souhaite partager
    ma passion pour les couleurs, les formes,
    les matières et les émotions.

    Chaque tableau est une invitation à découvrir
    une nouvelle sensibilité artistique.

    Merci de votre visite et de votre intérêt
    pour mon travail.
    """)

# ==========================================
# CONTACT
# ==========================================

elif page == "Contact":

    st.title("Entrons en contact")

    st.write("""
    Une peinture vous intéresse ?
    Vous souhaitez connaître sa disponibilité
    ou obtenir davantage de renseignements ?
    """)

    if EMAIL:
        st.link_button(
            "✉ Contacter LUCAS ART",
            "mailto:" + EMAIL + "?subject=" + quote(
                "Contact depuis LUCAS ART"
            )
        )
    else:
        st.info("Adresse de contact en cours de configuration.")

# ==========================================
# ADMINISTRATION
# ==========================================

st.divider()

with st.expander("🔐 Espace administrateur"):

    if not ADMIN_PASSWORD:
        st.error(
            "L'administration n'est pas configurée. "
            "Définissez ADMIN_PASSWORD."
        )
    else:
        password = st.text_input(
            "Mot de passe",
            type="password",
            key="admin_password"
        )

        if password and password == ADMIN_PASSWORD:

            st.success("Accès administrateur autorisé.")

            st.subheader("Ajouter une œuvre")

            with st.form("nouvelle_oeuvre"):

                titre = st.text_input("Titre du tableau")
                description = st.text_area("Description")
                technique = st.text_input(
                    "Technique : huile, acrylique, etc."
                )
                dimensions = st.text_input(
                    "Dimensions : 50 x 70 cm"
                )
                annee = st.text_input("Année de création")
                prix = st.text_input("Prix : exemple 250 €")

                fichier = st.file_uploader(
                    "Photographie du tableau",
                    type=["jpg", "jpeg", "png", "webp"]
                )

                valider = st.form_submit_button("Publier l'œuvre")

                if valider:

                    if not titre or fichier is None:
                        st.error("Le titre et la photo sont obligatoires.")

                    else:
                        try:
                            image = Image.open(fichier)
                            image.verify()

                            fichier.seek(0)
                            image = Image.open(fichier).convert("RGB")
                            image.thumbnail((2400, 2400))

                            nom = uuid.uuid4().hex + ".jpg"
                            image.save(
                                DOSSIER / nom,
                                format="JPEG",
                                quality=90
                            )

                            ajouter_oeuvre((
                                titre, description, technique,
                                dimensions, annee, prix, nom
                            ))

                            st.success("Œuvre publiée !")
                            st.rerun()

                        except Exception:
                            st.error("Le fichier image est invalide.")

            st.divider()
            st.subheader("Gérer les œuvres")

            for o in liste_oeuvres():
                gauche, droite = st.columns([4, 1])

                with gauche:
                    st.write("**" + o[1] + "**")

                with droite:
                    if st.button("Supprimer", key=f"del_{o[0]}"):
                        supprimer_oeuvre(o[0])
                        st.rerun()

        elif password:
            st.error("Mot de passe incorrect.")

# ==========================================
# PIED DE PAGE
# ==========================================

st.markdown("---")
st.markdown(
    "<center style='color:#8b8178'>"
    "© 2026 LUCAS ART — Tous droits réservés"
    "</center>",
    unsafe_allow_html=True
)
