Stroke data project
===================

Ce projet contient les fichiers nécessaires au brief Stroke data - Développement d'une API REST et visualisation.


Prétraitement des données
Le prétraitement des données a pour but de nettoyer, transformer et structurer les données brutes afin de les rendre exploitables pour l’analyse ou le machine learning. Voici les étapes réalisées dans ce projet :

1. Chargement des données
Import des données brutes depuis le fichier stroke_api/data/healthcare-dataset-stroke-data.csv à l'aide de pandas.read_csv().

2. Exploration initiale, nettoyage des données :
Vérification de la structure du jeu de données : colonnes, types, valeurs manquantes, statistiques de base:

On observe :

    Pour le BMI , il y'a 201 valeurs manquantes  ( indice de masse corporelle), peu de valeurs manquantes (3.9%):
    On comparant les deux méthodes, le resultat est pratiquement identique :
    On peut utiliser la médiane lorsqu'il ya des outliers (valeurs extrêmes) et lorsqu'on veut éviter que les extrêmes influencent la valeur de remplacement :
    Moyenne ≈ Médiane ⇒ distribution plutôt symétrique
    Max = 97.6, mais ce n’est pas une valeur aberrante pour un BMI (possible chez certains patients)
    Écart-type raisonnable (7.85), pas excessif.
    
    Nous avon opté pour le remplacement des valeurs par la moyenne vu le manque de valeurs extrêmes.

- Dans la colonne age il y'a des valeurs allant de 0.08 à 85, ce qui peut poser des problèmes si l'on veux analyser ou modéliser les données (ex: prédiction d’AVC):
    - On va garder toutes les données mais mieux les catégoriser en regroupant les âges en tranches.
    - Remplacement des valeurs de la colonne 'smoking_status' pour les Nourrisson passant de 'Unknown' en 'Never smoked' 

- Visualisation des emplois par tranche d'age : n'ayant pas dinformatios sur les nationalités des personnes et les lois en vigueur de chaque pays, je n'ai apporté aucune modification sur les possibles abérrations des emplois occupés.

- Visualisation des valeurs aberrantes au niveau des personnes mariées par tranche d'age : aucune modification apportés, cela me semble correct.

- Visualisation des valeurs aberrantes sur le niveau moyen de glucose (avg_glucose_level) par tranches d'âges: les données récoltées pour les valeurs max et min semblent plausibles:

Source :  
    Valeurs normales de la glycémie (glucose sanguin)
    American Diabetes Association (ADA) — Standards of Medical Care in Diabetes — 2023
    https://diabetesjournals.org/care/article/46/Supplement_1/S1/138924/Standards-of-Medical-Care-in-Diabetes-2023
    Contient les seuils de glycémie à jeun, post-prandiale, et diagnostic du diabète.

    Mayo Clinic — Blood sugar levels: What’s normal?
    https://www.mayoclinic.org/diseases-conditions/diabetes/in-depth/blood-sugar/art-20046628
    Explications simples des taux de glucose normaux, hypoglycémie et hyperglycémie.

    2. Glucose sanguin selon l’âge
    National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)
    https://www.niddk.nih.gov/health-information/diagnostic-tests/glucose-tolerance-test
    Le glucose varie peu avec l’âge, mais certains facteurs liés au vieillissement peuvent influencer le métabolisme.

    Article scientifique — Influence of age on glucose metabolism and insulin resistance
    Kalyani et al., Journal of Clinical Endocrinology & Metabolism, 2017
    https://academic.oup.com/jcem/article/102/7/2245/3843485
    Analyse de l’impact du vieillissement sur la régulation du glucose.

    3. Interprétation des valeurs extrêmes en contexte clinique (AVC, diabète, etc.)
    Stroke Association — Glycemia and Stroke Outcome
    https://www.stroke.org.uk/effect-of-diabetes-on-stroke
    Lien entre hyperglycémie, diabète et risques d’AVC.

    Clinical guidelines for management of glucose levels in acute stroke patients
    Hacke et al., Stroke, 2016
    https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.115.010164
    Recommandations pour le contrôle glycémique en phase aiguë d’AVC.

3. Chercher des infos sur le format de fichier parquet et indiquer les sources consultées : 
    Le format Apache Parquet est un format de fichier open-source orienté colonne, conçu pour le traitement efficace de données volumineuses et complexes. Il est largement utilisé dans les systèmes de traitement de données distribués tels qu'Apache Hadoop, Apache Spark et Apache Drill .

- Différence principale avec le format csv ?
    - Parquet est optimisé pour le traitement rapide et compact des grandes quantités de données, grâce à son stockage en colonnes et  
      sa compression.
    - CSV est simple, universel, lisible et facile à utiliser, mais peu adapté aux très gros volumes et traitements analytiques lourds.

- Dans quels cas l'utiliser ? 
    - Le format Parquet est particulièrement adapté dans les situations suivantes :
    - Traitement de grandes quantités de données : Parquet est conçu pour gérer efficacement de vastes ensembles de données, ce qui  
      le rend idéal pour les environnements de big data.
    - Requêtes analytiques complexes : Grâce à son stockage orienté colonne, Parquet permet une lecture rapide des colonnes  
      spécifiques nécessaires aux analyses, réduisant ainsi le temps de traitement.
    - Intégration avec des systèmes distribués : Parquet s'intègre bien avec des frameworks tels qu'Apache Spark, Apache Hive et 
      Apache Drill, facilitant le traitement parallèle des données.
    - Stockage dans des lacs de données (Data Lakes) : Parquet est couramment utilisé pour stocker des données dans des lacs de 
      données, permettant une gestion efficace et évolutive des données brutes .

- Pourquoi c'est un format adapté aux gros volumes de données ?

   - Compression efficace : Parquet utilise des techniques de compression au niveau des colonnes, ce qui permet de réduire 
     considérablement la taille des fichiers et d'optimiser l'utilisation de l'espace de stockage .
   - Lecture rapide : Grâce à son stockage orienté colonne, Parquet permet de lire rapidement les données pertinentes sans avoir à 
     charger l'ensemble du fichier, ce qui améliore les performances des requêtes.
   - Traitement parallèle : Parquet est conçu pour être utilisé dans des environnements distribués, permettant le traitement parallèle 
     des données et réduisant ainsi le temps de traitement global.

Sources consultées:
   - Last9 - Parquet vs CSV: Which Format Should You Choose?
   - Upsolver - What is the Parquet File Format? Use Cases & Benefits
   - Databricks - Apache Parquet: Efficient Data Storage
   - Apache Parquet Wikipedia

  -------------------------------------------------------------------------------------------------------------------------------------

                                            API Stroke Prediction

Cette API permet d’accéder à des données relatives à des patients pour la prédiction d’AVC (Accident Vasculaire Cérébral). Elle propose plusieurs routes pour récupérer des données filtrées, des détails par patient, et des statistiques agrégées.

Fonctionnalités principales :
- Filtrage des patients par âge maximal, genre, et présence d’AVC via la route /patients/.

- Recherche d’un patient par son identifiant unique avec la route /patients/{patient_id}.

- Statistiques globales sur les patients (nombre total, âge moyen, taux d’AVC, répartition par genre, etc.) via /patients/stats/.

- Statistiques filtrées selon des critères personnalisés (âge, genre, AVC, statut tabagique) via /patients/stats/detail.

Structure et fonctionnement :
- Les données sont chargées une seule fois au démarrage dans une variable globale et copiées pour les traitements dans chaque fonction.

- Le filtrage et le calcul des statistiques sont réalisés dans un module filters.py.

- Les routes FastAPI sont définies dans api.py et appellent les fonctions de filtrage/statistiques du module filters.py.

- Les erreurs (par exemple, patient non trouvé ou erreurs internes) sont correctement gérées avec des exceptions HTTP appropriées (404, 500).

Utilisation :
Lancer le serveur FastAPI avec la commande :
poetry run fastapi dev stroke_api/main.py

Accéder à la documentation interactive Swagger UI à l’adresse :
http://127.0.0.1:8000/docs

Tester les différentes routes via l’interface “Try it out”.