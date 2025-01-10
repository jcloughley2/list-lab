from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import List, UserProfile
from .forms import (
    ListPromptForm, ListForkForm, ListEditForm,
    UserRegistrationForm, UserProfileForm
)
from .services import ListGenerationService
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Homepage view - shows user's lists if authenticated, or public lists if not"""
    if request.user.is_authenticated:
        lists = List.objects.filter(owner=request.user)
        
        # Handle search query
        query = request.GET.get('q', '')
        if query:
            lists = lists.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )
        
        # Filter lists based on visibility parameter
        visibility = request.GET.get('visibility', 'all')
        if visibility == 'public':
            lists = lists.filter(is_public=True)
        elif visibility == 'private':
            lists = lists.filter(is_public=False)
            
        lists = lists.order_by('-created_at')
        return render(request, 'lists/home_authenticated.html', {
            'lists': lists,
            'current_visibility': visibility,
            'query': query
        })
    else:
        lists = List.objects.filter(is_public=True).order_by('-created_at')
        return render(request, 'lists/home_public.html', {
            'lists': lists
        })

@login_required
def create_list(request):
    """Create a new list manually or with AI assistance"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        
        # Limit content to 10 items
        content_lines = content.strip().split('\n')[:10]
        content = '\n'.join(content_lines)
        
        list_obj = List.objects.create(
            title=title,
            content=content,
            owner=request.user,
            is_public=request.POST.get('is_public', False) == 'on'
        )
        messages.success(request, 'List created successfully!')
        return redirect('list_detail', pk=list_obj.pk)
    
    return render(request, 'lists/create_list.html')

@login_required
def generate_list_content(request):
    """AJAX endpoint for generating list content"""
    if not request.method == 'POST' or not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    title = request.POST.get('title')
    if not title:
        return JsonResponse({'error': 'Title is required'}, status=400)
    
    service = ListGenerationService()
    try:
        result = service.generate_list(title)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error generating list: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

def explore(request):
    """Explore all public lists with search functionality"""
    query = request.GET.get('q', '')
    lists = List.objects.filter(is_public=True)
    
    if query:
        lists = lists.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )
    
    lists = lists.order_by('-created_at')
    
    return render(request, 'lists/explore.html', {
        'lists': lists,
        'query': query
    })

@login_required
def save_list(request):
    """Save a generated list"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        content = request.POST.get('content')
        tags = request.POST.get('tags')
        prompt = request.POST.get('prompt')
        
        list_obj = List.objects.create(
            title=title,
            description=description,
            content=content,
            tags=tags,
            prompt=prompt,
            owner=request.user
        )
        messages.success(request, 'List saved successfully!')
        return redirect('list_detail', pk=list_obj.pk)
    return redirect('home')

def list_detail(request, pk):
    """View a single list"""
    list_obj = get_object_or_404(List, pk=pk)
    if not list_obj.is_public and list_obj.owner != request.user:
        messages.error(request, 'This list is private.')
        return redirect('home')
    
    fork_form = ListForkForm() if request.user.is_authenticated else None
    
    # If it's an AJAX request, return just the list content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'lists/list_detail_content.html', {
            'list': list_obj,
            'fork_form': fork_form
        })
    
    # For regular requests, return the full page
    return render(request, 'lists/list_detail.html', {
        'list': list_obj,
        'fork_form': fork_form
    })

@login_required
def fork_list(request, pk):
    """Fork an existing list"""
    original_list = get_object_or_404(List, pk=pk)
    
    # Handle AJAX request for quick fork
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            forked_list = original_list.fork(
                new_owner=request.user,
                is_public=data.get('is_public', True)
            )
            return JsonResponse({
                'success': True,
                'fork_id': forked_list.pk,
                'fork_count': original_list.forks.count()
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Handle regular form submission
    if request.method == 'POST':
        form = ListForkForm(request.POST)
        if form.is_valid():
            forked_list = original_list.fork(
                new_owner=request.user,
                is_public=form.cleaned_data['is_public']
            )
            messages.success(request, 'List forked successfully!')
            return redirect('list_detail', pk=forked_list.pk)
    return redirect('list_detail', pk=pk)

@login_required
def edit_list(request, pk):
    """Edit a list"""
    list_obj = get_object_or_404(List, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ListEditForm(request.POST, instance=list_obj)
        if form.is_valid():
            list_obj = form.save(commit=False)
            # Limit content to 10 items
            content_lines = list_obj.content.strip().split('\n')[:10]
            list_obj.content = '\n'.join(content_lines)
            list_obj.save()
            messages.success(request, 'List updated successfully!')
            return redirect('list_detail', pk=list_obj.pk)
    else:
        # Limit existing content to 10 items before showing the form
        content_lines = list_obj.content.strip().split('\n')[:10]
        list_obj.content = '\n'.join(content_lines)
        form = ListEditForm(instance=list_obj)
    return render(request, 'lists/edit_list.html', {'form': form, 'list': list_obj})

@login_required
def my_lists(request):
    """View user's lists"""
    lists = List.objects.filter(owner=request.user)
    return render(request, 'lists/my_lists.html', {'lists': lists})

@login_required
def my_public_lists(request):
    """View user's public lists"""
    lists = List.objects.filter(owner=request.user, is_public=True)
    return render(request, 'lists/my_public_lists.html', {'lists': lists})

def user_lists(request, username):
    """View another user's public lists"""
    profile = get_object_or_404(UserProfile, user__username=username)
    lists = List.objects.filter(owner=profile.user, is_public=True)
    return render(request, 'lists/user_lists.html', {
        'profile': profile,
        'lists': lists
    })

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    # Get statistics
    total_lists = request.user.owned_lists.count()
    public_lists = request.user.owned_lists.filter(is_public=True).count()
    forked_lists = request.user.userprofile.forked_lists.count()
    
    context = {
        'form': form,
        'total_lists': total_lists,
        'public_lists': public_lists,
        'forked_lists': forked_lists,
    }
    
    return render(request, 'lists/profile.html', context)

@login_required
def delete_list(request, pk):
    """Delete a list"""
    list_obj = get_object_or_404(List, pk=pk, owner=request.user)
    if request.method == 'POST':
        list_obj.delete()
        messages.success(request, 'List deleted successfully!')
        return redirect('home')
    return redirect('list_detail', pk=pk)

@login_required
def toggle_like(request, pk):
    """Toggle like status for a list"""
    list_obj = get_object_or_404(List, pk=pk)
    
    # Check if list is public or user is owner
    if not list_obj.is_public and list_obj.owner != request.user:
        return JsonResponse({'error': 'This list is private'}, status=403)
    
    # Check if user has already liked the list
    like = list_obj.likes.filter(user=request.user).first()
    
    if like:
        # Unlike
        like.delete()
        liked = False
    else:
        # Like
        list_obj.likes.create(user=request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'count': list_obj.likes.count()
    })

@login_required
def toggle_visibility(request, pk):
    """Toggle public/private status for a list"""
    list_obj = get_object_or_404(List, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        list_obj.is_public = not list_obj.is_public
        list_obj.save()
        
        return JsonResponse({
            'is_public': list_obj.is_public,
            'message': f'List is now {"public" if list_obj.is_public else "private"}'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
