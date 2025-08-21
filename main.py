from pridobivanje_podatkov import pridobi_podatke
from preimenovanje import preimenuj
from pocisti_podatke import pocisti

dataframe = pridobi_podatke()
dataframe_urejen = pocisti(dataframe)

dataframe_urejen.to_csv("nagrajenci.csv", index=False, encoding='utf-8-sig')




