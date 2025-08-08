from typing import Optional
import pandas as pd


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
   

def stat_patients ():

   df = stroke_data_df.copy()

   total_patients = len(df)
   if total_patients == 0:
      return {"message": "Aucun patient trouvé avec ces critères."}
   
   #Moyenne d'age en pourcentage
   avg_age = round(df["age"].mean(), 2)

   #Moyenne d'AVC en pourcentage
   stroke_rate = round(df["stroke"].mean() * 100, 2)  # en pourcentage

   # Grouper par 'gender' 
   gender_distribution = df["gender"].value_counts().to_dict()

   # Grouper par 'gender' et 'smoking_status'
   gender_stroke_counts = (
    df.groupby(["gender", "stroke"])
      .size()
      .reset_index(name="count")
      .to_dict(orient="records")
   )
   # Grouper par 'stroke' et 'smoking_status'
   smoking_stroke = (
      df.groupby(['smoking_status', 'stroke'])
      .size()
      .reset_index(name='count')
      .to_dict(orient='records')
   )

   #  Retour des données
   return {
        "total_patients": total_patients,
        "average_age": avg_age,
        "stroke_rate_percent": stroke_rate,
        "gender_distribution": gender_distribution,
        "gender_stroke" : gender_stroke_counts,
        "smoking_stroke" : smoking_stroke

   }



def complex_stat_patients(
    max_age: Optional[float] = None,
    gender: Optional[str] = None,
    stroke: Optional[int] = None,
    smoking_status: Optional[str] = None
) -> dict:
    """
    Statistiques dynamiques selon les paramètres fournis.
    Voir le README inline pour description des comportements selon combinaisons.
    """
    try:
        df = stroke_data_df.copy()

        # --- Filtrage de base (max_age) ---
        if max_age is not None:
            df = df[df["age"] <= float(max_age)]

        # Normaliser les colonnes textuelles pour éviter les soucis de casse
        if "gender" in df.columns:
            df["gender"] = df["gender"].fillna("").astype(str)
        if "smoking_status" in df.columns:
            df["smoking_status"] = df["smoking_status"].fillna("").astype(str)

        # --- Cas où stroke est fourni (on veut des comptes/roupements sur stroke) ---
        if stroke is not None:
            # Sous-ensemble des lignes correspondant à la valeur de stroke demandée
            df_stroke = df[df["stroke"] == int(stroke)]

            # Si seul stroke est fourni -> moyenne (taux d'AVC) sur le (sous-)ensemble
            if gender is None and smoking_status is None:
                stroke_rate = round(float(df["stroke"].mean()) * 100, 2)
                return {
                    "mode": "stroke_only",
                    "stroke_value": int(stroke),
                    "stroke_rate_percent": stroke_rate,
                    "total_patients_considered": int(len(df))
                }

            # stroke + gender (regarder la répartition par genre pour ce stroke)
            if gender is not None and smoking_status is None:
                # counts par gender pour le stroke demandé
                by_gender = (
                    df_stroke.groupby("gender")
                             .size()
                             .reset_index(name="count")
                             .to_dict(orient="records")
                )
                for r in by_gender:
                    r["count"] = int(r["count"])

                # stats détaillées pour le genre demandé (filtres sur ce genre)
                df_gender = df[df["gender"].str.lower() == gender.lower()]
                total_gender = int(len(df_gender))
                gender_stroke_rate = (
                    round(float(df_gender["stroke"].mean()) * 100, 2)
                    if total_gender > 0 else None
                )
                avg_age_gender = round(float(df_gender["age"].mean()), 2) if total_gender > 0 else None

                return {
                    "mode": "stroke_and_gender",
                    "stroke_value": int(stroke),
                    "counts_by_gender_for_this_stroke": by_gender,
                    "requested_gender": gender,
                    "requested_gender_total": total_gender,
                    "requested_gender_stroke_rate_percent": gender_stroke_rate,
                    "requested_gender_average_age": avg_age_gender
                }

            # stroke + smoking_status (counts par smoking_status)
            if smoking_status is not None and gender is None:
                by_smoke = (
                    df_stroke.groupby("smoking_status")
                             .size()
                             .reset_index(name="count")
                             .to_dict(orient="records")
                )
                for r in by_smoke:
                    r["count"] = int(r["count"])
                return {
                    "mode": "stroke_and_smoking_status",
                    "stroke_value": int(stroke),
                    "counts_by_smoking_status": by_smoke
                }

            # stroke + both gender AND smoking_status -> group by (gender, smoking_status)
            if gender is not None and smoking_status is not None:
                by_both = (
                    df_stroke.groupby(["gender", "smoking_status"])
                             .size()
                             .reset_index(name="count")
                             .to_dict(orient="records")
                )
                for r in by_both:
                    r["count"] = int(r["count"])
                return {
                    "mode": "stroke_gender_smoking",
                    "stroke_value": int(stroke),
                    "counts_by_gender_and_smoking_status": by_both
                }

        # --- Cas où stroke n'est PAS fourni : stats filtrées ou globales ---
        # gender seul -> stats pour ce genre
        if gender is not None and stroke is None and smoking_status is None:
            df_gender = df[df["gender"].str.lower() == gender.lower()]
            total = int(len(df_gender))
            return {
                "mode": "gender_only",
                "gender": gender,
                "total": total,
                "average_age": round(float(df_gender["age"].mean()), 2) if total>0 else None,
                "stroke_rate_percent": round(float(df_gender["stroke"].mean()) * 100, 2) if total>0 else None,
                "smoking_status_counts": df_gender["smoking_status"].value_counts().to_dict()
            }

        # smoking_status seul -> stats pour ce groupe
        if smoking_status is not None and stroke is None and gender is None:
            df_smoke = df[df["smoking_status"].str.lower() == smoking_status.lower()]
            total = int(len(df_smoke))
            return {
                "mode": "smoking_only",
                "smoking_status": smoking_status,
                "total": total,
                "average_age": round(float(df_smoke["age"].mean()), 2) if total>0 else None,
                "stroke_rate_percent": round(float(df_smoke["stroke"].mean()) * 100, 2) if total>0 else None
            }

        # Aucune option précise -> stats globales
        total_patients = int(len(df))
        if total_patients == 0:
            return {"message": "Aucun patient trouvé avec ces critères."}

        avg_age = round(float(df["age"].mean()), 2)
        stroke_rate = round(float(df["stroke"].mean()) * 100, 2)
        gender_distribution = {k: int(v) for k, v in df["gender"].value_counts().to_dict().items()}
        gender_stroke = (
            df.groupby(["gender", "stroke"])
              .size()
              .reset_index(name="count")
              .to_dict(orient="records")
        )
        for r in gender_stroke: r["count"] = int(r["count"])
        smoking_stroke = (
            df.groupby(["smoking_status", "stroke"])
              .size()
              .reset_index(name="count")
              .to_dict(orient="records")
        )
        for r in smoking_stroke: r["count"] = int(r["count"])

        women_with_stroke = int(df[(df["gender"].str.lower() == "female") & (df["stroke"] == 1)].shape[0])

        return {
            "mode": "global",
            "total_patients": total_patients,
            "average_age": avg_age,
            "stroke_rate_percent": stroke_rate,
            "gender_distribution": gender_distribution,
            "gender_stroke": gender_stroke,
            "smoking_stroke": smoking_stroke,
            "women_with_stroke": women_with_stroke
        }

    except Exception as e:
        # log + convertir en erreur FastAPI (si tu appelles depuis une route)
        print(f"Erreur dans stat_patients(): {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors du calcul des statistiques")
