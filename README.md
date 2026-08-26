# 🧠 Stroke API - Prédiction d'AVC

Ce projet met à disposition les données du dataset Kaggle *Stroke Prediction Dataset* sous la forme d'une **API REST** robuste développée avec **FastAPI**. L'objectif est de permettre à d'autres équipes (médecins, data scientists, etc.) d'interroger et de filtrer facilement ces données médicales.

## 🎯 Objectif du projet

Le but est d'exposer des données patients (âge, genre, IMC, niveau de glucose, statut tabagique, antécédents médicaux, etc.) de manière standardisée. Les utilisateurs peuvent récupérer la liste des patients, filtrer selon divers critères (âge, antécédents d'AVC, genre), consulter le profil d'un patient unique ou encore obtenir des statistiques globales.

## 🏗️ Architecture du code

L'application est structurée de manière modulaire :
*   `stroke_api/main.py` : Point d'entrée de l'application FastAPI.
*   `stroke_api/api.py` : Définition des routes de l'API (les *endpoints*).
*   `stroke_api/filters.py` : Logique métier contenant le chargement du dataset et les fonctions de filtrage basées sur la bibliothèque **Pandas**.
*   `pyproject.toml` & `poetry.lock` : Fichiers de configuration pour la gestion des dépendances via **Poetry**.

---

## 🚀 Installation et Démarrage

### 1. Prérequis
*   **Python** (version 3.12 ou supérieure)
*   **Poetry** installé sur votre machine pour gérer les dépendances.

### 2. Installation des dépendances
Clonez le dépôt, placez-vous à la racine du projet, puis exécutez la commande suivante pour que Poetry installe toutes les bibliothèques (FastAPI, Pandas, Uvicorn, etc.) :

```bash
poetry install
