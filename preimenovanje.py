def preimenuj(df):
    df.rename(columns={
        "LETO": "leto",
        "PODROČJE": "podrocje",
        "NOBELOV NAGRAJENEC": "ime",
        "poklic": "poklic",
        "rojstvo": "datum rojstva",
        "kraj_rojstva": "kraj rojstva",
        "nagrade": "nagrade"
    }, inplace=True)
    
    return df