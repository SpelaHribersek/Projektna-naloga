# Projektna naloga
AVTORICA: Špela Hriberšek

## Uvod
Za svojo projektno nalogo sem se odločila analizirati spletno stran https://en.wikipedia.org/wiki/List_of_Nobel_laureates, kjer so zbrani podatki o vseh Nobelovnih nagrajencih med leti 1901 in 2024 na vseh področjih. Dostopala sem do spletne strani vsake osebe posebej, da sem pridobila tudi njihov rojstni datum in kraj ter ostale nagrade, ki so jih prejeli.

## Navodila za uporabo
Za delovanje tega programa so potrebne knjižnice: requests, BeautifulSoup, pandas, tqdm, time, urllib.parse, re in matplotlib.pyplot. Da se program izvede je treba le pognati datoteko main.py. To bo ustvarilo datoteko nagrajenci.csv. Nato pa si lahko ogledate rezultate v datoteki analiza_podatkov.ipynb.

## Opis datotek
- main.py je glavna datoteka, v kateri se izvedejo vse potrebne funkcije
- pridobivanje_podatkov.py je datoteka, v kateri poberemo podatke s spletne strani in jih v grobem uredimo. V njej uporabimo tudi funkcijo preimenuj iz datoteke preimenovanje.py.
- pocisti_podatke.py je datoteka, v kateri uredimo podatke.
- Datoteka nagrajenci.csv nastane, ko poženemo main.py. V njej so shranjeni vsi podatki.
- analiza_podatkov.ipynb je datoteka, ki s tabelami in grafi prikaže podatke in njihovo analizo.
