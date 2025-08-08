from fastapi import APIRouter, HTTPException, Query
from stroke_api import filters
from typing import Optional

router = APIRouter()

try : 
    @router.get("/")
    def read_root():
        return {"message": "Bienvenue sur l'API Stroke Prediction !"}
except Exception as e:
    print(e)


@router.get("/patients/")
def get_patients(
    gender: Optional[str] = Query(None, description="male | female | other"),
    stroke: Optional[int] = Query(None, ge=0, le=1, description="0 = pas d'AVC, 1 = AVC"),
    max_age: Optional[float] = Query(None, gt=0, description="Âge maximal des patients")
):
    """
    Récupère la liste des patients filtrés selon des critères optionnels.

    Paramètres (optionnels):
    - gender: sexe du patient ("male", "female", "other")
    - stroke: 0 pour patients sans AVC, 1 pour patients ayant eu un AVC
    - max_age: âge maximal des patients à inclure

    Retour:
    - Liste des patients correspondant aux critères sous forme de dictionnaires.
    """
    filtered_df = filters.filter_patient(gender=gender, stroke=stroke, max_age=max_age)
    return filtered_df

# Route pour récupérer un patient par son ID
@router.get("/patients/{patient_id}")
def get_patients_by_id(patient_id: int):
    """
    Endpoint : /patients/{patient_id}

    Description
    -----------
    Récupère les informations d'un patient à partir de son identifiant unique.

    Paramètres
    ----------
    patient_id : int
        L'identifiant unique du patient à rechercher.

    Retour
    ------
    list[dict]
        Une liste contenant un dictionnaire avec les données du patient trouvé.
        Si aucun patient n'est trouvé, lève une erreur 404.

    Exceptions
    ----------
    HTTPException 404 : Si aucun patient ne correspond à l'ID fourni.
    HTTPException 500 : Si une erreur interne survient lors de la recherche.
    """
    try:
        # Appel au filtre pour récupérer les données du patient
        patient_data = filters.filter_patient_id(id=patient_id)

        # Si aucun patient trouvé, renvoyer une erreur 404
        if not patient_data:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun patient trouvé avec l'ID numéro : {patient_id}"
            )

        return patient_data

    except HTTPException:
        # On relance directement si c'est déjà une HTTPException
        raise

    except Exception as e:
        # Gestion d'une erreur interne
        print(f"Erreur dans get_patients_by_id(): {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération du patient"
        )


# Ajout de la route /patients/stats/ pour calculer et retourner des statistiques sur les patients
@router.get("/patients/stats/")
def stats():
    """
    Endpoint : /patients/stats/

    Description
    -----------
    Cette route calcule et retourne des statistiques globales sur les patients
    du jeu de données. Les statistiques sont générées par la fonction
    `stat_patients()` du module filters.py.

    Détails de fonctionnement
    -------------------------
    - Copie les données originales dans un DataFrame
    - Calcule différents indicateurs comme :
        * Nombre total de patients
        * Âge moyen
        * Pourcentage de patients ayant eu un AVC (stroke)
        * Répartition par genre
        * Répartition par genre + AVC
        * Répartition par statut de tabagisme + AVC
    - Retourne ces statistiques sous forme de dictionnaire JSON

    Exceptions
    ----------
    - En cas d'erreur lors du calcul (ex : problème dans les données ou fonction),
      l'API retourne un code HTTP 500 avec un message d'erreur.
    """

    try:
        # Appel à la fonction qui calcule les statistiques dans filters.py
        stat_df = filters.stat_patients()

        # Retour direct des statistiques au format dictionnaire
        return stat_df

    except Exception as e:
        # Affiche l'erreur côté serveur (console) pour debug
        print(f"Erreur dans stats(): {e}")

        # Retourne une erreur 500 à l'utilisateur si le calcul échoue
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors du calcul des statistiques"
        )


@router.get("/patients/stats/detail")
def stats(
    max_age: Optional[float] = Query(None, description="Âge maximal"),
    gender: Optional[str] = Query(None, description="Genre (male/female)"),
    stroke: Optional[int] = Query(None, description="1 pour AVC, 0 sinon"),
    smoking_status: Optional[str] = Query(None, description="Statut de tabagisme : Never smoked | formerly smoked | never smoked | smokes | Unknown")   

):
    """
    Retourne des statistiques filtrées selon les critères choisis.
    - max_age : âge maximum des patients à considérer
    - gender : 'male' ou 'female'
    - stroke : 1 ou 0
    - smoking_status : ex. 'formerly smoked', 'never smoked'
    """

    try:
        stat_df = filters.complex_stat_patients(
            max_age=max_age,
            gender=gender,
            stroke=stroke,
            smoking_status=smoking_status
        )
        return stat_df
    except Exception as e:
        print(f"Erreur dans stats(): {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors du calcul des statistiques")
