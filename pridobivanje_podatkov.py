import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
import urllib.parse
from preimenovanje import preimenuj

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

def pridobi_podatke():

    url = 'https://en.wikipedia.org/wiki/List_of_Nobel_laureates'
    response = requests.get(url, headers=headers)
    juha = BeautifulSoup(response.text, "html.parser")

    tabele = juha.find_all("table", {"class": "wikitable"})
    df = pd.read_html(str(tabele[0]))[0]

    # PREIMENOVANJE
    df = df.rename(columns={'Year': 'LETO'})
    df = df.rename(columns={
        'Physics': 'Fizika',
        'Chemistry': 'Kemija',
        'Physiology or Medicine': 'Psihologija ali medicina',
        'Literature': 'Literatura',
        'Peace': 'Mir',
        'Prize in Economic Sciences [13][a]': 'Ekonomija'
    })

    # Stolpce področij razširimo v vrstice
    osnovni_podatki = df.melt(
        id_vars=['LETO'],
        value_vars=['Fizika', 'Kemija', 'Psihologija ali medicina', 'Literatura', 'Mir', 'Ekonomija'],
        var_name='PODROČJE',
        value_name='NOBELOV NAGRAJENEC'
    )

    osnovni_podatki = osnovni_podatki[~osnovni_podatki['NOBELOV NAGRAJENEC'].astype(str).str.strip().isin(['—', '-', '–'])]
    osnovni_podatki = osnovni_podatki.dropna(subset=['NOBELOV NAGRAJENEC']).reset_index(drop=True)

    # Razdeli nagrajence po ';' in razširi v vrstice
    osnovni_podatki['NOBELOV NAGRAJENEC'] = osnovni_podatki['NOBELOV NAGRAJENEC'].str.split(';')
    osnovni_podatki = osnovni_podatki.explode('NOBELOV NAGRAJENEC')
    osnovni_podatki['NOBELOV NAGRAJENEC'] = osnovni_podatki['NOBELOV NAGRAJENEC'].str.strip()
    osnovni_podatki = osnovni_podatki[osnovni_podatki['NOBELOV NAGRAJENEC'] != '']

    # URL do strani nagrajenca
    osnovni_podatki['URL'] = osnovni_podatki['NOBELOV NAGRAJENEC'].apply(
        lambda x: 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(x.strip().replace(' ', '_'))
    )

    def pridobi_podrobnejše_podatke(url):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            juha = BeautifulSoup(response.text, 'html.parser')

            infobox = juha.find('table', {'class': 'infobox'})
            if not infobox:
                return {'rojstvo': None, 'kraj_rojstva': None, 'nagrade': None}

            rojstvo = None
            kraj_rojstva = None
            nagrade = []

            for vrstica in infobox.find_all('tr'):
                naslov = vrstica.find('th')
                podatki = vrstica.find('td')
                if not naslov or not podatki:
                    continue
                label = naslov.text.strip().lower()

                # ---- Rojstvo (datum + kraj) ----
                if 'born' in label:
                    bday = podatki.find('span', {'class': 'bday'})
                    if bday:
                        rojstvo = bday.text.strip()
                        kraj_rojstva = podatki.get_text(" ", strip=True).replace(rojstvo, "").strip(" ,;()")
                    else:
                        full_text = podatki.get_text(" ", strip=True)
                        deli = full_text.split("(")
                        rojstvo = deli[0].strip()
                        if len(deli) > 1:
                            kraj_rojstva = deli[1].replace(")", "").strip()

                # ---- Nagrade ----
                elif 'awards' in label:
                    items = [el.get_text(" ", strip=True) for el in podatki.find_all(['a', 'li'])]
                    if not items:
                        items = [podatki.get_text(" ", strip=True)]
                    seen = set()
                    nagrade = [x for x in items if not (x in seen or seen.add(x))]

            return {
                'rojstvo': rojstvo,
                'kraj_rojstva': kraj_rojstva,
                'nagrade': ", ".join(nagrade) if nagrade else None
            }

        except Exception:
            return {'rojstvo': None, 'kraj_rojstva': None, 'nagrade': None}

    # Pridobivanje podrobnih podatkov za vse nagrajence
    podatki_oseb = []
    for url in tqdm(osnovni_podatki['URL'], desc="Pridobivanje podatkov z Wikipedije"):
        oseba = pridobi_podrobnejše_podatke(url)
        podatki_oseb.append(oseba)
        time.sleep(1)

    dodatni_df = pd.DataFrame(podatki_oseb)
    df_vsi_podatki = pd.concat([osnovni_podatki.reset_index(drop=True), dodatni_df], axis=1)
    
    preimenuj(df_vsi_podatki)

    return df_vsi_podatki