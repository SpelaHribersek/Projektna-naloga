import csv
import pandas as pd

def shrani_nobelovce(obogateno_df):
    obogateno_df.rename(columns={
        "LETO": "leto",
        "PODROČJE": "podrocje",
        "NOBELOV NAGRAJENEC": "ime",
        "poklic": "poklic",
        "rojstvo": "datum rojstva",
        "kraj_rojstva": "kraj rojstva",
        "nagrade": "nagrade"
    }, inplace=True)
    
    obogateno_df.to_csv("nagrajenci.csv", index=False, encoding="utf-8")
