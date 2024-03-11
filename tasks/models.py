from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.contrib import messages

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    
class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default = False)
    MOOD_CHOICES = [
        (1, 'Very Sad 😔'),  
        (2, 'Sad 🙁'),  
        (3, 'Neutral 😐'),  
        (4, 'Happy 🙂'),  
        (5, 'Very Happy😄'),  
    ]
    mood = models.IntegerField(choices=MOOD_CHOICES, default=3)  

    combined_answers = models.TextField(blank=True, null=True)

    def save_combined_answers(self, answers):
        self.combined_answers = ', '.join(answers)
        self.save()


    def delete_entry(self):
        self.deleted = True
        self.save()

    def recover_entry(self):
        self.deleted = False
        self.save()

class Template(models.Model):

    name = models.CharField(max_length = 50, blank = False)
    questions = models.CharField(max_length =255,blank = True)
    icon = models.ImageField(upload_to='template_icons/', null=True, blank=True)
    user_entry = models.BooleanField(default = True)
    deleted = models.BooleanField(default = False)
    MOOD_CHOICES = [
        (1, 'Very Sad 😔'),  
        (2, 'Sad 🙁'),  
        (3, 'Neutral 😐'),  
        (4, 'Happy 🙂'),  
        (5, 'Very Happy😄'),  
    ]
    mood = models.IntegerField(choices=MOOD_CHOICES, default=3)  

    def get_questions(self):
        return self.questions

    def get_questions_array(self):
        return self.questions.split(',')

    def set_questions_array(self, values):
        self.questions = ','.join(values)


class Calendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField()
