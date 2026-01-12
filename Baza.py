import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- KONFIGURACJA POŁĄCZENIA ---
# Dane projektu "Baza danych" z panelu Supabase (Settings -> API)
URL = "https://uggsrizjsnyjsxoyvhtb.supabase.co"
KEY = "sb_publishable_M8SPl2SHiiakYylbxCg2Og_8l31a2dT"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- FUNKCJE POBIERANIA DANYCH ---
def pobierz_kategorie():
    res = supabase.table("Kategorie").select("*").execute()
    return res.data

def pobierz_produkty():
    # Pobieramy produkty wraz z danymi z powiązanej tabeli Kategorie
    res = supabase.table("Produkty").select("*, Kategorie(nazwa_kategorii)").execute()
    return res.data

# --- INTERFEJS UŻYTKOWNIKA ---
st.set_page_config(page_title="Magazyn: Baza danych", layout="wide")
st.title("🗄️ System Zarządzania: Baza danych")

menu = st.sidebar.radio("Nawigacja", ["Podgląd Produktów", "Lista Kategorii", "Dodaj Nowy"])

if menu == "Podgląd Produktów":
    st.subheader("📦 Aktualny stan produktów")
    produkty = pobierz_produkty()
    if produkty:
        df = pd.DataFrame(produkty)
        # Wyświetlamy tabelę z produktami
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Brak produktów w tabeli 'Produkty'.")

elif menu == "Lista Kategorii":
    st.subheader("📂 Dostępne kategorie")
    kategorie = pobierz_kategorie()
    if kategorie:
        st.table(kategorie)
    else:
        st.info("Brak zdefiniowanych kategorii w tabeli 'Kategorie'.")

elif menu == "Dodaj Nowy":
    st.subheader("➕ Dodawanie do magazynu")
    kat_list = pobierz_kategorie()
    opcje_kat = {k['nazwa_kategorii']: k['id'] for k in kat_list} if kat_list else {}
    
    with st.form("form_produkt"):
        nazwa = st.text_input("Nazwa produktu")
        cena = st.number_input("Cena", min_value=0.0)
        wybrana_kat = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
        
        if st.form_submit_button("Zapisz produkt"):
            nowy = {
                "nazwa": nazwa,
                "cena": cena,
                "kategoria_id": opcje_kat[wybrana_kat]
            }
            supabase.table("Produkty").insert(nowy).execute()
            st.success(f"Dodano {nazwa} do bazy!")
