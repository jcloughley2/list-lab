from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lists.models import List, UserProfile
from django.utils import timezone
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Generates sample users and lists for testing'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.list_prompts = [
            "Best programming languages for beginners",
            "Top productivity apps for remote work",
            "Essential books for entrepreneurs",
            "Must-visit destinations in Europe",
            "Healthy breakfast ideas",
            "Best sci-fi movies of all time",
            "Home workout exercises without equipment",
            "Tips for better time management",
            "Classic novels everyone should read",
            "Popular board games for game night",
            "Essential kitchen gadgets",
            "Best practices for web development",
            "Indoor plants for beginners",
            "Meditation techniques for stress relief",
            "Creative writing prompts",
            "Budget-friendly travel tips",
            "Healthy snack ideas",
            "Photography tips for beginners",
            "Must-have camping gear",
            "DIY home organization ideas"
        ]

    def generate_list_content(self, prompt):
        items = []
        num_items = random.randint(5, 10)
        
        for i in range(num_items):
            item = f"{i+1}. {self.fake.sentence()}"
            items.append(item)
        
        return "\n".join(items)

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample users and lists...')

        # Create users
        users = []
        for i in range(15):
            username = self.fake.user_name()
            email = self.fake.email()
            password = 'testpass123'
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create user profile with bio
            profile = UserProfile.objects.get(user=user)
            profile.bio = self.fake.text(max_nb_chars=200)
            profile.save()
            
            users.append(user)
            self.stdout.write(f'Created user: {username}')

        # Create lists for each user
        for user in users:
            num_lists = random.randint(2, 5)  # Each user creates 2-5 lists
            
            for _ in range(num_lists):
                prompt = random.choice(self.list_prompts)
                title = f"{prompt.title()}"
                description = self.fake.text(max_nb_chars=150)
                content = self.generate_list_content(prompt)
                tags = ", ".join(self.fake.words(nb=random.randint(3, 6)))
                is_public = random.choice([True, True, False])  # 2/3 chance of being public
                
                list_obj = List.objects.create(
                    title=title,
                    description=description,
                    content=content,
                    tags=tags,
                    prompt=prompt,
                    owner=user,
                    is_public=is_public,
                    created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 30))
                )
                
                self.stdout.write(f'Created list: {title} for user {user.username}')

        # Create some forks
        public_lists = List.objects.filter(is_public=True)
        for user in random.sample(list(users), 10):  # 10 random users will fork lists
            lists_to_fork = random.sample(list(public_lists), random.randint(1, 3))
            for list_obj in lists_to_fork:
                forked_list = List.objects.create(
                    title=list_obj.title,
                    description=list_obj.description,
                    content=list_obj.content,
                    tags=list_obj.tags,
                    prompt=list_obj.prompt,
                    owner=user,
                    is_public=random.choice([True, False]),
                    original_list=list_obj,
                    created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 15))
                )
                self.stdout.write(f'Created fork of list: {forked_list.title} for user {user.username}')

        self.stdout.write(self.style.SUCCESS('Successfully generated sample data')) 