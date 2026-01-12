import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
# Zastąp te dane swoimi poświadczeniami z ustawień Supabase (Settings -> API)
URL = "TWOJ_URL_SUPABASE"
KEY = "TWOJ_KLUCZ_ANON_PUBLIC"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# --- FUNKCJE LOGICZNE ---
def pobierz_produkty():
    query = supabase.table("produkty").select("*").execute()
    return query.data

def dodaj_produkt(nazwa, sku, ilosc, cena, kategoria):
    data = {
        "nazwa": nazwa,
        "sku": sku,
        "ilosc": ilosc,
        "cena": cena,
        "kategoria": kategoria
    }
    supabase.table("produkty").insert(data).execute()

def usun_produkt(product_id):
    supabase.table("produkty").delete().eq("id", product_id).execute()

# --- INTERFEJS UŻYTKOWNIKA (STREAMLIT) ---
st.set_page_config(page_title="Magazynier 2.0", layout="wide")
st.title("📦 System Zarządzania Magazynem")

menu = ["Podgląd Zapasów", "Dodaj Produkt", "Zarządzanie"]
wybor = st.sidebar.selectbox("Menu", menu)

if wybor == "Podgląd Zapasów":
    st.subheader("Aktualne stany magazynowe")
    dane = pobierz_produkty()
    if dane:
        st.dataframe(dane, use_container_width=True)
    else:
        st.info("Magazyn jest pusty.")

elif wybor == "Dodaj Produkt":
    st.subheader("Wprowadź nowy towar")
    with st.form("form_dodawania"):
        col1, col2 = st.columns(2)
        with col1:
            nazwa = st.text_input("Nazwa produktu")
            sku = st.text_input("Kod SKU (unikalny)")
            kategoria = st.selectbox("Kategoria", ["Elektronika", "Dom", "Ogród", "Inne"])
        with col2:
            ilosc = st.number_input("Ilość", min_value=0, step=1)
            cena = st.number_input("Cena jednostkowa (PLN)", min_value=0.0, format="%.2f")
        
        submit = st.form_submit_button("Zapisz w bazie")
        
        if submit:
            if nazwa and sku:
                try:
                    dodaj_produkt(nazwa, sku, ilosc, cena, kategoria)
                    st.success(f"Produkt {nazwa} został dodany!")
                except Exception as e:
                    st.error(f"Błąd: {e}")
            else:
                st.warning("Pola Nazwa i SKU są wymagane.")

elif wybor == "Zarządzanie":
    st.subheader("Usuwanie produktów")
    produkty = pobierz_produkty()
    if produkty:
        lista_opcji = {f"{p['nazwa']} (SKU: {p['sku']})": p['id'] for p in produkty}
        wybrany = st.selectbox("Wybierz produkt do usunięcia", options=list(lista_opcji.keys()))
        
        if st.button("Usuń trwale", type="primary"):
            usun_produkt(lista_opcji[wybrany])
            st.rerun()
    else:
        st.write("Brak produktów do wyświetlenia.")
