#!/usr/bin/env python3
"""
TC016 - Test de cycle complet CRUD sur 10 tâches (End-to-End avec Selenium)

Ce test automatise le scénario manuel TC016 :
- Se connecter à l'application
- Compter le nombre initial de tâches
- Créer 10 nouvelles tâches
- Vérifier le comptage (N + 10)
- Supprimer les 10 tâches créées
- Vérifier le retour au nombre initial (N)
"""

import json
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10
TASK_PREFIX = "Test Task E2E"


class TC016TestRunner:
    """Test runner pour TC016 - CRUD de 10 tâches."""

    def __init__(self, base_url=BASE_URL, headless=True):
        """
        Initialise le test runner.

        Args:
            base_url: URL de base de l'application
            headless: Mode headless (sans interface graphique)
        """
        self.base_url = base_url
        self.headless = headless
        self.driver = None
        self.initial_task_count = 0
        self.created_task_ids = []

    def setup(self):
        """Configure le driver Selenium."""
        print("🔧 Configuration du driver Selenium...")
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        try:
            self.driver = webdriver.Chrome(options=options)
            print("✅ Driver Chrome initialisé")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du driver: {e}")
            print("💡 Assurez-vous que ChromeDriver est installé:")
            print("   brew install chromedriver  (macOS)")
            print("   apt install chromium-chromedriver  (Linux)")
            raise

    def teardown(self):
        """Ferme le driver Selenium."""
        if self.driver:
            self.driver.quit()
            print("🔒 Driver fermé")

    def navigate_to_app(self):
        """Navigue vers l'application."""
        print(f"\n📍 Navigation vers {self.base_url}...")
        try:
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, TIMEOUT).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            print("✅ Application chargée")
            return True
        except TimeoutException:
            print("❌ Timeout: L'application n'a pas chargé à temps")
            print(f"💡 Assurez-vous que le serveur Django tourne sur {self.base_url}")
            return False

    def count_tasks(self):
        """
        Compte le nombre de tâches affichées.

        Returns:
            int: Nombre de tâches
        """
        try:
            # Les tâches ont la classe 'item-row'
            tasks = self.driver.find_elements(By.CLASS_NAME, "item-row")
            count = len(tasks)
            print(f"📊 Nombre de tâches trouvées: {count}")
            return count
        except Exception as e:
            print(f"⚠️  Erreur lors du comptage: {e}")
            return 0

    def create_task(self, task_title):
        """
        Crée une nouvelle tâche.

        Args:
            task_title: Titre de la tâche

        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Trouver le champ de saisie
            input_field = self.driver.find_element(By.ID, "id_title")
            input_field.clear()
            input_field.send_keys(task_title)

            # Cliquer sur le bouton de création
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, "input.btn-primary[type='submit']")
            submit_button.click()

            # Attendre la redirection et le rechargement
            time.sleep(0.5)

            return True
        except Exception as e:
            print(f"❌ Erreur lors de la création de '{task_title}': {e}")
            return False

    def delete_task_by_title(self, task_title):
        """
        Supprime une tâche par son titre.

        Args:
            task_title: Titre de la tâche à supprimer

        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Trouver toutes les tâches
            task_rows = self.driver.find_elements(By.CLASS_NAME, "item-row")

            for row in task_rows:
                # Vérifier si le titre correspond
                if task_title in row.text:
                    # Cliquer sur le bouton "Supprimer"
                    delete_button = row.find_element(By.CSS_SELECTOR, "a.btn-danger")
                    delete_button.click()

                    # Attendre la page de confirmation
                    time.sleep(0.3)

                    # Confirmer la suppression
                    confirm_button = WebDriverWait(self.driver, TIMEOUT).until(
                        expected_conditions.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.btn-delete[type='submit']"))
                    )
                    confirm_button.click()

                    # Attendre la redirection
                    time.sleep(0.5)

                    return True

            print(f"⚠️  Tâche '{task_title}' non trouvée")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de '{task_title}': {e}")
            return False

    def run_test(self):
        """
        Exécute le test complet TC016.

        Returns:
            dict: Résultat du test avec statut et détails
        """
        result = {
            'test_number': '16',
            'test_name': 'TC016 - CRUD 10 tâches',
            'status': 'passed',
            'details': {},
            'errors': []
        }

        try:
            # Étape 1: Naviguer vers l'application
            if not self.navigate_to_app():
                result['status'] = 'failed'
                result['errors'].append("Impossible d'accéder à l'application")
                return result

            # Étape 2: Compter les tâches initiales
            print("\n📝 Étape 1: Comptage initial des tâches")
            self.initial_task_count = self.count_tasks()
            result['details']['initial_count'] = self.initial_task_count

            # Étape 3: Créer 10 tâches
            print("\n➕ Étape 2: Création de 10 tâches")
            created_count = 0
            for i in range(1, 11):
                task_title = f"{TASK_PREFIX} {i}"
                print(f"   Création de '{task_title}'...", end=" ")
                if self.create_task(task_title):
                    created_count += 1
                    print("✅")
                else:
                    print("❌")
                    result['errors'].append(f"Échec création '{task_title}'")

            result['details']['created_count'] = created_count

            if created_count != 10:
                result['status'] = 'failed'
                result['errors'].append(f"Seulement {created_count}/10 tâches créées")

            # Étape 4: Vérifier le comptage après création
            print("\n📊 Étape 3: Comptage après création")
            count_after_creation = self.count_tasks()
            result['details']['count_after_creation'] = count_after_creation
            expected_count = self.initial_task_count + 10

            if count_after_creation == expected_count:
                print("✅ Comptage correct: " \
                       "{count_after_creation} (attendu: {expected_count})")
            else:
                print("❌ Comptage incorrect: " \
                      "{count_after_creation} (attendu: {expected_count})")
                result['status'] = 'failed'
                result['errors'].append(
                    "Comptage après création" \
                    ": {count_after_creation} != {expected_count}"
                )

            # Étape 5: Supprimer les 10 tâches
            print("\n🗑️  Étape 4: Suppression de 10 tâches")
            deleted_count = 0
            for i in range(1, 11):
                task_title = f"{TASK_PREFIX} {i}"
                print(f"   Suppression de '{task_title}'...", end=" ")
                if self.delete_task_by_title(task_title):
                    deleted_count += 1
                    print("✅")
                else:
                    print("❌")
                    result['errors'].append(f"Échec suppression '{task_title}'")

            result['details']['deleted_count'] = deleted_count

            if deleted_count != 10:
                result['status'] = 'failed'
                result['errors'].append(
                    f"Seulement {deleted_count}/10 tâches supprimées"
                )

            # Étape 6: Vérifier le retour au comptage initial
            print("\n📊 Étape 5: Comptage final")
            final_count = self.count_tasks()
            result['details']['final_count'] = final_count

            if final_count == self.initial_task_count:
                print("✅ Comptage final correct: " \
                       "{final_count} (attendu: {self.initial_task_count})")
            else:
                print("❌ Comptage final incorrect: " \
                      "{final_count} (attendu: {self.initial_task_count})")
                result['status'] = 'failed'
                result['errors'].append(
                    f"Comptage final: {final_count} != {self.initial_task_count}"
                )

        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            print(f"\n❌ Erreur critique: {e}")

        return result


def export_results_to_json(result, filename='result_test_selenium.json'):
    """
    Exporte les résultats du test au format JSON.

    Args:
        result: Dictionnaire contenant les résultats du test
        filename: Nom du fichier JSON de sortie
    """
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': 1,
        'summary': {
            'passed': 1 if result['status'] == 'passed' else 0,
            'failed': 1 if result['status'] == 'failed' else 0,
            'errors': 1 if result['status'] == 'error' else 0
        },
        'tests': [
            {
                'test_number': result['test_number'],
                'test_name': result['test_name'],
                'test_class': 'SeleniumE2E',
                'test_method': 'tc016_crud_10_tasks',
                'status': result['status'],
                'error_message': '\n'.join(result['errors'])
                if result['errors'] else None,
                'description': 'Test E2E de cycle complet CRUD sur 10 tâches',
                'details': result['details']
            }
        ]
    }

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Résultats exportés vers {filename}")
    except Exception as e:
        print(f"\n⚠️  Erreur lors de l'export JSON: {e}")


def main():
    """Point d'entrée principal."""
    print("=" * 70)
    print("TC016 - Test End-to-End: CRUD de 10 tâches")
    print("=" * 70)

    # Vérifier si on veut le mode verbose
    headless = '--no-headless' not in sys.argv

    runner = TC016TestRunner(headless=headless)

    try:
        runner.setup()
        result = runner.run_test()

        # Afficher le résultat
        print("\n" + "=" * 70)
        print("RÉSULTAT DU TEST")
        print("=" * 70)
        print(f"Test: {result['test_name']}")
        print(f"Statut: {result['status'].upper()}")
        print("\nDétails:")
        for key, value in result['details'].items():
            print(f"  - {key}: {value}")

        if result['errors']:
            print(f"\n❌ Erreurs ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        else:
            print("\n✅ Aucune erreur")

        print("=" * 70)

        # Exporter les résultats en JSON
        export_results_to_json(result)

        # Code de sortie
        return 0 if result['status'] == 'passed' else 1

    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        # En cas d'erreur fatale, créer quand même un résultat
        error_result = {
            'test_number': '16',
            'test_name': 'TC016 - CRUD 10 tâches',
            'status': 'error',
            'details': {},
            'errors': [str(e)]
        }
        export_results_to_json(error_result)
        return 1
    finally:
        runner.teardown()


if __name__ == '__main__':
    sys.exit(main())
