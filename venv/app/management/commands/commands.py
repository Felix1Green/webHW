from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app import models
import random



class Command(BaseCommand):
    help = "Filling the Question model in DataBase"

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='+', type=int, help='num of objects')
    def handle(self,*args,**kwargs):
        cnt = (kwargs['count'][0])
        for i in range(cnt):
            try:
                user = User()
                user.username = "{}daddd".format(i)
                user.save()
                Profile = models.Profile(user=user)
                Profile.save()
                for j in range(random.randint(0,100)%cnt):
                    Question = models.Question(Author=Profile,title="{}question".format(i),text="some unique text asndoisndnoad asd instagram pam pam ?")
                    Question.save()
            except:
                continue
        Question = models.Question.objects.all()
        for y in range(random.randint(0,100) % cnt):
            try:
                user_liked = User()
                user_liked.username = "{}dddd.user".format(y)
                user_liked.save()
                Profile_liked = models.Profile(user=user_liked)
                Profile_liked.save()
                like = models.Like(Question=Question[y],Author=Profile_liked)
                answer = models.Answer(text="{}aaadnswer".format(y),Question=Question[y],Author=Profile_liked)
                like.save()
                answer.save()
            except:
                continue
        for y in range(random.randint(0,100) % cnt):
            try:
                Tag = models.Tag(title="{}ddtag".format(y))
                Tag.save()
                Tag.Questions.add(Question[y])
                Tag.save()
            except:
                continue
