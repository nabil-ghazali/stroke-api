from typing import Optional
import pandas as pd
import numpy as np

# Chargement des données (une fois)
stroke_data_df = pd.read_parquet("stroke_api/data/hearth_data.parquet")

# Tester l'app avec :
# poetry run fastapi dev stroke_api/main.py
# http://127.0.0.1:8000/docs : utiliser la fonctionnalité Try it out pour tester les routes

# Ajout des fonctions de filtrage des données cf notebook 1
# fonction filter_patient paramètre max_age optionnel

def filter_patient(max_age , gender , stroke) -> dict:
   """
   Filtre les patients selon l'âge maximal, le genre et l'état AVC.

   Cette fonction sélectionne les patients dans un DataFrame qui répondent
   aux critères suivants :
    - Âge inférieur ou égal à `max_age`
    - Sexe égal à `gender` (insensible à la casse)
    - AVC (`stroke`) égal à 0 ou 1

   Parameters
   ----------
   df : pd.DataFrame
     Le DataFrame contenant les données des patients.
   max_age : float
     L'âge maximal des patients à inclure dans le filtre.
   gender : str
     Le sexe du patient à filtrer (ex. : 'male' ou 'female').
     La comparaison est insensible à la casse.
   stroke : int
     1 pour sélectionner uniquement les patients ayant eu un AVC,
     0 pour ceux qui n’en ont pas eu.

   Returns
   -------
    dict
     Un dictionnaire de la forme `list[dict]` représentant les enregistrements filtrés.
     Chaque dictionnaire correspond à une ligne (patient).

   Example
   -------
   >>> filter_patient(data_hearth, 60, 'male', 1)
   [{'id': ..., 'age': ..., 'gender': 'Male', 'stroke': 1, ...}, ...]
   """

   df = stroke_data_df.copy()

   if max_age is not None:
      df= df[df['age'] <= max_age ]
   if stroke is not None:
      df = df[df['stroke']== stroke]
   if gender is not None: 
      df = df[df['gender'].str.lower() == gender]

   return df.to_dict('records')


# Ensuite faire appel à ces fonctions dans le fichier api.py où sont définies les routes.
# Ajouter les fonctions de filtrage pour les autres routes.

def filter_patient_id(id: int) -> dict:
   """
   Filtre les patients selon l'identifiant (ID).

   Cette fonction sélectionne le ou les patients dans le DataFrame
   dont l'identifiant correspond à la valeur donnée.

    - ID : identifiant du patient

   Parameters
   ----------
   Id : int    
    
   L'identifiant unique du patient à rechercher.

   Returns
   -------
    dict
     Un dictionnaire de la forme `list[dict]` représentant les enregistrements filtrés.
     Chaque dictionnaire correspond à une ligne (patient).

   Example
   -------
   >>> filter_patient(id: int)
   [{'id': ..., 'age': ..., 'gender': 'Male', 'stroke': 1, ...}, ...]
   """

   df = stroke_data_df.copy()
  
   result= df[df['id'] == id ]
   if result.empty:
      return None
   else :   
    return result.to_dict('records')
   

def stat_patients():
    """
    Calcule des statistiques globales sur le jeu de données stroke_data_df.

    Retour
    ------
    dict : {
        "total_patients": int,
        "avg_age": float,
        "age_min": float,
        "age_max": float,
        "age_std": float,
        "stroke_rate": float,  # en %
        "stroke_counts": dict,
        "gender_distribution": dict,
        "gender_stroke": list of dicts,
        "stroke_by_gender": dict,
        "smoking_stroke": list of dicts,
        "stroke_by_smoking": dict
    }
    """
    df = stroke_data_df.copy()

    total_patients = len(df)
    if total_patients == 0:
        return {"message": "Aucun patient trouvé."}

    # Statistiques sur l'âge
    avg_age = round(df["age"].mean(), 2)
    age_min = round(df["age"].min(), 2)
    age_max = round(df["age"].max(), 2)
    age_std = round(df["age"].std(), 2)

    # Répartition AVC
    stroke_rate = round(df["stroke"].mean() * 100, 2)
    stroke_counts = df["stroke"].value_counts().to_dict()
    stroke_0 = stroke_counts.get(0, 0)
    stroke_1 = stroke_counts.get(1, 0)

    # Répartition par genre
    gender_distribution = df["gender"].value_counts().to_dict()

    # Répartition AVC par genre avec pourcentage
    gender_stroke_counts = (
        df.groupby(["gender", "stroke"])
        .size()
        .reset_index(name="count")
    )
    gender_stroke_counts["percent"] = round(gender_stroke_counts["count"] / total_patients * 100, 2)
    gender_stroke_counts = gender_stroke_counts.to_dict(orient="records")

    # Taux d'AVC par genre
    stroke_by_gender = (
        df.groupby("gender")["stroke"]
        .mean()
        .mul(100)
        .round(2)
        .to_dict()
    )

    # Répartition AVC par statut tabac avec pourcentage
    smoking_stroke = (
        df.groupby(["smoking_status", "stroke"])
        .size()
        .reset_index(name="count")
    )
    smoking_stroke["percent"] = round(smoking_stroke["count"] / total_patients * 100, 2)
    smoking_stroke = smoking_stroke.to_dict(orient="records")

    # Taux d'AVC par statut tabac
    stroke_by_smoking = (
        df.groupby("smoking_status")["stroke"]
        .mean()
        .mul(100)
        .round(2)
        .to_dict()
    )

    # Taux d'AVC par BMI
    df["bmi_category"] = pd.cut(
    df["bmi"],
    bins=[0, 18.5, 24.9, 29.9, np.inf],
    labels=["Sous poids", "Normal", "Surpoids", "Obésite"]
    ).round()

    stroke_by_bmi = (
      df.groupby("bmi_category", observed=True)["stroke"]  # On groupe par BMI
      .mean()                      # Moyenne = proportion de 1 (AVC)
      .mul(100)                    # On multiplie par 100 pour avoir un %
      .reset_index()
      .to_dict()                   # Conversion en dictionnaire

    )

    return {
        "total_patients": total_patients,
        "avg_age": avg_age,
        "age_min": age_min,
        "age_max": age_max,
        "age_std": age_std,
        "stroke_rate": stroke_rate,
        "stroke_counts": {"Pas d'AVC": stroke_0, "AVC": stroke_1},
        "gender_distribution": gender_distribution,
        "gender_stroke": gender_stroke_counts,
        "stroke_by_gender": stroke_by_gender,
        "smoking_stroke": smoking_stroke,
        "stroke_by_smoking": stroke_by_smoking,
        "stroke_by_bmi": stroke_by_bmi
    }
