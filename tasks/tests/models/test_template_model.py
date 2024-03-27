from django.test import TestCase
from tasks.models import Template


class TemplateModelTest(TestCase):
    def setUp(self):
        self.template = Template.objects.create(
            name='Test Template',
            questions='Question1,Question2,Question3'
        )

    def test_get_questions_array(self):
        questions = self.template.get_questions_array()
        self.assertEqual(questions, ['Question1', 'Question2', 'Question3'])



    def test_set_questions_array(self):
        questions_array = ['NewQuestion1', 'NewQuestion2', 'NewQuestion3']
        self.template.set_questions_array(questions_array)
        self.template.save()
        self.template.refresh_from_db()
        self.assertEqual(self.template.questions, 'NewQuestion1,NewQuestion2,NewQuestion3')