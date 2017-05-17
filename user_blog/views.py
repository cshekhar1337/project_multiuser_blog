from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import User_Blog, Blog_Post, Post_Like, Comment
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def p_decorate(func):
    ''' decorator to check if there is a session or not.. if there is no session it loads login page else runs the request'''

    def func_wrapper(*args):

        if 'user_name' not in args[0].session and 'name' not in args[0].session:
            return render(args[0], 'user_blog/login_signup.html')
        else:
            print("in else block")
            return func(*args)

    return func_wrapper


@p_decorate
def home(request):
    '''
    This API is the landing page of the application
    '''
    return blog_render(request)


def register(request):
    '''
    POST API which receives the request for registration.
    This API verifies that email and user name don't match with any other existing applicant,
    sets the user session details and redirects the user to login page .
    '''

    if request.POST:
        # Obtain form data from the request and store in session variables so they can be accessed across functions
        user_info = request.POST
        is_valid_user = True

        if User_Blog.objects.filter(email=user_info['email']).exists():
            is_valid_user = False
            error_message = "This email is already registered!"
            messages.add_message(request, messages.ERROR, error_message)
        if User_Blog.objects.filter(user_name=user_info['user_name']).exists():
            is_valid_user = False
            error_message = "This user name is already registered!"
            messages.add_message(request, messages.ERROR, error_message)

        if not is_valid_user:
            return render(request, 'user_blog/login_signup.html')

        # If the user is valid, set the user session details
        request.session['name'] = user_info['name']
        request.session['email'] = user_info['email']
        request.session['user_name'] = user_info['user_name']
        email = user_info['email']
        pw_hash = make_password(user_info['password'], 'user_blog', hasher='default')
        print(pw_hash)
        name = user_info['name']
        user_name = user_info['user_name']
        user_blog = User_Blog(name=name, email=email, user_name=user_name, pw_hash=pw_hash)
        user_blog.save()
        error_message = "Successfully registered... Please Login to your account"
        messages.add_message(request, messages.SUCCESS, error_message)

        # Redirect the user to background check consent form
        return render(request, 'user_blog/login_signup.html')


def logout(request):
    ''' deletes the session'''

    del request.session['name']
    del request.session['user_name']
    error_message = "Logout successful.."
    messages.add_message(request, messages.SUCCESS, error_message)

    return render(request, 'user_blog/login_signup.html')


def login(request):
    ''' handles the login request. If session already exists then renders the blow view request'''
    if request.POST:
        email = request.POST['email']
        password = make_password(request.POST['password'], 'user_blog', hasher='default')
        if (User_Blog.objects.filter(email=email, pw_hash=password).exists()):
            blog = blog_list_values()

            user_blog = User_Blog.objects.filter(email=email, pw_hash=password)[0]

            # Set the user's email in session
            request.session['user_name'] = user_blog.user_name
            request.session['name'] = user_blog.name

            return render(request, 'user_blog/application_success_page.html',
                          {'res': blog, 'name': user_blog.name, 'user_name': user_blog.user_name})
        else:
            messages.add_message(request, messages.ERROR, "Wrong email or password..")
            return render(request, 'user_blog/login_signup.html')

    if 'user_name' in request.session and 'name' in request.session:
        return blog_render(request)
    else:
        blog = blog_list_values()
        return render(request, 'user_blog/application_success_page.html', {'res': blog})


def blog_view(request):
    if 'user_name' in request.session and 'name' in request.session:
        blog = blog_list_values()
        return render(request, 'user_blog/application_success_page.html',
                      {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})
    else:
        blog = blog_list_values()
        return render(request, 'user_blog/application_success_page.html', {'res': blog})


def blog_list_values():
    ''' returns a dictionary that contains all the entries of the blog'''
    blogs = Blog_Post.objects.all().order_by('updated_at')
    results = {}
    resultList = []
    for blog in blogs:
        res = {}
        res['blog_id'] = blog.blog_id
        res['subject'] = blog.subject
        res['content'] = blog.content
        res['updated_at'] = blog.updated_at
        res['user_name'] = blog.user_name.user_name
        postLike = [e.user_name.user_name for e in Post_Like.objects.filter(blog_id__blog_id=blog.blog_id)]
        res['likes'] = postLike
        comments = []
        for e in Comment.objects.filter(blog_id__blog_id=blog.blog_id):
            comment = {}
            comment['id'] = e.comment_id
            comment['user_name'] = e.user_name.user_name
            comment['comment'] = e.comment
            comments.append(comment)
        res['comments'] = comments

        resultList.append(res)

    return resultList


@p_decorate
def likepost(request):
    ''' Updates the table that stores like and username. When done send a confirmation message which is displayed on client side using jquery'''
    pid = request.POST['pid']
    try:
        pid = int(pid)
    except ValueError:
        return render_error(request, "sorry.. some error occured")

    try:
        uname = User_Blog.objects.get(user_name=request.session['user_name'])

        bid = Blog_Post.objects.get(blog_id=pid)
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")

    post = Post_Like(blog_id=bid, user_name=uname)

    post.save()
    data = {}
    return JsonResponse(data)


@p_decorate
def editpost(request):
    ''' updates the blog post'''
    pid = request.POST['blogid']
    try:
        pid = int(pid)
    except ValueError:
        return render_error(request, "sorry.. some error occured")

    s = (request.POST['subject']).strip()
    c = (request.POST['content']).strip()
    if checkArguments(s, c):
        return render_error(request, "Please enter valid values for the post")
    try:
        blog = Blog_Post.objects.get(blog_id=pid)
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")

    blog.subject = s
    blog.content = c
    blog.updated_at = timezone.now()
    blog.save()
    return blog_render(request)


@p_decorate
def editcomment(request):
    ''' handles edit comment '''

    s = (request.POST['comment']).strip()
    if checkArguments(s):
        return render_error(request, "Please enter valid values for the comment")

    c = request.POST['commentid']
    try:
        uname = User_Blog.objects.get(user_name=request.session['user_name'])
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")

    try:
        com = Comment.objects.get(comment_id=c, user_name=uname)
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")
    com.comment = s
    com.save()
    return blog_render(request)


@p_decorate
def deletepost(request):
    ''' deletes the post'''
    pid = request.POST['pid']
    try:
        pid = int(pid)
    except ValueError:
        return render_error(request, "sorry.. some error occured")
    try:
        if pid:
            pid = int(pid)
    except ValueError:
        return render_error(request, "sorry.. some error occured")

    try:
        uname = User_Blog.objects.get(user_name=request.session['user_name'])
        bid = Blog_Post.objects.get(blog_id=pid, user_name=uname)
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")
    bid.delete()

    data = {}
    return JsonResponse(data)


@p_decorate
def deletecomment(request):
    ''' deletes the comment'''
    pid = request.POST['pid']
    try:
        pid = int(pid)
    except ValueError:
        return render_error(request, "sorry.. some error occured")

    try:
        uname = User_Blog.objects.get(user_name=request.session['user_name'])
        bid = Comment.objects.get(comment_id=pid, user_name=uname)
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")

    bid.delete()
    data = {}
    return JsonResponse(data)


@p_decorate
def addcomment(request):
    ''' adds  new comment'''

    s = (request.POST['comment']).strip()
    c = request.POST['commentid'].strip()
    if checkArguments(s, c):
        return render_error(request, "Please enter valid values for the comment")
    try:
        uname = User_Blog.objects.get(user_name=request.session['user_name'])
        blog = Blog_Post.objects.get(blog_id=c)
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")

    com = Comment(comment=s, blog_id=blog, user_name=uname)
    com.save()
    return blog_render(request)


@p_decorate
def addpost(request):
    ''' adds  new blog post'''

    s = (request.POST['subject']).strip()
    c = (request.POST['content']).strip()
    if checkArguments(s, c):
        return render_error(request, "Please enter valid values for the post")
    try:
        uname = User_Blog.objects.get(user_name=request.session['user_name'])
    except ObjectDoesNotExist:
        return render_error(request, "sorry.. some error occured")

    temp = Blog_Post(subject=s, content=c, user_name=uname)
    temp.save()
    return blog_render(request)


def blog_render(request):
    blog = blog_list_values()
    return render(request, 'user_blog/application_success_page.html',
                  {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})


def checkArguments(*args):
    ''' checks if arguments are none or empty.. '''
    check = False

    for i in args:
        if i is None or not i:
            check = True
    return check


def render_error(request, error_message):
    ''' renders blog with error message'''
    blog = blog_list_values()
    messages.add_message(request, messages.ERROR, error_message)
    return render(request, 'user_blog/application_success_page.html',
                  {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})
