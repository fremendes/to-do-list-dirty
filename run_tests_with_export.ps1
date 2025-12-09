#!/usr/bin/env pwsh
# Script pour exécuter les tests et générer un rapport

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Running Django tests..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Exécuter les tests avec le runner JSON
python -m pipenv run python manage.py test tasks.tests --testrunner=tests.json_test_runner.JSONTestRunner
$testExitCode = $LASTEXITCODE

# Vérifier si les tests ont réussi
if ($testExitCode -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "Generating test report..." -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green

    # Générer le rapport
    python -m pipenv run python test_report.py
} else {
    Write-Host ""
    Write-Host "Tests failed. Generating report anyway..." -ForegroundColor Yellow
    Write-Host ""
    python -m pipenv run python test_report.py
    exit 1
}

exit 0