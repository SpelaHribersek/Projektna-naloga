import pandas as pd
import re



def pocisti(df):

    # Poenotenje datuma rojstva.
    df["datum rojstva"] = pd.to_datetime(df["datum rojstva"], errors='coerce').dt.strftime('%Y-%m-%d')


    # Izlušči državo iz kraja rojstva.
    def izlusc_drzavo(kraj):

        if pd.isna(kraj):
            return ""
        parts = kraj.split(",")
        drzava = parts[-1].strip()

        if drzava == "US":
            drzava = "U.S."
        return drzava

    df["drzava rojstva"] = df["kraj rojstva"].apply(izlusc_drzavo)


    def pocisti_nagrade(nagrade):
        if pd.isna(nagrade):
            return ""

        nagrade_pociscene = [re.sub(r"\(\d{4}\)", "", a).strip() for a in nagrade.split(",")]

        nagrade_pociscene = list(dict.fromkeys([a for a in nagrade_pociscene if a]))
        return "; ".join(nagrade_pociscene)

    df["nagrade"] = df["nagrade"].apply(pocisti_nagrade)

    final_col = ['leto', 'podrocje', 'ime', 'URL', 'datum rojstva', 'drzava rojstva', 'nagrade']
    df_urejen = df[final_col]

    return df_urejen

