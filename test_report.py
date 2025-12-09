#!/usr/bin/env python3
"""
Script pour générer un rapport visuel des tests à partir du cahier de tests YAML
et des résultats des tests automatisés (JSON).

Usage:
    python3 test_report.py
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ Erreur: Le module PyYAML n'est pas installé.")
    print("   Installez-le avec: pip install pyyaml")
    sys.exit(1)


def load_test_list(yaml_path='test_list.yaml'):
    """
    Charge la liste des tests depuis le fichier YAML.

    Args:
        yaml_path: Chemin vers le fichier YAML

    Returns:
        Liste des tests
    """
    try:
        with open(yaml_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('tests', [])
    except FileNotFoundError:
        print(f"❌ Erreur: Fichier {yaml_path} introuvable.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Erreur lors de la lecture du YAML: {e}")
        sys.exit(1)


def load_test_results(json_path='result_test_auto.json'):
    """
    Charge les résultats des tests automatisés depuis le fichier JSON.

    Args:
        json_path: Chemin vers le fichier JSON

    Returns:
        Dictionnaire des résultats, ou None si le fichier n'existe pas
    """
    if not Path(json_path).exists():
        return None

    try:
        with open(json_path, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠️  Avertissement: Erreur lors de la lecture du JSON: {e}")
        return None


# def load_selenium_results(json_path='result_test_selenium.json'):
#     """
#     Charge les résultats des tests Selenium depuis le fichier JSON.

#     Args:
#         json_path: Chemin vers le fichier JSON

#     Returns:
#         Dictionnaire des résultats, ou None si le fichier n'existe pas
#     """
#     if not Path(json_path).exists():
#         return None

#     try:
#         with open(json_path, encoding='utf-8') as f:
#             return json.load(f)
#     except json.JSONDecodeError as e:
#         print(f"⚠️  Avertissement: Erreur lors de la lecture du JSON Selenium: {e}")
#         return None


def get_test_status(test, results_data, selenium_data=None):
    """
    Détermine le statut d'un test.

    Args:
        test: Dictionnaire du test depuis le YAML
        results_data: Données des résultats JSON (unittest)
        selenium_data: Données des résultats JSON Selenium

    Returns:
        Tuple (emoji, status_text, status_key)
    """
    test_id = str(test['id'])
    test_type = test['type']

    # Si le test est manuel
    if test_type == 'manual':
        return '🫱', 'Manual test needed', 'manual'

    # Si le test est Selenium
    if test_type == 'auto-selenium':
        # Si pas de résultats Selenium JSON
        if not selenium_data:
            return '🕳', 'Not found', 'not_found'

        # Chercher le test dans les résultats Selenium
        for result_test in selenium_data.get('tests', []):
            if result_test.get('test_id') == test_id:
                status = result_test.get('status')
                if status == 'passed':
                    return '✅', 'Passed', 'passed'
                elif status == 'failed':
                    return '❌', 'Failed', 'failed'
                elif status == 'error':
                    return '❌', 'Error', 'failed'

        # Test pas trouvé dans les résultats
        return '🕳', 'Not found', 'not_found'

    # Si le test est automatique
    if test_type == 'auto':
        # Si pas de résultats JSON
        if not results_data:
            return '🕳', 'Not found', 'not_found'

        # Chercher le test dans les résultats
        for result_test in results_data.get('tests', []):
            if result_test.get('test_id') == test_id:
                status = result_test.get('status')
                if status == 'passed':
                    return '✅', 'Passed', 'passed'
                elif status == 'failed':
                    return '❌', 'Failed', 'failed'
                elif status == 'error':
                    return '❌', 'Error', 'failed'
                elif status == 'skipped':
                    return '⏭️', 'Skipped', 'skipped'

        # Test pas trouvé dans les résultats
        return '🕳', 'Not found', 'not_found'

    # Type de test inconnu
    return '❓', 'Unknown', 'unknown'


def print_test_report(tests, results_data, selenium_data=None):
    """
    Affiche le rapport des tests.

    Args:
        tests: Liste des tests depuis le YAML
        results_data: Données des résultats JSON (unittest)
        selenium_data: Données des résultats JSON Selenium
    """
    print("\nLecture des tests auto via result_test_auto.json…")
    if results_data:
        print("OK")
    else:
        print("⚠️  Fichier non trouvé ou invalide - " \
        "tous les tests auto seront marqués 'Not found'")

    print("Lecture des tests Selenium via result_test_selenium.json…")
    if selenium_data:
        print("OK\n")
    else:
        print("⚠️  Fichier non trouvé ou invalide - " \
              "tous les tests Selenium seront marqués 'Not found'\n")

    # Statistiques
    stats = {
        'passed': 0,
        'failed': 0,
        'not_found': 0,
        'manual': 0,
        'e2e': 0,
        'skipped': 0,
        'unknown': 0
    }

    # Afficher chaque test
    for test in tests:
        emoji, status_text, status_key = get_test_status(
            test, results_data, selenium_data=None)
        test_id = test['id']
        test_type = test['type']

        print(f"{test_id} | {test_type:15} | {emoji} {status_text}")

        # Incrémenter les statistiques
        if status_key in stats:
            stats[status_key] += 1

    return stats


def print_statistics(stats, total_tests):
    """
    Affiche les statistiques en pourcentage.

    Args:
        stats: Dictionnaire des statistiques
        total_tests: Nombre total de tests
    """
    print(f"\nNumber of tests: {total_tests}")

    # Tests réussis
    passed_count = stats['passed']
    passed_pct = (passed_count / total_tests * 100) if total_tests > 0 else 0
    print(f"✅ Passed tests: {passed_count} ({passed_pct:.1f}%)")

    # Tests échoués
    failed_count = stats['failed']
    failed_pct = (failed_count / total_tests * 100) if total_tests > 0 else 0
    print(f"❌ Failed tests: {failed_count} ({failed_pct:.1f}%)")

    # Tests non trouvés
    not_found_count = stats['not_found']
    not_found_pct = (not_found_count / total_tests * 100) if total_tests > 0 else 0
    print(f"🕳  Not found tests: {not_found_count} ({not_found_pct:.1f}%)")

    # Tests manuels
    manual_count = stats['manual']
    manual_pct = (manual_count / total_tests * 100) if total_tests > 0 else 0
    print(f"🫱  Test to pass manually: {manual_count} ({manual_pct:.1f}%)")

    # Tests E2E
    e2e_count = stats['e2e']
    if e2e_count > 0:
        e2e_pct = (e2e_count / total_tests * 100) if total_tests > 0 else 0
        print(f"🌐  E2E tests (run separately): {e2e_count} ({e2e_pct:.1f}%)")

    # Tests sautés (optionnel)
    if stats['skipped'] > 0:
        skipped_count = stats['skipped']
        skipped_pct = (skipped_count / total_tests * 100) if total_tests > 0 else 0
        print(f"⏭️  Skipped tests: {skipped_count} ({skipped_pct:.1f}%)")

    # Total réussis + manuels + E2E
    success_count = passed_count + manual_count + e2e_count
    success_pct = (success_count / total_tests * 100) if total_tests > 0 else 0
    print(f"✅ Passed + 🫱 Manual + 🌐 E2E: {success_count} ({success_pct:.1f}%)")


def main():
    """Point d'entrée principal du script."""
    print("=" * 70)
    print("TEST REPORT - Rapport des tests")
    print("=" * 70)

    # Charger les tests depuis le YAML
    tests = load_test_list()
    if not tests:
        print("❌ Aucun test trouvé dans le fichier YAML.")
        sys.exit(1)

    # Charger les résultats des tests automatisés
    results_data = load_test_results()

    # Charger les résultats des tests Selenium
    # selenium_data = load_selenium_results()

    # Afficher le rapport
    stats = print_test_report(tests, results_data, selenium_data=None)

    # Afficher les statistiques
    print_statistics(stats, len(tests))

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
