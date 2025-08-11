import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
from shrani import shrani_nobelovce

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

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

# Odstrani vrstice brez nagrajencev
osnovni_podatki = osnovni_podatki.dropna(subset=['NOBELOV NAGRAJENEC']).reset_index(drop=True)

# Razdeli nagrajence po ';' in razširi v vrstice
osnovni_podatki['NOBELOV NAGRAJENEC'] = osnovni_podatki['NOBELOV NAGRAJENEC'].str.split(';')
osnovni_podatki = osnovni_podatki.explode('NOBELOV NAGRAJENEC')
osnovni_podatki['NOBELOV NAGRAJENEC'] = osnovni_podatki['NOBELOV NAGRAJENEC'].str.strip()
osnovni_podatki = osnovni_podatki[osnovni_podatki['NOBELOV NAGRAJENEC'] != '']

# PRIDOBIVANJE DODATNIH PODATKOV O NOBELOVIH NAGRAJENCIH!!!

import urllib.parse

osnovni_podatki['URL'] = osnovni_podatki['NOBELOV NAGRAJENEC'].apply(
    lambda x: 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(x.strip().replace(' ', '_'))
)






def pridobi_podrobnejše_podatke(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        infobox = soup.find('table', {'class': 'infobox'})

        if not infobox:
            return {'poklic': None, 'rojstvo': None, 'kraj_rojstva': None, 'nagrade': None}

        poklic = None
        rojstvo = None
        kraj_rojstva = None
        nagrade = []

        for vrstica in infobox.find_all('tr'):
            naslov = vrstica.find('th')
            podatki = vrstica.find('td')

            if not naslov or not podatki:
                continue

            label = naslov.text.strip().lower()

            # datum in kraj rojstva
            if 'born' in label:
                bday = podatki.find('span', {'class': 'bday'})
                if bday:

                    rojstvo = bday.text.strip()

                    full_text = podatki.text.strip()

                    kraj_rojstva = full_text.replace(rojstvo, '').strip('() ,\n')

                else:

                    parts = podatki.text.strip().split('(')
                    rojstvo = parts[0].strip()
                    if len(parts) > 1:
                        kraj_rojstva = parts[1].strip(') ')

            # Poklic
            if 'occupation' in label:
                poklic = podatki.text.strip().replace('\n', ' ')

            # nagrade
            elif 'awards' in label:
                nagrade = [el.text.strip() for el in podatki.find_all(['a', 'li']) if el.text.strip()]
                if not nagrade:
                    nagrade = [podatki.text.strip().replace('\n', ' ')]

        return {
            'poklic': poklic,
            'rojstvo': rojstvo,
            'kraj_rojstva': kraj_rojstva,
            'nagrade': ', '.join(nagrade) if nagrade else None
        }

    except Exception as e:
        return {'poklic': None, 'rojstvo': None, 'kraj_rojstva': None, 'nagrade': None}


 
podatki_oseb = []
for url in tqdm(osnovni_podatki['URL'], desc="Pridobivanje podatkov z Wikipedije"):
    oseba = pridobi_podrobnejše_podatke(url)
    podatki_oseb.append(oseba)
    time.sleep(1)  

dodatni_df = pd.DataFrame(podatki_oseb)
obogateno = pd.concat([osnovni_podatki.reset_index(drop=True), dodatni_df], axis=1)



shrani_nobelovce(obogateno)





