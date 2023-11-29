import base64
from pathlib import Path
import streamlit as st
import pandas as pd
import requests as request

# List of main Italian cities
italian_cities = ["Milano", "Roma", "Napoli", "Bologna", "Firenze"]

def read_pdf_file(pdf_path):
    with open(pdf_path, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800px" height="2100px" type="application/pdf"></iframe>'

def scrape(category, cities, num_pages):
    base_url = "https://www.paginegialle.it"
    results_by_city = {}

    for city in cities:
        city_results = {}

        for k in range(1, num_pages + 1):
            search_url = f"{base_url}/ricerca/{category}/{city}"

            if k == 1:
                search_url_ = search_url + '?output=json'
            else:
                search_url_ = search_url + f'/p-{k}?output=json'

            response = request.get(search_url_)

            json_data = response.json()       

            if 'list' in json_data and 'out' in json_data['list'] and 'base' in json_data['list']['out']:
                json_info = json_data['list']['out']['base']['results']

                for k in json_info:
                    loc = k.get("loc", "")
                    if loc.lower() != city.lower():
                        continue

                    ds_ragsoc = k.get("ds_ragsoc", "")
                    addr = k.get("addr", "")
                    PIVA = k.get("ds_pi", "")
                    prov = k.get("prov", "")
                    zip_cod = k.get("ds_cap", "")

                    ds_ls_telefoni = ""
                    try:
                        ds_ls = k["ds_ls_telefoni"]
                        ds_ls_telefoni = ", ".join(ds_ls)
                    except KeyError:
                        pass

                    site_link = k.get("extra", {}).get("site_link", {}).get("url", "")
                    p_link = k.get("extra", {}).get("urlms", "")

                    email = ""
                    try:
                        mail = k["ds_ls_email"]
                        email = ", ".join(mail)
                    except KeyError:
                        pass

                    whatsapp = ""
                    try:
                        wa = k["ds_ls_telefoni_whatsapp"]
                        whatsapp = ", ".join(wa)
                    except KeyError:
                        pass

                    city_results[ds_ragsoc] = {'indirizzo': addr, 'prov': prov, 'città': loc, 'cap': zip_cod, 'P. IVA': PIVA,
                                        'telefoni': ds_ls_telefoni, 'whatsapp': whatsapp, 'email': email,
                                        'sito web': site_link,
                                        'pagine gialle': p_link}

        df = pd.DataFrame.from_dict(city_results, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Nome'}, inplace=True)
        results_by_city[city] = df

    return results_by_city

def main():
    tab1, tab2 = st.tabs(["Scraper", "Guida all'uso"])
    with tab1:
        st.title("Scraping Pagine Gialle")
        #with st.expander("!"):
            #pdf_path = Path(r"Istruzioni_Scraping.pdf")
            #pdf_display = read_pdf_file(pdf_path)
            #st.markdown(pdf_display, unsafe_allow_html=True)
        # Inserimento dati
        category = st.text_input("Inserisci la categoria:", "")
        
        
        
        selected_cities = st.multiselect("Seleziona le città italiane:", italian_cities)
        num_pages = st.slider("Numero di pagine da cercare:", 1, 10, 1)

        if st.button("Esegui scraping"):
            # Bottone Avvio
            results = scrape(category, selected_cities, num_pages)

            st.subheader("")
            for city, df in results.items():
                st.subheader(f"{city}:")
                st.write(df)
    with tab2:
        st.markdown('### Guida \n Il codice è strutturato come uno script interattivo che consente agli utenti di **specificare la categoria di aziende, le città di interesse e il numero di pagine da cercare**.\n \nL\'obiettivo principale è **estrarre informazioni aziendali**, come nomi, indirizzi, numeri di telefono, e-mail, e altro, per la categoria specificata in diverse città italiane.\n\n L’utente dovrà procedere all’inserimento nella voce “Inserisci la categoria:” della figura professionale / società che desidera cercare. *Ad esempio, può inserire "ristorante", "hotel", "parrucchiere", ecc*. **La declinazione al plurale non altera i risultati dello scraping, l’inserimento di “ristoranti” al posto di “ristorante” restituirà gli stessi risultati**.\n\nIl pulsante "Esegui scraping" invierà richieste al sito web delle Pagine Gialle e recupererà le informazioni desiderate per la categoria e le città selezionate.\n\nI risultati dello scraping vengono presentati in forma tabellare per ciascuna città selezionata.\n\n  **Ogni tabella mostra informazioni dettagliate sulle aziende trovate, organizzate per nome azienda, indirizzo, provincia, città, CAP, partita IVA, numeri di telefono, WhatsApp, e-mail, sito web e un link alle Pagine Gialle**. \n\n **È possibile scaricare la tabella muovendo il cursore in alto a destra della tabella, il file scaricato sarà un file CVS** (compatibile con Google Sheets o Excel).')

        
    

if __name__ == "__main__":
    main()
