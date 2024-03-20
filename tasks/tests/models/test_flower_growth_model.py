from django.test import TestCase
from django.db.utils import IntegrityError
from tasks.models import User, FlowerGrowth
from django.utils import timezone
import datetime

class FlowerGrowthModelTests(TestCase):
    """Unit Tests for the Flower Growth Model"""
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.flower_growth = FlowerGrowth.objects.create(
            user=self.user,
            stage=0,
            last_entry_date=datetime.date.today()
        )

    def test_flower_growth_default_stage(self):
        """Ensure the default stage is set correctly."""
        self.assertEqual(self.flower_growth.stage, 0)

    def test_increment_flower_growth_stage(self):
        """Test incrementing the flower's growth stage."""
        current_stage = self.flower_growth.stage
        self.flower_growth.increment_stage()
        self.assertEqual(self.flower_growth.stage, current_stage + 1)

    def test_reset_flower_growth_stage(self):
        """Test resetting the flower's growth stage to zero."""
        self.flower_growth.increment_stage()  
        self.flower_growth.reset_to_stage_zero()
        self.assertEqual(self.flower_growth.stage, 0)

    def test_update_last_entry_date(self):
        """Test updating the last entry date."""
        new_date = timezone.now().date() - datetime.timedelta(days=1)
        self.flower_growth.update_last_entry_date(new_date)
        self.assertEqual(self.flower_growth.last_entry_date, new_date)

    def test_flower_growth_must_have_user(self):
        """Ensure FlowerGrowth instance must have a user."""
        with self.assertRaises(IntegrityError):
            FlowerGrowth.objects.create(
                stage=1,
                last_entry_date=datetime.date.today()
            )

    def test_flower_growth_one_to_one_user_relationship(self):
        """Test that each user can have only one FlowerGrowth instance."""
        with self.assertRaises(IntegrityError):
            FlowerGrowth.objects.create(
                user=self.user,
                stage=1,
                last_entry_date=datetime.date.today()
            )
