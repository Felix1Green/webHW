
from django.contrib import admin
from django.conf.urls.static import static
from askme import settings
from django.urls import path
from app import views

urlpatterns = [
    path("",views.new_filter, name ="main_page"),
    path("question/<int:pk>/",views.question, name = "question"),
    path("new/",views.new_filter,name = "question_new"),
    path("like/<int:pk>/<int:type>/",views.like_setter,name = "like"),
    path("correct_ans/<int:pk>/",views.correct_answer_setter, name ="Correct_ans"),
    path("tag/<slug:slug>/",views.tag_filter, name = "tag_question_list"),
    path("login/",views.Login, name = "login"),
    path("auth/",views.Auth, name= "auth"),
    path("profile/edit/",views.User_settings, name = "user_settings"),
    path("ask/",views.Question_form, name = "question_form"),
    path("popular/",views.popular_filter,name="popular_filter"),
    path("logout/",views.Logout,name="logout")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)