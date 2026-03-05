from django.db import models
from django.contrib.auth.models import User
from ecom.models import Customer, FieldStaff, ShowroomStaff, Painter

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    is_group = models.BooleanField(default=False)
    group_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_groups')
    
    def __str__(self):
        return self.name

class Message(models.Model):
    ATTACHMENT_TYPE_CHOICES = [
        ('none', 'None'),
        ('file', 'File'),
        ('image', 'Image'),
        ('location', 'Location'),
    ]
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True) 
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_forwarded = models.BooleanField(default=False)
    original_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forwarded_messages')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES, default='none')
    attachment_file = models.FileField(upload_to='chat_attachments/files/', null=True, blank=True)
    attachment_image = models.ImageField(upload_to='chat_attachments/images/', null=True, blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"