import streamlit as st
from supabase import create_client, Client


# --- 1. KONFIGURACJA POŁĄCZENIA ---
# Dane Twojego projektu "Baza danych"
SUPABASE_URL = "https://uggsrizjsnyjsxoyvhtb.supabase.co"
SUPABASE_KEY = "sb_publishable_M8SPl2SHiiakYylbxCg2Og_8l31a2dT"

@st.cache_resource
def init_connection() -> Client:
    """Inicjalizuje połączenie z Supabase (Client to typ obiektu)."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- 2. LOGIKA BIZNESOWA (FUNKCJE) ---

def pobierz_kategorie():
    """Pobiera wszystkie rekordy z tabeli Kategorie."""
    res = supabase.table("Kategorie").select("*").order("nazwa_kategorii").execute()
    return res.data

def pobierz_produkty_z_kategoriami():
    """Pobiera produkty łącząc je z tabelą Kategorie (Inner Join)."""
    # Składnia "*, Kategorie(nazwa_kategorii)" pobiera dane z relacji
    res = supabase.table("Produkty").select("*, Kategorie(nazwa_kategorii)").execute()
    return res.data

def dodaj_produkt(nazwa, cena, ilosc, kat_id):
    data = {"nazwa": nazwa, "cena": cena, "ilosc": ilosc, "kategoria_id": kat_id}
    return supabase.table("Produkty").insert(data).execute()

def usun_produkt(prod_id):
    return supabase.table("Produkty").delete().eq("id", prod_id).execute()

# --- 3. INTERFEJS UŻYTKOWNIKA (UI) ---

st.set_page_config(page_title="Magazyn Pro", layout="wide", page_icon="📦")

# Sidebar - Nawigacja
st.sidebar.title("🎮 Panel Sterowania")
strona = st.sidebar.selectbox("Przejdź do:", ["Dashboard", "Zarządzanie Produktami", "Kategorie", "Ustawienia"])

# --- STRONA: DASHBOARD ---
if strona == "Dashboard":
    st.title("📊 Dashboard Magazynowy")
    
    produkty = pobierz_produkty_z_kategoriami()
    if produkty:
        df = pd.DataFrame(produkty)
        
        # Szybkie statystyki w kolumnach
        c1, c2, c3 = st.columns(3)
        c1.metric("Liczba Produktów", len(df))
        c2.metric("Łączna Wartość", f"{sum(df['cena'] * df['ilosc']):,.2f} PLN")
        c3.metric("Liczba Kategorii", len(df['kategoria_id'].unique()))
        
        st.divider()
        
        # Wykres rozkładu towarów (wymaga plotly)
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Stany magazynowe")
            st.bar_chart(df.set_index('nazwa')['ilosc'])
    else:
        st.warning("Baza danych jest pusta. Przejdź do zakładki Zarządzanie, aby dodać towar.")

# --- STRONA: ZARZĄDZANIE PRODUKTAMI ---
elif strona == "Zarządzanie Produktami":
    st.title("📦 Produkty")
    
    tab1, tab2 = st.tabs(["📋 Lista i Edycja", "➕ Dodaj Nowy Produkt"])
    
    with tab1:
        produkty = pobierz_produkty_z_kategoriami()
        if produkty:
            # Przekształcenie danych do czytelnej tabeli
            clean_data = []
            for p in produkty:
                clean_data.append({
                    "ID": p['id'],
                    "Nazwa": p['nazwa'],
                    "Cena": f"{p['cena']} PLN",
                    "Ilość": p['ilosc'],
                    "Kategoria": p['Kategorie']['nazwa_kategorii'] if p['Kategorie'] else "Brak"
                })
            df_display = pd.DataFrame(clean_data)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Usuwanie
            with st.expander("🗑️ Usuń produkt"):
                to_delete = st.selectbox("Wybierz produkt do usunięcia", options=df_display['Nazwa'].tolist())
                if st.button("Potwierdź usunięcie", type="primary"):
                    prod_id = df_display[df_display['Nazwa'] == to_delete]['ID'].values[0]
                    usun_produkt(prod_id)
                    st.success(f"Usunięto {to_delete}")
                    st.rerun()
        else:
            st.info("Brak produktów.")

    with tab2:
        kategorie = pobierz_kategorie()
        if not kategorie:
            st.error("Najpierw musisz dodać przynajmniej jedną kategorię!")
        else:
            with st.form("add_product_form"):
                n = st.text_input("Nazwa produktu")
                c = st.number_input("Cena (PLN)", min_value=0.0, step=0.01)
                i = st.number_input("Ilość na stanie", min_value=0, step=1)
                k_opcje = {kat['nazwa_kategorii']: kat['id'] for kat in kategorie}
                k_wybor = st.selectbox("Kategoria", options=list(k_opcje.keys()))
                
                if st.form_submit_button("Zapisz do Bazy"):
                    if n:
                        dodaj_produkt(n, c, i, k_opcje[k_wybor])
                        st.success("Produkt dodany pomyślnie!")
                        st.rerun()

# --- STRONA: KATEGORIE ---
elif strona == "Kategorie":
    st.title("📂 Kategorie")
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("Dodaj kategorię")
        nowa_kat = st.text_input("Nazwa nowej kategorii")
        if st.button("Dodaj"):
            if nowa_kat:
                supabase.table("Kategorie").insert({"nazwa_kategorii": nowa_kat}).execute()
                st.success("Dodano!")
                st.rerun()
                
    with col_b:
        st.subheader("Istniejące kategorie")
        kat_data = pobierz_kategorie()
        if kat_data:
            st.table(pd.DataFrame(kat_data)[['id', 'nazwa_kategorii']])
