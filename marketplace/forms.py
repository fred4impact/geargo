from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Booking, Profile, Category
from django.utils import timezone


class CustomSignupForm(UserCreationForm):
    """Custom signup form with profile fields"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please enter your last name'
        })
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please enter a valid email address'
        })
    )
    
    # Profile fields
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)'
        })
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your city/location (optional)'
        })
    )
    membership_tier = forms.ChoiceField(
        choices=Profile.MEMBERSHIP_CHOICES,
        initial='casual',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    is_owner = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Set username to email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Update profile with custom fields (signal creates the profile)
            if hasattr(user, 'profile'):
                user.profile.phone = self.cleaned_data.get('phone', '')
                user.profile.location = self.cleaned_data.get('location', '')
                user.profile.membership_tier = self.cleaned_data.get('membership_tier', 'casual')
                user.profile.is_owner = self.cleaned_data.get('is_owner', False)
                user.profile.is_renter = True
                user.profile.save()
        
        return user
    
    def try_save(self, request):
        """Required method for Django Allauth compatibility"""
        if self.is_valid():
            user = self.save()
            # Allauth expects a tuple: (user, success_message)
            return (user, None)
        return None


class ItemForm(forms.ModelForm):
    """Form for creating and editing items"""
    images = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        required=False,
        help_text='Upload an image of your item (max 5MB, will be automatically resized to fit perfectly)'
    )
    
    def clean_images(self):
        image = self.cleaned_data.get('images')
        if image:
            from .utils import validate_image_file
            is_valid, error_message = validate_image_file(image, max_size_mb=5)
            if not is_valid:
                raise forms.ValidationError(error_message)
        return image
    
    class Meta:
        model = Item
        fields = ['category', 'title', 'description', 'daily_price', 'condition', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'daily_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()


class BookingForm(forms.ModelForm):
    """Form for creating bookings"""
    
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date < timezone.now().date():
                raise forms.ValidationError("Start date cannot be in the past.")
            
            if end_date <= start_date:
                raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data


class ProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = Profile
        fields = ['bio', 'phone', 'location', 'membership_tier', 'is_owner', 'is_renter']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'membership_tier': forms.Select(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    """Form for editing user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
