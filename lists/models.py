from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey('List', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'list')  # Prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} likes {self.list.title}"

class List(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    tags = models.CharField(max_length=500)  # Store as comma-separated values
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_lists')
    is_public = models.BooleanField(default=True)
    original_list = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forks')
    prompt = models.TextField()  # Store the original prompt used to generate the list
    liked_by = models.ManyToManyField(User, through='Like', related_name='liked_lists')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def fork(self, new_owner, is_public=True):
        """Create a fork of the current list"""
        forked_list = List.objects.create(
            title=self.title,
            description=self.description,
            content=self.content,
            tags=self.tags,
            owner=new_owner,
            is_public=is_public,
            original_list=self,
            prompt=self.prompt
        )
        return forked_list

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    forked_lists = models.ManyToManyField(List, related_name='forked_by', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for every new User"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    instance.userprofile.save()
