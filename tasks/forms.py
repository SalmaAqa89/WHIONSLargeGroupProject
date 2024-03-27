"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User, JournalEntry, Calendar, UserPreferences,Template
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user
    
class JournalEntryForm(forms.ModelForm):
    """Form allowing user to create a journal entry"""
    
    widgets = {
            'text': CKEditorUploadingWidget(),  
        }
    
    class Meta:
        model = JournalEntry
        fields = ['title', 'text', 'mood']


        
    def __init__(self, user, text, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user
        self.fields['text'].initial = text
    
    def save(self, commit=True):
        """Create a new journal entry"""
        new_journal_entry = super().save(commit=False)
        if self.user:
            new_journal_entry.user = self.user
        if commit:
            new_journal_entry.save()
        return new_journal_entry
    
class JournalEntryForm(forms.ModelForm):
    """Form allowing user to create a journal entry"""
    
    class Meta:
        model = JournalEntry
        fields = ['title', 'text', 'mood']
        
    def __init__(self, user, text, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user
        self.fields['text'].initial = text
    
    def save(self, commit=True): 
        """Create a new journal entry"""
        new_journal_entry = super().save(commit=False) 

        new_journal_entry.user = self.user
        if commit:
            new_journal_entry.save() 
        return new_journal_entry

class CalendarForm(forms.ModelForm):
    """Form allowing user to create a journal entry"""
    class Meta:
        model = Calendar
        fields = ['title','text']

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['journal_time','monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'opt_out']
        widgets = {
            'journal_time': forms.TimeInput(attrs={'type': 'time'}),
            'monday': forms.CheckboxInput(),
            'tuesday': forms.CheckboxInput(),
            'wednesday': forms.CheckboxInput(),
            'thursday': forms.CheckboxInput(),
            'friday': forms.CheckboxInput(),
            'saturday': forms.CheckboxInput(),
            'sunday': forms.CheckboxInput(),
            'opt_out': forms.CheckboxInput(),
        }

class TemplateForm(forms.ModelForm):
    """Form allowing user to create a journal entry"""
    
    widgets = {
            'text': CKEditorUploadingWidget(),  
        }
    
    class Meta:
        model = Template
        fields = ['name', 'questions']
        
    def __init__(self, user,text, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean_name(self):
        """Validate that the name is unique for the given user."""
        name = self.cleaned_data.get('name')
        if Template.objects.filter(user=self.user, name=name).exists():
            raise ValidationError("A template with this name already exists.")
        return name
    
    def save(self):
        """Create a new journal entry"""
        new_template = super().save(commit=False)

        new_template.user = self.user
        new_template.save()
        return new_template

class JournalSearchForm(forms.Form):
        title = forms.CharField(required=False)



    

  
