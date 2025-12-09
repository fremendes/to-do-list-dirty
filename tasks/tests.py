from django.test import TestCase
from django.urls import reverse

from tasks.models import Task


def tc(test_id):
    """Décorateur pour ajouter un ID de test"""
    def decorator(test_func):
        test_func.test_number = test_id
        return test_func
    return decorator

class TaskURLTests(TestCase):

    def setUp(self):
        """Configuration initiale pour tous les tests"""
        self.task = Task.objects.create(
            title="Test task",
            complete=False
        )

    @tc("TC001")
    def test_home_page_url(self):
        """Test que la page d'accueil fonctionne"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @tc("TC002")
    def test_update_task_url(self):
        """Test que l'URL de mise à jour fonctionne"""
        url = reverse('update_task', args=[str(self.task.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @tc("TC003")
    def test_delete_task_url(self):
        """Test que l'URL de suppression fonctionne"""
        url = reverse('delete', args=[str(self.task.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @tc("TC004")
    def test_update_task_post(self):
        """Test la mise à jour via POST"""
        url = reverse('update_task', args=[str(self.task.id)])
        response = self.client.post(url, {
            'title': 'Updated task',
            'complete': True
        })
        # Vérifie la redirection après mise à jour (302 = redirect)
        self.assertEqual(response.status_code, 302)

        # Vérifie que la tâche a été mise à jour
        updated_task = Task.objects.get(id=self.task.id)
        self.assertEqual(updated_task.title, 'Updated task')
        self.assertEqual(updated_task.complete, True)

    @tc("TC005")
    def test_delete_task_post(self):
        """Test la suppression via POST"""
        url = reverse('delete', args=[str(self.task.id)])
        response = self.client.post(url)
        # Vérifie la redirection après suppression
        self.assertEqual(response.status_code, 302)
        # Vérifie que la tâche a été supprimée
        self.assertEqual(Task.objects.count(), 0)

    @tc("TC006")
    def test_create_task_post(self):
        """Test la création d'une tâche via POST"""
        initial_count = Task.objects.count()
        response = self.client.post('/', {
            'title': 'New task',
            'complete': False
        })
        # Vérifie la redirection après création
        self.assertEqual(response.status_code, 302)
        # Vérifie qu'une nouvelle tâche a été créée
        self.assertEqual(Task.objects.count(), initial_count + 1)


class TaskModelTests(TestCase):

    @tc("TC007")
    def test_task_creation(self):
        """Test la création d'un modèle Task"""
        task = Task.objects.create(
            title="Test task",
            complete=False
        )
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.complete, False)
        self.assertIsNotNone(task.created)

    @tc("TC008")
    def test_task_string_representation(self):
        """Test la représentation en string du modèle"""
        task = Task.objects.create(title="Test task")
        self.assertEqual(str(task), "Test task")
