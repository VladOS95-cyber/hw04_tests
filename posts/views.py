from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse


from .models import Group, Post
from .forms import PostForm


User = get_user_model()


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """Функция возвращает страницу сообщества
    и выводит до 12 записей на странице.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'posts': posts, 'page': page, 'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post = post_list[0]
    counter = paginator.count
    contex = {
        'post_list': post_list,
        'counter': counter,
        'post': post
    }
    return render(request, 'profile.html', {'contex': contex, 'page': page, 'author': author})
 
 
def post_view(request, username, post_id):
    current_user = get_object_or_404(User, username=username)
    post = Post.objects.filter(author=current_user, id=post_id).first()
    counter = current_user.posts.all().count
    return render(request, 'post.html', {'current_user': current_user, 'post': post, 'counter': counter})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new.html', {'form': form, 'is_edit': True, 'post': post})
    post = form.save(commit=False)
    if request.user != post.author:
        return redirect(reverse('post', kwargs={
            'username': username, 
            'post_id': post_id, 
            }))
    post.author = request.user
    form.save()
    return redirect('index')
