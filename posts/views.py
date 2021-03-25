from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.shortcuts import redirect


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html",
                  {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
                  {"group": group, "posts": posts, "page": page,
                   "paginator": paginator})


@login_required
def post_new(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'newpost.html', {'form': form})

    form = PostForm(request.POST)

    if not form.is_valid():
        return render(request, 'newpost.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    all_posts = Post.objects.all().filter(author__username=username)
    counter = all_posts.count()
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                  {'page': page, 'author': author, 'counter': counter})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    full_post = get_object_or_404(Post, id=post_id)
    post = get_object_or_404(Post, id=post_id)
    all_posts = Post.objects.all().filter(author__username=username)
    counter = all_posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    return render(request, 'post.html',
                  {'author': author,
                   'counter': counter, 'form': form, 'comments': comments,
                   'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', username=post.author, post_id=post.id)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=username)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)

    # if request.method == 'POST':
    if request.user != post.author:
        return redirect('post', username=post.author, post_id=post.id)
    if form.is_valid():
        form.save()
        return redirect('post', username=post.author, post_id=post.id)
    # form = PostForm(instance=post)
    return render(request, 'newpost.html',
                  {'form': form, 'post': post, 'author': author})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html",
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    # ...
    pass


@login_required
def profile_unfollow(request, username):
    # ...
    pass
