
import streamlit as st
from supabase import create_client, Client

# Pobieranie danych projektu z sekcji Secrets Streamlita
# (Lokalnie możesz je wpisać w cudzysłów, jeśli nie używasz .streamlit/secrets.toml)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except:
    # Opcja awaryjna do testów lokalnych - zastąp swoimi danymi z projektu "Baza danych"
    url = "https://TWOJ-PROJEKT.supabase.co"
    key = "TWOJ-KLUCZ-ANON"

@st.cache_resource
def get_supabase_client():
    return create_client(url, key)

db = get_supabase_client()

# --- Aplikacja ---
st.title("🗄️ Projekt: Baza danych")

def wyswietl_tabele():
    # Pobieramy dane z tabeli o nazwie 'produkty'
    response = db.table("produkty").select("*").execute()
    return response.data

try:
    dane = wyswietl_tabele()
    if dane:
        st.write("### Lista produktów w magazynie:")
        st.table(dane)
    else:
        st.info("Połączono z projektem 'Baza danych', ale tabela 'produkty' jest pusta.")
except Exception as e:
    st.error(f"Nie udało się pobrać danych. Upewnij się, że tabela 'produkty' istnieje w projekcie. Błąd: {e}")
