#!/usr/bin/env python3
"""
TC017 - Test de vérification des impacts croisés lors de la suppression

Ce test vérifie qu'une suppression de tâche n'affecte pas les autres tâches :
1. Créer une tâche (task1) et sauvegarder son ID
2. Créer une autre tâche (task2)
3. Supprimer task2
4. Vérifier que task1 est toujours présente et intacte
"""

import json
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10
TASK1_TITLE = "Task Cross Impact Test 1"
TASK2_TITLE = "Task Cross Impact Test 2"


class TC017TestRunner:
    """Test runner pour TC017 - Impacts croisés."""

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
        self.task1_id = None
        self.task1_title = TASK1_TITLE
        self.task2_title = TASK2_TITLE

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
            print("💡 Assurez-vous que ChromeDriver est installé")
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
            return False

    def create_task(self, task_title):
        """
        Crée une nouvelle tâche.

        Args:
            task_title: Titre de la tâche

        Returns:
            str: ID de la tâche créée, ou None si échec
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
            time.sleep(1)

            # Trouver la nouvelle tâche (celle qui a le titre qu'on vient de créer)
            tasks_after = self.driver.find_elements(By.CLASS_NAME, "item-row")

            for task in tasks_after:
                task_id = task.get_attribute("data-task-id")
                task_title_attr = task.get_attribute("data-task-title")

                if task_title_attr == task_title:
                    print(f"✅ Tâche '{task_title}' créée avec ID={task_id}")
                    return task_id

            print("⚠️  Tâche créée mais ID non trouvé")
            return None

        except Exception as e:
            print(f"❌ Erreur lors de la création de '{task_title}': {e}")
            return None

    def find_task_by_id(self, task_id):
        """
        Trouve une tâche par son ID.

        Args:
            task_id: ID de la tâche

        Returns:
            WebElement: Élément de la tâche, ou None si non trouvé
        """
        try:
            selector = f"div.item-row[data-task-id='{task_id}']"
            task = self.driver.find_element(By.CSS_SELECTOR, selector)
            return task
        except NoSuchElementException:
            return None

    def find_task_by_title(self, task_title):
        """
        Trouve une tâche par son titre.

        Args:
            task_title: Titre de la tâche

        Returns:
            WebElement: Élément de la tâche, ou None si non trouvé
        """
        try:
            selector = f"div.item-row[data-task-title='{task_title}']"
            task = self.driver.find_element(By.CSS_SELECTOR, selector)
            return task
        except NoSuchElementException:
            return None

    def delete_task_by_id(self, task_id):
        """
        Supprime une tâche par son ID.

        Args:
            task_id: ID de la tâche

        Returns:
            bool: True si succès, False sinon
        """
        try:
            task = self.find_task_by_id(task_id)
            if not task:
                print(f"⚠️  Tâche ID={task_id} non trouvée")
                return False

            # Cliquer sur le bouton "Supprimer"
            delete_button = task.find_element(By.CSS_SELECTOR, "a.btn-danger")
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

        except Exception as e:
            print(f"❌ Erreur lors de la suppression de task ID={task_id}: {e}")
            return False

    def verify_task_exists(self, task_id, task_title):
        """
        Vérifie qu'une tâche existe.

        Args:
            task_id: ID de la tâche
            task_title: Titre attendu

        Returns:
            bool: True si la tâche existe avec le bon titre, False sinon
        """
        task = self.find_task_by_id(task_id)
        if not task:
            return False

        actual_title = task.get_attribute("data-task-title")
        return actual_title == task_title

    def run_test(self):
        """
        Exécute le test complet TC017.

        Returns:
            dict: Résultat du test avec statut et détails
        """
        result = {
            'test_number': '17',
            'test_name': 'TC017 - Impacts croisés',
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

            # Étape 2: Créer la première tâche
            print("\n➕ Étape 1: Création de la tâche 1")
            self.task1_id = self.create_task(self.task1_title)

            if not self.task1_id:
                result['status'] = 'failed'
                result['errors'].append("Échec création task1")
                return result

            result['details']['task1_id'] = self.task1_id
            result['details']['task1_title'] = self.task1_title

            # Étape 3: Créer la deuxième tâche
            print("\n➕ Étape 2: Création de la tâche 2")
            task2_id = self.create_task(self.task2_title)

            if not task2_id:
                result['status'] = 'failed'
                result['errors'].append("Échec création task2")
                return result

            result['details']['task2_id'] = task2_id
            result['details']['task2_title'] = self.task2_title

            # Étape 4: Vérifier que les deux tâches existent
            print("\n🔍 Étape 3: Vérification existence des 2 tâches")
            if not self.verify_task_exists(self.task1_id, self.task1_title):
                result['status'] = 'failed'
                result['errors'].append("Task1 non trouvée après création des 2 tâches")
                return result
            print("✅ Task1 présente")

            if not self.verify_task_exists(task2_id, self.task2_title):
                result['status'] = 'failed'
                result['errors'].append("Task2 non trouvée après création")
                return result
            print("✅ Task2 présente")

            # Étape 5: Supprimer la deuxième tâche
            print("\n🗑️  Étape 4: Suppression de la tâche 2")
            if not self.delete_task_by_id(task2_id):
                result['status'] = 'failed'
                result['errors'].append("Échec suppression task2")
                return result
            print("✅ Task2 supprimée")

            # Étape 6: Vérifier que task2 n'existe plus
            print("\n🔍 Étape 5: Vérification que task2 est supprimée")
            if self.verify_task_exists(task2_id, self.task2_title):
                result['status'] = 'failed'
                result['errors'].append("Task2 toujours présente après suppression")
                return result
            print("✅ Task2 bien supprimée")

            # Étape 7: CRITIQUE - Vérifier que task1 existe toujours
            print("\n🔍 Étape 6: Vérification CRITIQUE - task1 toujours présente")
            if not self.verify_task_exists(self.task1_id, self.task1_title):
                result['status'] = 'failed'
                result['errors'].append(
                    "IMPACT CROISÉ DÉTECTÉ: " \
                    "Task1 a été affectée par la suppression de task2!"
                )
                return result

            print("✅ Task1 toujours présente et intacte")
            print("✅ PAS D'IMPACT CROISÉ - Le test est réussi!")

            result['details']['cross_impact_detected'] = False

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
    # Charger les résultats existants si le fichier existe
    import os
    existing_tests = []
    if os.path.exists(filename):
        try:
            with open(filename, encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_tests = existing_data.get('tests', [])
        except Exception:
            pass

    # Ajouter le nouveau test
    new_test = {
        'test_number': result['test_number'],
        'test_name': result['test_name'],
        'test_class': 'SeleniumE2E',
        'test_method': 'tc017_cross_impact',
        'status': result['status'],
        'error_message': '\n'.join(result['errors']) if result['errors'] else None,
        'description': 'Test E2E de vérification '
        'des impacts croisés lors de la suppression',
        'details': result['details']
    }

    # Remplacer si le test existe déjà, sinon ajouter
    test_exists = False
    for i, test in enumerate(existing_tests):
        if test.get('test_number') == result['test_number']:
            existing_tests[i] = new_test
            test_exists = True
            break

    if not test_exists:
        existing_tests.append(new_test)

    # Calculer les statistiques
    passed = sum(1 for t in existing_tests if t.get('status') == 'passed')
    failed = sum(1 for t in existing_tests if t.get('status') == 'failed')
    errors = sum(1 for t in existing_tests if t.get('status') == 'error')

    output = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(existing_tests),
        'summary': {
            'passed': passed,
            'failed': failed,
            'errors': errors
        },
        'tests': existing_tests
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
    print("TC017 - Test End-to-End: Impacts croisés")
    print("=" * 70)

    # Vérifier si on veut le mode verbose
    headless = '--no-headless' not in sys.argv

    runner = TC017TestRunner(headless=headless)

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
            'test_number': '17',
            'test_name': 'TC017 - Impacts croisés',
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
