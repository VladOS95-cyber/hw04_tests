from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse


from .forms import PostForm
from .models import Group, Post


User = get_user_model()


POSTS_PER_PAGE = 12

def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """Функция возвращает страницу сообщества
    и выводит до 12 записей на странице.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_quantity = paginator.count
    return render(request, 'group.html', {
        'posts_quantity': posts_quantity,
        'group': group, 
        'posts': posts, 
        'page': page, 
        'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post = post_list.first()
    posts_quantity = paginator.count
    return render(request, 'profile.html', {
        'posts_quantity': posts_quantity,
        'post': post, 
        'page': page, 
        'author': author, 
        'paginator': paginator})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    posts_quantity = post.author.posts.all().count
    return render(request, 'post.html', {
        'author': post.author, 
        'post': post,
        'posts_quantity': posts_quantity})


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
    files=request.FILES or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new.html', {'form': form, 'is_edit': False})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect(reverse('index'))


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    if request.user != author:
        return redirect(reverse('index'))
    form = PostForm(request.POST or None, 
    files=request.FILES or None, 
    instance=post)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new.html', {
            'form': form, 
            'is_edit': True, 
            'post': post})
    post = form.save(commit=False)
    form.save()
    return redirect(reverse('post', kwargs={
            'username': username, 
            'post_id': post_id, 
            }))


def page_not_found(request, exception=None):
    return render(
        request, 
        'misc/404.html', 
        {'path': request.path}, 
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def add_comment(request):
    