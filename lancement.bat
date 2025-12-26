@echo off
chcp 65001 > nul
title 📊 Application Statistique Desktop
color 0A

echo ========================================================
echo    📈 APPLICATION D'ANALYSE STATISTIQUE - DESKTOP
echo ========================================================
echo.

:: Vérifier Python
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ ERREUR : Python n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer Python 3.8+ depuis :
    echo https://www.python.org/downloads/
    echo.
    echo Assurez-vous de cocher "Add Python to PATH" durant l'installation
    pause
    exit /b 1
)

:: Vérifier la version de Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%I"
echo ✅ Python %PYTHON_VERSION% détecté

:: Vérifier pip
where pip >nul 2>nul
if errorlevel 1 (
    echo ⚠️  Pip n'est pas disponible
    echo Installation de pip...
    python -m ensurepip --upgrade
)

:: Vérifier et installer les dépendances
echo.
echo 📦 Vérification des dépendances...
pip install --quiet --upgrade pip 2>nul

:: Installer les packages manquants
for %%P in (
    streamlit
    pandas
    numpy
    matplotlib
    statsmodels
    scipy
    scikit-learn
    pywebview
) do (
    pip show %%P >nul 2>nul
    if errorlevel 1 (
        echo Installation de %%P...
        pip install --quiet %%P
    ) else (
        echo ✅ %%P déjà installé
    )
)

:: Vérifier les fichiers nécessaires
echo.
echo 🔍 Vérification des fichiers...
if not exist "app.py" (
    echo ❌ ERREUR : app.py non trouvé !
    echo Placez ce fichier dans le même dossier que lancement.bat
    pause
    exit /b 1
)

if not exist "desktop_launcher.py" (
    echo ❌ ERREUR : desktop_launcher.py non trouvé !
    pause
    exit /b 1
)

:: Lancer l'application
echo.
echo 🚀 Lancement de l'application...
echo.

:: Exécuter le lanceur Python
python desktop_launcher.py

:: Gestion après fermeture
if errorlevel 1 (
    echo.
    echo ❌ L'application s'est arrêtée avec une erreur
    echo.
    echo Solutions possibles :
    echo 1. Vérifiez que tous les fichiers sont présents
    echo 2. Essayez manuellement : streamlit run app.py
    echo 3. Vérifiez les logs ci-dessus
    pause
    exit /b 1
)

echo.
echo ✅ Application fermée proprement
timeout /t 5