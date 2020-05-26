from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from datetime import datetime
from django.contrib.auth.models import AbstractUser


class QuetionManager(models.Manager):
    def new(self):
        return self.order_by('-added_at')

    def popular(self):
        return self.annotate(num_likes=Count(self.votes.avgNumber)).order_by('-num_likes')

    def cnt_ans(self):
            return self.annotate(num_ans=Count('question_ans'))


class AnswerManager(models.Manager):
    def new(self):
        return self.order_by('-added_at')

    def popular(self):
        num_likes = Count(self.votes.avgNumber)
        return self.order_by['-num_likes']


class LikeDislikeManager(models.Manager):
    def likes(self):
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        return self.get_queryset().filter(vote__lt=0)

    def avgNumber(self):
        return self.get_queryset().aggregate(Sum("vote__sum")).get('vote__sum') or 0


class TagsManager(models.Manager):
    def popular(self):
        return self.annotate(num_tags = Count(Tag.Questions)).order_by("-num_tags")[:30]


class ProfileManager(models.Manager):
    def best(self):
        return self.annotate(num_ans = Count("author_ans")).order_by("num_ans")[:15]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
    avatar = models.ImageField(upload_to='upload/')
    nickname = models.CharField(max_length=30)
    objects = ProfileManager()


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTES = (
        (DISLIKE, "Не нравится"),
        (LIKE, "Нравится")
    )
    vote = models.SmallIntegerField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contentObject = GenericForeignKey()

    objects = LikeDislikeManager()

class Question(models.Model):
    Author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    votes = GenericRelation(LikeDislike,related_query_name="Questions")
    title = models.CharField(max_length=30)
    text = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    objects = QuetionManager()

    def get_absolute_url(self):
        return reverse('question', kwargs={"pk": self.id})

    def __unicode__(self):
        return self.title

    def total_answers(self):
        return len(self.question_ans.filter(Question__id = self.id))

    def all_tags(self):
        return list(self.question_tags.filter(Questions = self.id))

    def count_likes(self):
        return len(self.votes.filter(vote=1))

    def count_dislikes(self):
        return len(self.votes.filter(vote=0))


class Tag(models.Model):
    title = models.CharField(max_length=10, unique=True)
    Questions = models.ManyToManyField(Question,related_name="question_tags")
    objects = TagsManager()

    def get_absolute_url(self):
        return reverse('tag_question_list', kwargs={"slug": self.title})

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


class Answer(models.Model):
    text = models.TextField()
    Question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_ans")
    Author = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="author_ans")
    votes = GenericRelation(LikeDislike, related_query_name='Answers')
    added_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    objects = AnswerManager()

    def __unicode__(self):
        return self.text
