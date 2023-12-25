from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from django.views.decorators.http import require_POST
# Create your views here.

class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.objects.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment =None
    form = CommentForm(data = request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    comments = post.comments.filter(active=True)
    return render(request, 'blog/post/detail.html', {'post': post,
                                                      'form':form,
                                                      'comments':comments})

def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n\n"
            send_mail(subject, message, 'sudharshanvas@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
        
    return render(request, 'blog/post/share.html', {'post': post, 'form':form, 'sent': sent})


def post_list(request):
    post_list= Post.objects.all()
    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts})

def post_detail(request, year, month, day, post, id):
    post = get_object_or_404(Post, slug=post, publish__year = year, publish__month = month, publish__day = day, id = id)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'body':post.body.split("\n"),
                                                     'form': form,
                                                     'comments':comments})
