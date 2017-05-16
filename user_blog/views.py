from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import User_Blog, Blog_Post, Post_Like
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password


# Create your views here.

def home(request):
    '''
    This API is the landing page of the application
    '''
    if 'user_name' not in request.session and 'name' not in request.session:
        return render(request, 'user_blog/login_signup.html')
    else:
        blog = blog_view()
        return render(request, 'user_blog/application_success_page.html',
                      {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})


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
            blog = blog_view()

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
        blog = blog_view()
        return render(request, 'user_blog/application_success_page.html',
                      {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})
    else:
        blog = blog_view()
        return render(request, 'user_blog/application_success_page.html', {'res': blog})


def blog_view():
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

        resultList.append(res)

    return resultList


def likepost(request, pid):
    ''' Updates the table that stores like and username. When done send a confirmation message which is displayed on client side using jquery'''
    if 'user_name' not in request.session and 'name' not in request.session:
        return render(request, 'user_blog/login_signup.html')
    uname = User_Blog.objects.get(user_name=request.session['user_name'])
    bid = Blog_Post.objects.get(blog_id=pid)

    post = Post_Like(blog_id=bid, user_name=uname)
    post.save()
    data = {}
    return JsonResponse(data)


@csrf_exempt
def editpost(request, pid):
    ''' updates the blog post'''
    if 'user_name' not in request.session and 'name' not in request.session:
        return render(request, 'user_blog/login_signup.html')
    s = request.POST['subject']
    c = request.POST['content']
    blog = Blog_Post.objects.get(blog_id=pid)
    blog.subject = s
    blog.content = c
    blog.updated_at = timezone.now()
    blog.save()
    blog = blog_view()
    return render(request, 'user_blog/application_success_page.html',
                  {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})

def addpost(request):
    ''' adds  new blog post'''
    if 'user_name' not in request.session and 'name' not in request.session:
        return render(request, 'user_blog/login_signup.html')

    s = request.POST['subject']
    c = request.POST['content']
    uname = User_Blog.objects.get(user_name=request.session['user_name'])
    temp = Blog_Post(subject= s, content= c, user_name= uname)
    temp.save()
    blog = blog_view()
    return render(request, 'user_blog/application_success_page.html',
                  {'res': blog, 'name': request.session['name'], 'user_name': request.session['user_name']})
