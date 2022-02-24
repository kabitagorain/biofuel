from django.conf import settings
from django.db import models
from django.forms import ValidationError
# from accounts.models import User
from django.urls import reverse

def get_common_status(value):
    try:
        common_status_total = DifinedLabel.objects.filter(common_status = True).count()
        common_status = DifinedLabel.objects.get(common_status = True)
    except Exception:
        common_status_total = 0

    if common_status_total == int(1) and value == 1:
        raise ValidationError('A common status named "' + common_status.name +'" already exist! Only One common status allowed!')
    else:
        pass

class DifinedLabel(models.Model): 
    name = models.CharField(max_length=252)
    label = models.CharField(max_length=252, default='')
    adj = models.CharField(max_length=252, default='')
    common_status = models.BooleanField(default=False, validators=[get_common_status])

    sort_order = models.CharField(max_length=3, default=0)

    def __str__(self):
        return self.name

class Question(models.Model):
    name = models.CharField(max_length=252)
    sort_order = models.IntegerField(default=1)
    description = models.TextField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return  '(' + str(self.sort_order) +') ' + self.name
    
    def get_absolute_url(self):        
        return reverse('home:questions_details', args=[str(self.pk)])
    @property
    def labels(self):
        return Label.objects.filter(question = self)
    
    

class Label(models.Model):
    name = models.ForeignKey(DifinedLabel, on_delete=models.PROTECT, related_name='dlabels', limit_choices_to={'common_status': False})
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='questions')
    value = models.CharField(max_length=1, default=0)

    def __str__(self):
        return self.name.name

class Option(models.Model):
    name = models.CharField(max_length=252)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question')
    next_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null = True, blank = True, related_name='next_question', limit_choices_to={'is_active': True})
    statement = models.TextField(null = True, blank = True,)
    next_step = models.TextField(null = True, blank = True,)
    overall = models.CharField(max_length=1, default=0)
    positive = models.CharField(max_length=1, default=0)
    dont_know = models.BooleanField(default=False)

    def __str__(self):
        return self.name + '(' + str(self.question.sort_order) + ')'

class LogicalString(models.Model):
    options = models.ManyToManyField(Option)
    text = models.TextField(null = True, blank = True,)
    overall = models.CharField(max_length=1, default=0)
    positive = models.CharField(max_length=1, default=0)

    def __str__(self):
        return self.text

class Lslabel(models.Model):
    name = models.ForeignKey(DifinedLabel, on_delete=models.PROTECT, related_name='ls_dlabels', limit_choices_to={'common_status': False})
    logical_string = models.ForeignKey(LogicalString, on_delete=models.CASCADE, related_name='logical_strings')
    value = models.CharField(max_length=1, default=0)

    def __str__(self):
        return self.name.name




class Biofuel(models.Model):
    name = models.CharField(max_length=252)
    

    def __str__(self):
        return self.name

class Evaluator(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user')
    name = models.CharField(max_length=252)
    email = models.EmailField()
    phone = models.CharField(max_length=16)
    orgonization = models.CharField(max_length=252)
    biofuel = models.ForeignKey(Biofuel, on_delete=models.SET_NULL, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    report_genarated = models.BooleanField(default=False)
    

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('evaluation:report', args=[str(self.id)])

class Evaluation(models.Model):
    evaluator = models.ForeignKey(Evaluator, on_delete=models.RESTRICT, related_name='eva_evaluator')
    option = models.ForeignKey(Option, on_delete=models.RESTRICT, related_name='eva_option')
    question = models.ForeignKey(Question, on_delete=models.RESTRICT,null=True, blank=True, related_name='eva_question')
    

    def __str__(self):
        return self.evaluator.name

    @property
    def get_question_comment(self):
        eva_comment = EvaComments.objects.filter(question = self.question, evaluator = self.evaluator)
        return eva_comment


class EvaComments(models.Model):
    evaluator = models.ForeignKey(Evaluator, on_delete=models.RESTRICT, related_name='coment_evaluator')
    question = models.ForeignKey(Question, on_delete=models.RESTRICT, related_name='comment_question')
    comments = models.TextField(max_length=600)

    def __str__(self):
        return self.comments


class EvaLabel(models.Model):
    label = models.ForeignKey(DifinedLabel, on_delete=models.PROTECT, related_name='labels')
    evaluator = models.ForeignKey(Evaluator, on_delete=models.RESTRICT, related_name='evaluators')
    sort_order = models.CharField(max_length=3, default=0)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.label.name

class EvaLebelStatement(models.Model):
    evalebel = models.ForeignKey(EvaLabel, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, null=True, blank=True)
    option_id = models.CharField(max_length=252, null=True, blank=True)
    statement = models.TextField(blank=True, null=True)
    next_step = models.TextField(blank=True, null=True)
    positive = models.CharField(max_length=1, default=0)
    dont_know = models.BooleanField(default=False)
    assesment = models.BooleanField(default=False)
    evaluator = models.ForeignKey(Evaluator, on_delete=models.RESTRICT, related_name='s_evaluators', null=True)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.statement
class OptionSet(models.Model):
    option_list = models.CharField(max_length=252, unique = True)
    text = models.TextField()
    positive = models.CharField(max_length=1, default=0)
    overall = models.CharField(max_length=1, default=0)
    ls_id = models.CharField(max_length=252, default=0)


    def __str__(self):
        return str(self.option_list) + str(self.text)
