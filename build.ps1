#!/usr/bin/env pwsh
# Script de build automatique pour Todo-list - Version Windows
# Usage: .\build.ps1 -version 1.0.1

param(
    [Parameter(Mandatory=$true)]
    [string]$version
)

# Vérification que Git est disponible
try {
    git --version > $null 2>&1
} catch {
    Write-Error "Git n'est pas installe ou n'est pas dans le PATH"
    exit 1
}

Write-Host "Construction de la version $version..." -ForegroundColor Green

# Mise à jour de la version dans settings.py
Write-Host "Mise à jour de la version dans settings.py..." -ForegroundColor Yellow
$settingsFile = "todo\settings.py"

if (Test-Path $settingsFile) {
    $content = Get-Content $settingsFile -Raw
    $newContent = $content -replace 'VERSION\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"', "VERSION = `"$version`""
    Set-Content $settingsFile $newContent
} else {
    Write-Error "Fichier settings.py introuvable"
    exit 1
}

# Ajout des fichiers modifiés
Write-Host "Ajout des fichiers modifies..." -ForegroundColor Yellow
git add todo/settings.py

# Commit des changements
Write-Host "Commit des changements..." -ForegroundColor Yellow
git commit -m "chore: bump version to $version"

# Création du tag
Write-Host "Creation du tag v$version..." -ForegroundColor Yellow
git tag "v$version"

# Génération de l'archive
$archiveName = "todo-$version.zip"
Write-Host "Generation de l'archive $archiveName..." -ForegroundColor Yellow
git archive --format zip --output $archiveName HEAD

Write-Host "Version $version construite avec succes!" -ForegroundColor Green
Write-Host "Archive: $archiveName" -ForegroundColor Cyan