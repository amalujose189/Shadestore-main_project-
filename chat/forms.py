
from django import forms
from .models import Message, ChatRoom
from django.contrib.auth.models import User

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment_file', 'attachment_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make content field not required
        self.fields['content'].required = False
        self.fields['attachment_file'].required = False
        self.fields['attachment_image'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        attachment_file = cleaned_data.get('attachment_file')
        attachment_image = cleaned_data.get('attachment_image')
        
        # Ensure at least one field has data
        if not content and not attachment_file and not attachment_image:
            raise forms.ValidationError("You must enter a message or attach a file.")
        
        return cleaned_data
class GroupChatForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select users to add to this group chat"
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'})
        }

    def __init__(self, *args, **kwargs):
        super(GroupChatForm, self).__init__(*args, **kwargs)
        self.fields['participants'].label_from_instance = lambda obj: obj.get_full_name() or obj.username
