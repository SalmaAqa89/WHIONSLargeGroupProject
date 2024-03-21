from django.core.management.base import BaseCommand, CommandError

from tasks.models import User,Template

import pytz
from faker import Faker
from random import randint, random
from django.conf import settings

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

template_fixtures = [
    {'name': 'Morning Reflection', 'questions': 'What are some things you feel grateful for ?,What are your main focuses for today e.g. fitness, reading ... ? ,What are you planning to do today ?', 'user_entry': False, 'deleted': False},
    {'name': 'Evening Reflection', 'questions': 'How was your day ? ,How well do you think you accomplished your goals for the day ?,What were your highlights of the day ?', 'user_entry': False, 'deleted': False},
    # Add more template fixtures as needed
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 3
    TEMPLATE_COUNT = 2
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
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
    
    def create_template(self, data):
        template_count = Template.objects.count()
        try:
            Template.objects.create(
                name=data['name'],
                questions=data['questions'],
                user_entry = data['user_entry'],
                deleted=data['deleted'],
               
            )
            print(f"Seeding user {template_count}/{self.TEMPLATE_COUNT}", end='\r')
        except Exception as e:
            print(f"Error creating template: {e}")

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'