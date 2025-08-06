import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time

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
            return {'narodnost': None, 'rojstvo': None, 'nagrade': None}

        narodnost = None
        rojstvo = None
        nagrade = []

        for vrstica in infobox.find_all('tr'):
            naslov = vrstica.find('th')
            podatki = vrstica.find('td')

            if not naslov or not podatki:
                continue

            label = naslov.text.strip().lower()

            if 'born' in label:
                rojstvo = podatki.text.strip().replace('\n', ' ')
            elif 'nationality' in label:
                narodnost = podatki.text.strip().replace('\n', ' ')
            elif 'awards' in label:
                nagrade = [el.text.strip() for el in podatki.find_all(['a', 'li']) if el.text.strip()]
                if not nagrade:
                    nagrade = [podatki.text.strip().replace('\n', ' ')]

        return {
            'narodnost': narodnost,
            'rojstvo': rojstvo,
            'nagrade': ', '.join(nagrade) if nagrade else None
        }

    except Exception as e:
        return {'narodnost': None, 'rojstvo': None, 'nagrade': None}



# Pridobivanje dodatnih podatkov z napredkom
podatki_oseb = []
for url in tqdm(osnovni_podatki['URL'], desc="Pridobivanje podatkov z Wikipedije"):
    oseba = pridobi_podrobnejše_podatke(url)
    podatki_oseb.append(oseba)
    time.sleep(1)  # Ne obremenjuj Wikipedije prehitro

# Združi s tabelo
dodatni_df = pd.DataFrame(podatki_oseb)
obogateno = pd.concat([osnovni_podatki.reset_index(drop=True), dodatni_df], axis=1)


print(obogateno.head(10))




# def pridobi_link_nagrajenca(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')

#         infobox = soup.find('table', {'class': 'infobox biography vcard'})

#         if not infobox:
#             return {'narodnost': None, 'rojstvo': None, 'nagrade': None}

#         vrstice = infobox.find_all('tr')

#         narodnost = None
#         rojstvo = None
#         nagrade = []

#         for vrstica in vrstice:
#             header = vrstica.find('th')
#             if not header:
#                 continue
#             label = header.text.strip().lower()

#             if 'born' in label:
#                 rojstvo = vrstica.find('td').text.strip()
#             elif 'nationality' in label:
#                 narodnost = vrstica.find('td').text.strip()
#             elif 'awards' in label:
#                 nagrade_td = vrstica.find('td')
#                 if nagrade_td:
#                     nagrade = [el.text.strip() for el in nagrade_td.find_all(['a', 'li']) if el.text.strip()]
#                     if not nagrade:  # fallback
#                         nagrade = [nagrade_td.text.strip()]

#         return {
#             'narodnost': narodnost,
#             'rojstvo': rojstvo,
#             'nagrade': ', '.join(nagrade) if nagrade else None
#         }

#     except Exception as e:
#         return {'narodnost': None, 'rojstvo': None, 'nagrade': None}
    
# def pridobi_podatke(url):
#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')

#         infobox = soup.find('table', {'class': 'infobox'})
#         if not infobox:
#             return {'narodnost': None, 'rojstvo': None, 'nagrade': None}

#         narodnost = None
#         rojstvo = None
#         nagrade = []

#         for vrstica in infobox.find_all('tr'):
#             naslov = vrstica.find('th')
#             podatki = vrstica.find('td')

#             if not naslov or not podatki:
#                 continue

#             label = naslov.text.strip().lower()

#             if 'born' in label:
#                 rojstvo = podatki.text.strip().replace('\n', ' ')
#             elif 'nationality' in label:
#                 narodnost = podatki.text.strip().replace('\n', ' ')
#             elif 'awards' in label:
#                 # Poskusi dobiti vse povezave ali besedilo
#                 nagrade = [el.text.strip() for el in podatki.find_all(['a', 'li']) if el.text.strip()]
#                 if not nagrade:
#                     nagrade = [podatki.text.strip().replace('\n', ' ')]

#         return {
#             'narodnost': narodnost,
#             'rojstvo': rojstvo,
#             'nagrade': ', '.join(nagrade) if nagrade else None
#         }

#     except Exception as e:
#         return {'narodnost': None, 'rojstvo': None, 'nagrade': None}

# # Dodaj stolpce z napredkom
# dodatki = []
# for url in tqdm(osnovni_podatki['URL'], desc="Pridobivanje podatkov z Wikipedije"):
#     podatki = pridobi_podatke(url)
#     dodatki.append(podatki)
#     time.sleep(1)  # da ne preobremeniš Wikipedije

# # Združi vse
# dodatni_df = pd.DataFrame(dodatki)
# obogateno = pd.concat([osnovni_podatki.reset_index(drop=True), dodatni_df], axis=1)

# # Preglej rezultate
# print(obogateno.head())



