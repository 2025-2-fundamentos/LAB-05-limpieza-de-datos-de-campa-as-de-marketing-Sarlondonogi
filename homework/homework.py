# pylint: disable=import-outside-toplevel
#Se importan todas las liberías necesarias.  Import os se menciona en los test.
import pandas as pd
import zipfile
import os
import glob


#Limpie los datos de una campaña de marketing realizada por un banco
def clean_campaign_data():
    #Definicion de rutas
    input_dir = "files/input/"
    output_dir = "files/output/"
    os.makedirs(output_dir, exist_ok=True)

    #Lee los archivos
    #Buscar archivos en la ruta que finalicen en ".csv.zip" y se evita descomprimirlos
    zip_files = glob.glob(os.path.join(input_dir, "*.csv.zip"))
    dataframes = []

    for zip_path in zip_files:
        with zipfile.ZipFile(zip_path, "r") as archive:
            for file_name in archive.namelist():
                if file_name.endswith(".csv"):
                    with archive.open(file_name) as f:
                        df = pd.read_csv(f)
                        dataframes.append(df)

    #Une todos los datos
    df = pd.concat(dataframes, ignore_index=True)

    #Se crea el primer archivo pedido, es decir, el archivo cliente
    df_client = df[["client_id", "age", "job", "marital", "education", "credit_default", "mortgage" ]].copy()
    #Se cambia el "." por "" y el "-" por "_"
    #Se cambia "." por "_" y "unknown" por pd.NA
    #Convierte a "yes" a 1 y cualquier otro valor a 0
    df_client["job"] = df_client["job"].str.replace(".", "", regex=False).str.replace("-", "_", regex=False)
    df_client["education"] = df_client["education"].str.replace(".", "_", regex=False)
    df_client["education"] = df_client["education"].replace("unknown", pd.NA)
    df_client["credit_default"] = df_client["credit_default"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    df_client["mortgage"] = df_client["mortgage"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    df_client.to_csv(os.path.join(output_dir, "client.csv"), index=False)

    #Se crea el segundo archivo pedido, es decir, el archivo campaign
    df_campaign = df[["client_id", "number_contacts", "contact_duration", "previous_campaign_contacts", "previous_outcome", "campaign_outcome", "day", "month"]].copy()
    #Se cambia "success" por 1, y cualquier otro valor a 0
    #Se cambia "yes" por 1 y cualquier otro valor a 0
    df_campaign["previous_outcome"] = df_campaign["previous_outcome"].apply(lambda x: 1 if str(x).lower() == "success" else 0)
    df_campaign["campaign_outcome"] = df_campaign["campaign_outcome"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
    #Se crea un valor con el formato "YYYY-MM-DD", combinando los campos "day" y "month" con el año 2022.
    month_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    df_campaign["month"] = df_campaign["month"].str.lower().map(month_map)
    df_campaign["day"] = df_campaign["day"].astype(int).astype(str).str.zfill(2)
    df_campaign["last_contact_date"] = "2022-" + df_campaign["month"] + "-" + df_campaign["day"]
    df_campaign.drop(columns=["day", "month"], inplace=True)
    df_campaign.to_csv(os.path.join(output_dir, "campaign.csv"), index=False)

    #Se crea el tercer archivo pedido, es decir, el archivo economics
    df_economics = df[["client_id", "cons_price_idx", "euribor_three_months"]].copy()
    df_economics.to_csv(os.path.join(output_dir, "economics.csv"), index=False)


if __name__ == "__main__":
    clean_campaign_data()

