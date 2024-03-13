from django.core.management.base import BaseCommand, CommandError

from tasks.models import User,Template

import pytz
from faker import Faker
from random import randint, random
from PIL import Image
import os
from django.conf import settings

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

template_fixtures = [
    {'name': 'Morning Reflection', 'questions': 'What are some things you feel grateful for ?,What are your main focuses for today e.g. fitness, reading ... ? ,What are you planning to do today ?', 'icon': 'media/template_icons/morning.jpeg', 'deleted': False},
    {'name': 'Evening Reflection', 'questions': 'How was your day ? ,How well do you think you accomplished your goals for the day ?,What were your highlights of the day ?', 'icon': 'media/template_icons/night.jpeg', 'deleted': False},
    # Add more template fixtures as needed
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 100
    DEFAULT_PASSWORD = 'Password123'
    TEMPLATE_COUNT = 2
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.create_templates()
        self.users = User.objects.all()


    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    def create_templates(self):
        for data in template_fixtures:
            self.try_create_template(data)

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
    
    def try_create_template(self, data):
        try:
            self.create_template(data)
        except Exception as e:
            print(f"Error creating template: {e}")
    
    @staticmethod
    def load_image(icon_path):
        try:
            img = Image.open(icon_path)
            img = img.resize((100, 100))  # Adjust the size as needed
            return img
        except Exception as e:
            print(f"Error loading image {icon_path}: {e}")
            return None  # Handle the case where image loading fails

    def create_template(self, data):
        try:
            icon_path = data['icon']
            img = self.load_image(icon_path)
            
            # Save the image file to the media directory and get the relative path
            img_path = self.save_image(img, icon_path)

            Template.objects.create(
                name=data['name'],
                questions=data['questions'],
                icon=img_path,
                deleted=data['deleted'],
            )
        except Exception as e:
            print(f"Error creating template: {e}")

    
    def save_image(self, img, original_path):
        try:
            # Define your media directory path
            media_dir = os.path.join(settings.MEDIA_ROOT, 'template_icons')

            # Generate a unique filename or use the original one
            filename = str(Faker().uuid4()) + original_path.split('/')[-1]

            # Save the image to the media directory
            img.save(os.path.join(media_dir, filename))

            # Return the relative path to be stored in the database
            return 'template_icons/' + filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'
