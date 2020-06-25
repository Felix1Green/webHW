from django import forms
from django.core.files.storage import FileSystemStorage
from app import models
from django.contrib.auth.models import User
import re


def save_avatar(request):
    avatar = request['avatar']
    fs = FileSystemStorage()
    filename = fs.save(avatar.name, avatar)
    image_url = fs.url(filename)
    return image_url


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8 or len(self.cleaned_data['username']) > 15:
            raise forms.ValidationError("The login or password is incorrect")
        return password


# class SignupForm(forms.ModelForm):
#     email = forms.EmailField()
#
#     class Meta:
#         model = models.Profile
#         fields = ['avatar', 'nickname']
#
#     def __init__(self, *args, user=None, **kwargs):
#         super().__init__(args, kwargs)
#         self.user = user
#
#     def clean_nickname(self):
#         username = self.cleaned_data['nickname']
#         if ' ' in username:
#             raise forms.ValidationError('Никнейм содержит пробелы')
#         return username
#
#     def save(self, commit=True):
#         profile = models.Profile(**self.cleaned_data)
#         profile.user = self.user
#         profile.user.email = self.cleaned_data['email']
#         if self.cleaned_data['avatar']:
#             image_url = save_avatar(self.cleaned_data)
#             profile.avatar = image_url
#         if commit:
#             profile.save()
#         return profile


class SignupForm(forms.Form):
    username = forms.CharField(max_length=15)
    nickname = forms.CharField(max_length=15)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    Repeat_Password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)

    def clean(self):
        if len(self.cleaned_data['password']) < 8:
            raise forms.ValidationError("The password is incorrect")
        if self.cleaned_data['Repeat_Password'] != self.cleaned_data['password']:
            raise forms.ValidationError("Repeated password doesnt match")
        return

    def save(self):
        nickname = self.cleaned_data['username']
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        try:
            user = User.objects.create(username=nickname, email=email)
        except:
            return None
        user.set_password(password)
        user.save()
        profile = models.Profile.objects.create(user=user, nickname=nickname)
        if self.cleaned_data['avatar']:
            avatar_url = save_avatar(self.cleaned_data)
            profile.avatar = avatar_url
        profile.save()
        print(user)
        return user


class TagsFieldWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.TextInput(attrs={'placeholder': 'Введите тэги через запятую'})]
        super(TagsFieldWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value]
        else:
            return ['']


class TagsField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = [forms.CharField()]
        super(TagsField, self).__init__(fields, widget=TagsFieldWidget, *args, **kwargs)

    def compress(self, values):
        return values[0]


class QuestionForm(forms.ModelForm):
    tags = TagsField(label="Tags")
    class Meta:
        model = models.Question
        fields = ["title", "text"]
        widgets = {
            'title': forms.TextInput,
            'text': forms.Textarea
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст вопроса',
            'tags': 'Имена тегов через запятую'
        }

    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        lst = tags.split(', ')
        if len(lst) > 3:
            raise forms.ValidationError("Некорректное количество тэгов")
        for tag in lst:
            print(tag)
            if ' ' in tag:
                raise forms.ValidationError("Пробел в названии тега")
            if re.match(r'^[A-Za-z1-9]{1, }$', tag):
                raise forms.ValidationError("Неправильные теги")
        return lst

    def save(self, commit=True):
        question = models.Question(title=self.cleaned_data['title'], text=self.cleaned_data['text'])
        question.Author = self.author
        if commit:
            question.save()
            for i in self.cleaned_data['tags']:
                tag = models.Tag.objects.get_or_create(title=i)[0]
                tag.Questions.add(question)
                tag.save()
            question.save()
        return question


# class QuestionForm(forms.Form):
#     title = forms.CharField(max_length=15)
#     Text = forms.CharField(widget=forms.Textarea)
#     Tags = forms.CharField(max_length=50)
#
#     def clean(self):
#         tags = self.cleaned_data.get('Tags')
#         if len(tags) < 1:
#             raise forms.ValidationError("No tags")
#
#     def save(self,user):
#         tags = list()
#         try:
#             tags = self.cleaned_data['Tags'].split(', ')
#         except Exception as e:
#             tags = ["test"]
#         q = models.Question.objects.create(Author=user, title=self.cleaned_data['title'],
#                                            text=self.cleaned_data['Text'])
#         for i in tags:
#             tag = models.Tag.objects.get_or_create(title=i)[0]
#             tag.Questions.add(q)
#             tag.save()
#         return q


class User_Settings(forms.ModelForm):
    email = forms.EmailField(required=False)
    nickname = forms.CharField(label="Никнейм",required=False)
    avatar = forms.ImageField(label="Аватар", required=False)

    class Meta:
        model = models.Profile
        fields = ['nickname', 'avatar']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_nickname(self):
        username = self.cleaned_data['nickname']
        if ' ' in username:
            raise forms.ValidationError('Никнейм содержит пробелы')
        return username

    def save(self, commit=True):
        profile = self.user.profile
        if self.cleaned_data['nickname']:
            profile.nickname = self.cleaned_data['nickname']
        if self.cleaned_data['email']:
            profile.user.email = self.cleaned_data['email']
        if self.cleaned_data['avatar']:
            image_url = save_avatar(self.cleaned_data)
            profile.avatar = image_url
        if commit:
            profile.save()
        return profile


# class User_Settings(forms.Form):
#     nickname = forms.CharField(max_length=15, required=False)
#     email = forms.EmailField(required=False)
#     avatar = forms.ImageField(required=False)
#
#     def clean(self):
#         image = self.cleaned_data.get('avatar', False)
#         if image and len(image) > 4 * 1024 * 1024:
#             raise forms.ValidationError("Image file too large ( > 4mb )")
#         return
#
#     def save(self,instance):
#         print(self.cleaned_data)
#         if len(self.cleaned_data['nickname']) > 0:
#             instance.profile.nickname = self.cleaned_data['nickname']
#         if len(self.cleaned_data['email']) > 0:
#             instance.email = self.cleaned_data['email']
#         if self.cleaned_data['avatar']:
#             image_url = save_avatar(self.cleaned_data)
#             instance.profile.avatar = image_url
#         instance.profile.save()
#         instance.save()
#         return instance


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ['text']

    def __init__(self, *args, user=None, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.question = question

    def save(self, commit=True):
        answer = models.Answer(**self.cleaned_data)
        answer.Author = self.user
        answer.Question = self.question
        if commit:
            answer.save()
        return answer

# class AnswerForm(forms.Form):
#     text = forms.CharField(widget=forms.Textarea)
#
#     def clean(self):
#         if len(self.cleaned_data['text']) <1:
#             raise forms.ValidationError("No answer to send")
#         return
#
#     def save(self,question_object,user):
#         answer = models.Answer.objects.create(text=self.cleaned_data['text'], Question=question_object, Author=user)
#         answer.save()
#         return answer.id
