import streamlit as st
import pandas as pd
import io
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment
import time

st.set_page_config(page_title="Consolidation GSC", page_icon="📊", layout="wide")

st.title("Consolidation des données Google Search Console")
st.markdown("""
Cette application consolide les données exportées de Google Search Console avec le format exact demandé.
""")

def consolidate_gsc_data(df, min_clicks=0, progress_bar=None):
    """
    Consolide les données GSC avec exactement 7 colonnes et les mots-clés en colonne dans chaque cellule.
    Filtre les mots-clés en fonction d'un seuil minimum de clics.
    
    Args:
        df (pd.DataFrame): DataFrame contenant les données GSC
        min_clicks (int): Nombre minimum de clics pour inclure un mot-clé
        progress_bar (st.progress): Barre de progression Streamlit
    
    Returns:
        pd.DataFrame: DataFrame consolidé
    """
    # Normaliser les noms de colonnes
    df.columns = df.columns.str.lower().str.strip()
    
    if progress_bar:
        progress_bar.progress(0.1, text="Identification des colonnes...")
    
    # Identifier les colonnes basées sur les motifs possibles
    page_col = next((col for col in df.columns if 'page' in col or 'url' in col), None)
    query_col = next((col for col in df.columns if 'query' in col or 'mot' in col or 'clé' in col or 'recherche' in col), None)
    clicks_col = next((col for col in df.columns if 'click' in col or 'clic' in col or 'visite' in col), None)
    impressions_col = next((col for col in df.columns if 'impress' in col or 'affichage' in col), None)
    
    if not all([page_col, query_col, clicks_col, impressions_col]):
        # S'il manque des colonnes, utiliser les indices positionnels
        cols = list(df.columns)
        if len(cols) >= 4:
            page_col = cols[0]
            query_col = cols[1]
            clicks_col = cols[2]
            impressions_col = cols[3]
        else:
            st.error("Impossible d'identifier les colonnes requises dans le fichier!")
            st.stop()
    
    # Convertir les colonnes numériques
    for col in [clicks_col, impressions_col]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if progress_bar:
        progress_bar.progress(0.2, text="Collecte et organisation des données...")
    
    # Dictionnaire pour stocker les données par page
    page_data = {}
    
    # Parcourir le DataFrame pour collecter les données
    total_rows = len(df)
    for i, (_, row) in enumerate(df.iterrows()):
        page = row[page_col]
        keyword = row[query_col]
        clicks = row[clicks_col]
        impressions = row[impressions_col]
        
        if page not in page_data:
            page_data[page] = {
                'keywords': [],
                'clicks_by_keyword': {},
                'impressions_by_keyword': {},
                'total_clicks': 0,
                'total_impressions': 0
            }
        
        # Ajouter le mot-clé s'il n'existe pas déjà
        if keyword not in page_data[page]['keywords']:
            page_data[page]['keywords'].append(keyword)
            page_data[page]['clicks_by_keyword'][keyword] = 0
            page_data[page]['impressions_by_keyword'][keyword] = 0
        
        # Mettre à jour les compteurs
        page_data[page]['clicks_by_keyword'][keyword] += clicks
        page_data[page]['impressions_by_keyword'][keyword] += impressions
        page_data[page]['total_clicks'] += clicks
        page_data[page]['total_impressions'] += impressions
        
        # Mise à jour de la barre de progression pendant la collecte des données
        if progress_bar and i % max(1, total_rows // 100) == 0:
            progress_value = 0.2 + (0.4 * i / total_rows)
            progress_bar.progress(progress_value, text=f"Traitement des données... ({i}/{total_rows})")
    
    if progress_bar:
        progress_bar.progress(0.6, text="Filtrage et tri des mots-clés...")
    
    # Créer le DataFrame résultat avec exactement 7 colonnes
    result_data = []
    
    total_pages = len(page_data)
    for i, (page, data) in enumerate(page_data.items()):
        # Filtrer les mots-clés selon le nombre minimum de clics
        filtered_keywords = [k for k in data['keywords'] 
                            if data['clicks_by_keyword'].get(k, 0) >= min_clicks]
        
        # Compter le nombre total de mots-clés avant filtrage (pour statistiques)
        total_keywords_count = len(data['keywords'])
        
        # Si aucun mot-clé ne passe le filtre, passer à la page suivante
        if not filtered_keywords:
            result_data.append({
                'Page': page,
                'Mots clés': "",
                'Total Mots clés': total_keywords_count,
                'Clics': "",
                'Totaux Clics': data['total_clicks'],
                'Impressions': "",
                'Totaux Impressions': data['total_impressions']
            })
        else:
            # Trier les mots-clés par nombre de clics (décroissant)
            sorted_keywords = sorted(filtered_keywords, 
                                    key=lambda k: data['clicks_by_keyword'].get(k, 0), 
                                    reverse=True)
            
            # Préparation des textes pour les cellules (avec sauts de ligne forcés)
            keywords_text = "\n".join(sorted_keywords)
            clicks_text = "\n".join([str(data['clicks_by_keyword'].get(k, 0)) for k in sorted_keywords])
            impressions_text = "\n".join([str(data['impressions_by_keyword'].get(k, 0)) for k in sorted_keywords])
            
            # Ajouter une ligne au résultat
            result_data.append({
                'Page': page,
                'Mots clés': keywords_text,
                'Total Mots clés': total_keywords_count,
                'Clics': clicks_text,
                'Totaux Clics': data['total_clicks'],
                'Impressions': impressions_text,
                'Totaux Impressions': data['total_impressions']
            })
        
        # Mise à jour de la barre de progression pendant la création du résultat
        if progress_bar:
            progress_value = 0.6 + (0.3 * i / total_pages)
            progress_bar.progress(progress_value, text=f"Préparation du résultat... ({i+1}/{total_pages} pages)")
    
    if progress_bar:
        progress_bar.progress(0.9, text="Finalisation du traitement...")
    
    # Créer le DataFrame final
    result_df = pd.DataFrame(result_data)
    
    if progress_bar:
        progress_bar.progress(1.0, text="Traitement terminé!")
        time.sleep(0.5)  # Pause pour montrer que le traitement est terminé
    
    return result_df

# Interface utilisateur
uploaded_file = st.file_uploader("Choisissez un fichier CSV ou Excel", type=['csv', 'xlsx', 'xls'])

col1, col2 = st.columns(2)
with col1:
    min_clicks = st.number_input("Seuil minimum de clics pour inclure un mot-clé", 
                                min_value=0, value=0, step=1,
                                help="Seuls les mots-clés ayant au moins ce nombre de clics seront inclus dans le fichier. 0 = tous les mots-clés.")

with col2:
    output_format = st.selectbox("Format du fichier de sortie", ["CSV", "Excel"], index=1)

if uploaded_file is not None:
    st.info("Fichier chargé avec succès, prêt pour le traitement.")
    
    if st.button("Lancer la consolidation"):
        # Création de la barre de progression
        progress_bar = st.progress(0, text="Initialisation...")
        
        # Déterminer le type de fichier et le charger
        file_ext = Path(uploaded_file.name).suffix.lower()
        
        try:
            progress_bar.progress(0.05, text="Chargement du fichier...")
            
            if file_ext == '.csv':
                # Essayer d'abord avec séparateur virgule
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    # Si échec, essayer avec séparateur point-virgule
                    uploaded_file.seek(0)  # Remettre le curseur au début du fichier
                    df = pd.read_csv(uploaded_file, encoding='utf-8', sep=';')
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Format de fichier non supporté. Utilisez CSV ou Excel.")
                st.stop()
            
            # Afficher un aperçu des données d'entrée
            st.subheader("Aperçu des données d'entrée")
            st.dataframe(df.head())
            
            # Consolider les données avec le filtre de clics minimum
            consolidated_df = consolidate_gsc_data(df, min_clicks, progress_bar)
            
            # Créer une version pour l'affichage dans Streamlit 
            # (maximum 5 mots-clés affichés dans l'aperçu pour la lisibilité)
            display_df = consolidated_df.copy()
            for i, row in display_df.iterrows():
                for col in ['Mots clés', 'Clics', 'Impressions']:
                    parts = row[col].split('\n') if row[col] else []
                    if len(parts) > 5:  # Limiter à 5 pour l'affichage
                        display_df.at[i, col] = '\n'.join(parts[:5]) + '\n...'
            
            # Afficher l'aperçu des données consolidées
            st.subheader("Aperçu des données consolidées")
            st.dataframe(display_df)
            
            # Compter les mots-clés avant et après filtrage
            keywords_before = consolidated_df['Total Mots clés'].sum()
            keywords_after = sum([len(row['Mots clés'].split('\n')) if row['Mots clés'] else 0 
                                for _, row in consolidated_df.iterrows()])
            
            # Informations sur le filtrage
            if min_clicks > 0:
                st.success(f"Filtrage : {keywords_after} mots-clés conservés sur {keywords_before} au total (seuil : {min_clicks} clics minimum)")
            
            # Préparer le téléchargement des données consolidées
            if output_format == "CSV":
                output_buffer = io.StringIO()
                consolidated_df.to_csv(output_buffer, index=False, encoding='utf-8')
                output_data = output_buffer.getvalue()
                download_filename = f"{Path(uploaded_file.name).stem}_consolide.csv"
                st.download_button(
                    label="Télécharger les données consolidées (CSV)",
                    data=output_data,
                    file_name=download_filename,
                    mime="text/csv"
                )
            else:  # Excel
                progress_bar.progress(0.95, text="Préparation du fichier Excel...")
                
                output_buffer = io.BytesIO()
                
                # Utiliser openpyxl pour un meilleur contrôle du formatage
                with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                    consolidated_df.to_excel(writer, index=False, sheet_name='Données consolidées')
                    
                    # Accéder à la feuille de calcul
                    worksheet = writer.sheets['Données consolidées']
                    
                    # Configurer l'alignement du texte pour les cellules contenant des sauts de ligne
                    wrap_alignment = Alignment(wrap_text=True, vertical='top')
                    
                    # Formater toutes les cellules pour permettre les sauts de ligne
                    for row in worksheet.iter_rows(min_row=2):  # Ignorer l'en-tête
                        for cell in row:
                            if isinstance(cell.value, str) and '\n' in cell.value:
                                cell.alignment = wrap_alignment
                    
                    # Ajuster la hauteur des lignes pour montrer seulement ~3 mots-clés par défaut
                    for i, row in enumerate(worksheet.iter_rows(min_row=2)):
                        # Définir une hauteur fixe pour montrer environ 3 lignes
                        worksheet.row_dimensions[i+2].height = 60  # Hauteur pour ~3 lignes
                    
                    # Ajuster la largeur des colonnes
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        
                        for cell in column:
                            if cell.value:
                                # Pour les cellules avec sauts de ligne, ne considérer que la première ligne
                                first_line = str(cell.value).split('\n')[0] if '\n' in str(cell.value) else str(cell.value)
                                cell_length = len(first_line)
                                max_length = max(max_length, cell_length)
                        
                        adjusted_width = max(max_length + 2, 10)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                progress_bar.progress(1.0, text="Fichier Excel prêt à télécharger!")
                
                output_data = output_buffer.getvalue()
                download_filename = f"{Path(uploaded_file.name).stem}_consolide{'' if min_clicks == 0 else f'_min{min_clicks}clics'}.xlsx"
                st.download_button(
                    label="Télécharger les données consolidées (Excel)",
                    data=output_data,
                    file_name=download_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Afficher des statistiques
            st.subheader("Statistiques")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pages uniques", len(consolidated_df))
            with col2:
                st.metric("Total des mots-clés", keywords_before)
            with col3:
                st.metric("Total des clics", int(consolidated_df['Totaux Clics'].sum()))
                
        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier: {str(e)}")
            st.exception(e)
else:
    st.info("Veuillez charger un fichier pour commencer.")

# Afficher des instructions
st.markdown("---")
st.markdown("""
### Format du fichier de sortie
Le fichier généré contiendra exactement 7 colonnes:
1. **Page**: L'URL de la page
2. **Mots clés**: Les mots-clés filtrés affichés en colonne dans la cellule (triés par nombre de clics)
3. **Total Mots clés**: Nombre total de mots-clés pour cette page (avant filtrage)
4. **Clics**: Les clics pour chaque mot-clé filtré, affichés en colonne dans la cellule
5. **Totaux Clics**: Somme de tous les clics pour cette page (incluant ceux des mots-clés filtrés et non filtrés)
6. **Impressions**: Les impressions pour chaque mot-clé filtré, affichées en colonne dans la cellule
7. **Totaux Impressions**: Somme de toutes les impressions pour cette page

### Filtrage des mots-clés
- Si le seuil minimum de clics est défini à 0, tous les mots-clés sont inclus
- Si le seuil est défini à 1 ou plus, seuls les mots-clés ayant au moins ce nombre de clics seront inclus
- Le nombre total de mots-clés (colonne "Total Mots clés") affiche toujours le nombre total avant filtrage
- Les "Totaux Clics" et "Totaux Impressions" incluent toujours les valeurs de tous les mots-clés, même ceux qui ne sont pas affichés

### Note Excel
- Le fichier Excel est configuré pour n'afficher qu'environ 3 lignes de mots-clés par défaut
- Pour voir tous les mots-clés d'une cellule, double-cliquez dessus
""")
