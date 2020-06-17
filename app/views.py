from django.shortcuts import render
from app import forms
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpRequest,HttpResponseRedirect
from django.http.response import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from app import models


# p = Paginator(object_list, per_page)
# return p


def paginate(object_list, request, per_page=10,ans_id=None):
    p = Paginator(object_list, per_page)
    page = request.GET.get("page") or 1
    response = list()
    if page is None:
        page = 1
        response = p.get_page(page).object_list
    else:
        response = p.get_page(page).object_list
    return response, p.page(page) if ans_id is None else p.page(p.num_pages), p.num_pages


def new_filter(request):
    questions = models.Question.objects.new()
    question_list, current_page, num_pages = paginate(questions,request)
    tags = models.Tag.objects.popular()
    best_users = models.Profile.objects.best()
    print(request.user)
    return render(request, "index.html", {
        'title': "New",
        'user': request.user,
        'tags': tags,
        'Best_Users': best_users,
        'questions': question_list,
        'cur_list': current_page,
        'max_page_number': num_pages
    })


def popular_filter(request):
    questions = models.Question.objects.popular()
    question_list, current_page, num_pages = paginate(questions, request)
    tags = models.Tag.objects.popular()
    best_users = models.Profile.objects.best()
    return render(request, "index.html", {
        'title': "Popular",
        'user': request.user,
        'tags': tags,
        'Best_Users': best_users,
        'questions': question_list,
        'cur_list': current_page,
        'max_page_number': num_pages
    })


def tag_filter(request, slug):
    tag = get_object_or_404(models.Tag, title=slug)
    questions = tag.Questions.all()
    question_list,current_page,num_pages = paginate(questions, request)
    tags = models.Tag.objects.popular()
    best_users = models.Profile.objects.best()
    return render(request, "tag_index.html", {
        'user': request.user,
        'tag': slug,
        'tags': tags,
        'Best_Users': best_users,
        'questions': question_list,
        'cur_list': current_page,
        'max_page_number': num_pages
    })


def question(request, pk):
    question_object = get_object_or_404(models.Question, id=pk)
    ans_id = None
    if request.method == "POST" and request.user.is_authenticated:
        form = forms.AnswerForm(request.POST)
        if form.is_valid():
            ans_id = form.save(question_object, request.user.profile)
    answers = models.Answer.objects.filter(Question=question_object)
    question_tags = models.Tag.objects.filter(Questions__id=question_object.id)[:10]
    tags = models.Tag.objects.popular()
    best_users = models.Profile.objects.best()
    answers_list, current_page, num_pages = paginate(answers, request,ans_id=ans_id)
    print(current_page," asdasdasd")
    form = forms.AnswerForm()
    return render(request, "question.html", {
        'user': request.user,
        'tags': tags,
        'Best_Users': best_users,
        "question": question_object,
        "answers": answers_list,
        "cur_list": current_page,
        "max_page_number": num_pages,
        "question_tags": question_tags,
        "form":form,
        "id":ans_id 
    })


def Login(request):
    redirect_url = request.GET.get("continue")
    print(redirect_url)
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if redirect_url != "None":
                    return HttpResponseRedirect(redirect_url)
                return HttpResponseRedirect("/")
            form.add_error(None, 'Incorrect credentials')
    else:
        form = forms.LoginForm()
    return render(request, "login.html", {
        'form': form,
        'redirect_url': redirect_url
    })


def Auth(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    if request.method == 'POST':
        form = forms.SignupForm(request.POST,request.FILES)
        print("error1")
        if form.is_valid():
            print("error")
            user = form.save()
            if user:
                login(request, user)
                return HttpResponseRedirect("/")
        form.add_error(None, 'Username already exists')
    else:
        form = forms.SignupForm()
    return render(request, "auth.html", {
        'form': form
    })


@login_required(redirect_field_name="continue")
def like_setter(request,pk,type):
    if request.method == "POST":
        return HttpResponse.status_code(405)
    user = request.user
    Question = get_object_or_404(models.Question,id=pk)
    if Question.votes.filter(user=user.profile).exists():
        if Question.votes.filter(vote=type,user=user.profile).exists():
            return HttpResponse.status_code(400)
        vote = models.LikeDislike.objects.get(user=user.profile,object_id = Question.id)
        vote.vote = type
        vote.save()
        return JsonResponse({"Like":len(Question.votes.filter(vote=1)),
                             "Dislike": len(Question.votes.filter(vote=0))})
    Like = models.LikeDislike.objects.create(vote = type,user=user.profile,contentObject =Question)
    Like.save()
    print("ok")
    return JsonResponse({"Like":len(Question.votes.filter(vote=1)),
                             "Dislike": len(Question.votes.filter(vote=0))})


@login_required(redirect_field_name="continue")
def correct_answer_setter(request,pk):
    if request.method == "POST":
        return HttpResponse.status_code(405)
    user = request.user.profile
    Answer = models.Answer.objects.get(id = pk)
    if Answer.Question.Author == user:
        Answer.is_correct = True
        Answer.save()
        return JsonResponse({"Ok":"True"})
    return HttpResponse.status_code(403)


@login_required(redirect_field_name="continue")
def User_settings(request):
    form = forms.User_Settings()
    if request.method == "POST":
        form = forms.User_Settings(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user)
    tags = models.Tag.objects.popular()
    best_users = models.Profile.objects.best()
    return render(request, "user_settings.html", {
        'user': request.user,
        'tags': tags,
        'Best_Users': best_users,
        'form': form
    })


@login_required(redirect_field_name="continue")
def Logout(request):
    logout(request)
    return HttpResponseRedirect("/")


@login_required(redirect_field_name="continue")
def Question_form(request):
    if request.method == "POST":
        form = forms.QuestionForm(request.POST)
        if form.is_valid():
            user = request.user.profile
            q = form.save(user)
            return HttpResponseRedirect(reverse('question',kwargs={"pk":q.id}))
    form = forms.QuestionForm()
    tags = models.Tag.objects.popular()
    best_users = models.Profile.objects.best()
    return render(request, "question_form.html", {
        'form': form,
        'user': request.user,
        'tags': tags,
        'Best_Users': best_users,
    })
