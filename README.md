# Consolidateur de Données Google Search Console

## Description

Cette application Streamlit permet de consolider et d'analyser les données exportées de Google Search Console (GSC) de manière simple et intuitive.

## Fonctionnalités principales

- 🔍 Consolidation des données GSC par page
- 📊 Filtrage des mots-clés par nombre minimum de clics
- 📥 Export en CSV ou Excel
- 🔢 Statistiques détaillées sur les pages, mots-clés et clics

## Prérequis

- Python 3.7+
- Bibliothèques requises :
  - streamlit
  - pandas
  - openpyxl

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-utilisateur/gsc-consolidateur.git
cd gsc-consolidateur
```

2. Créez un environnement virtuel (optionnel mais recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Lancement de l'application

```bash
streamlit run gsc_consolidateur.py
```

### Préparation des fichiers d'entrée

1. **Fichier source** : Exportez vos données depuis Google Search Console
   - Formats supportés : CSV, Excel (.xlsx, .xls)
   - Colonnes recommandées : Page, Mot-clé, Clics, Impressions

### Fonctionnalités de l'application

- **Filtrage des mots-clés** : 
  - Définissez un seuil minimum de clics
  - Conservez uniquement les mots-clés pertinents

- **Formats de sortie** :
  - CSV
  - Excel (avec mise en forme optimisée)

## Structure du fichier de sortie

Le fichier généré contient 7 colonnes :

1. **Page** : URL de la page
2. **Mots clés** : Mots-clés filtrés
3. **Total Mots clés** : Nombre total de mots-clés avant filtrage
4. **Clics** : Clics par mot-clé
5. **Totaux Clics** : Somme totale des clics
6. **Impressions** : Impressions par mot-clé
7. **Totaux Impressions** : Somme totale des impressions

## Exemple de workflow

1. Exportez vos données depuis Google Search Console
2. Chargez le fichier dans l'application
3. Définissez un seuil de clics minimum (optionnel)
4. Choisissez le format de sortie (CSV ou Excel)
5. Téléchargez le fichier consolidé

## Conseils

- Les mots-clés sont triés par nombre de clics décroissant
- Dans le fichier Excel, double-cliquez sur une cellule pour voir tous les mots-clés
- Le nombre total de mots-clés est toujours conservé, même après filtrage

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue.

## Licence

[Spécifiez votre licence ici]

## Support

En cas de problème ou de question, veuillez ouvrir une issue sur le dépôt GitHub.

## Avertissement

Cette application n'est pas officiellement liée à Google Search Console. Elle est conçue comme un outil d'analyse complémentaire.
