from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from .forms import UserForm, ProfileForm, PasswordChangeForm, QuestionForm, OptionForm
from django.contrib import messages
from django.urls import reverse, reverse_lazy
# from django.contrib.auth.forms import PasswordChangeForm
from accounts.decorators import expert_required, producer_required, consumer_required
from accounts.models import User, UserType
from accounts.helper import check_type
from gfvp import null_session
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render, get_object_or_404
from evaluation.models import *
from django.forms import formset_factory, inlineformset_factory
from django.core.exceptions import PermissionDenied
from .helper import users_under_each_label, reports_under_each_biofuel, weeks_results, all_reports, total_reports, typewise_user
from django.db.models import Count, Min


def home(request):
    null_session(request)
    
    user_types = UserType.objects.filter(active = True).order_by('sort_order') 
    context = {
        'user_types': user_types        
    }
    return render(request, 'home/index.html', context = context)


def user_types(request, slug):
    null_session(request)    
    request.session['interested_in'] = slug   
    
    '''Same type of user and admin and staff can have permission to visit this page'''
    
    # check_type(request, slug)
    try:
        curent_user_type_slug = request.user.type.slug
    except:
        curent_user_type_slug = None
        
    
    if slug == curent_user_type_slug:        
        enroll = reverse('evaluation:evaluation')
    else:
        enroll = ''
        
    try:
        user_type = UserType.objects.get(slug = slug)
        users = User.objects.filter(type = user_type)
    except:
        user_type = None
        users = None
    
    context = {
        'user_type': user_type,
        'users': users,
        'enroll': enroll    
    }
    return render(request, 'home/usertypes.html', context = context)
    


@login_required
def dashboard(request):
    null_session(request)    
    day_of_week = [key.split(': ') for key, value in weeks_results(request).items()]
    total_of_day = [value for key, value in weeks_results(request).items()]
    
    # print(typewise_user(request))
    
    
    
    context = {
        'user_of_labels' : users_under_each_label(request),
        'biofuel_records' : reports_under_each_biofuel(request),
        'day_of_week': day_of_week,
        'total_of_day': total_of_day,  
        'total_reports': total_reports(request),      
        'allreports' : all_reports(request),
        'typewise_user' : typewise_user(request)
        
    }
    
    
    
    return render(request, 'home/dashboard.html', context = context)

@login_required
def user_setting(request):   
    null_session(request) 
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request,('Your profile was successfully updated!'))		    
        elif profile_form.is_valid():
            profile_form.save()
            messages.success(request,('Your profile data was successfully updated!'))
        else:
            messages.error(request, 'Invalid form submission.')
            messages.error(request, profile_form.errors)
            messages.error(request, user_form.errors) 
           
        
        return HttpResponseRedirect(reverse('home:user_settings'))
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)    
    
    context = {
        "user":request.user,
        "user_form":user_form,
        "profile_form":profile_form,
        
    }
    return render(request, 'home/settings.html', context = context)

@login_required
def password_change(request):   
    null_session(request) 
    if request.method == "POST":        
        password_form = PasswordChangeForm(user=request.user, data=request.POST)        
        if password_form.is_valid():            
            password_form.save()            
            update_session_auth_hash(request, password_form.user)            
            messages.success(request,('Your password was successfully updated!')) 
        else:
            messages.error(request, 'Invalid form submission.')            
            messages.error(request, password_form.errors)       
        
        return HttpResponseRedirect(reverse('home:change_pass'))
    
    password_form = PasswordChangeForm(request.user)  
    
    context = {
        "user":request.user,        
        "password_form":password_form
    }
    return render(request, 'home/change_pass.html', context = context)



@login_required
@expert_required
def questions(request):  
    null_session(request)
    '''get questions related to the current user'''
    curent_user_expert_in = request.user.experts_in
    label_to_question = Label.objects.filter(name = curent_user_expert_in, value = str(1))
    
    if request.user.is_staff or request.user.is_superuser:
        questions = Question.objects.all()
    else:    
        questions = []
        for q in label_to_question:
            questions.append(q.question)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(questions, 10)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)
    
    context = {
        'questions': questions
        
    }
    
    return render(request, 'home/questions.html', context = context)



@login_required
@expert_required
def questions_details(request, pk):
    null_session(request)
    if 'extra' not in request.session:
        request.session['extra'] = 0
    
    res_question = get_object_or_404(Question, pk = pk)
    
    '''get questions related to the current user'''
    curent_user_expert_in = request.user.experts_in
    
    if request.user.is_staff or request.user.is_superuser:
        question = res_question
    else: 
    
        try:
            label_to_question = Label.objects.get(name = curent_user_expert_in, value = str(1), question = res_question)
            question = label_to_question.question
        except:
            raise PermissionDenied   
    
    
    OptionFormSet = inlineformset_factory(Question, Option, fk_name='question', form = OptionForm, extra= int(request.session['extra']), can_delete=False)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, request.FILES, prefix='questions', instance=question)
        
        option_formset = OptionFormSet(request.POST, request.FILES, prefix='options', instance=question)
        if question_form.is_valid() and option_formset.is_valid():
            question = question_form.save()
            option_formset = OptionFormSet(request.POST, request.FILES, prefix='options', instance=question)
            option_formset.is_valid()
            option_formset.save()
            request.session['extra'] = 0
            if 'add_more' in request.POST or 'extra' in request.POST:
                return HttpResponseRedirect(reverse('home:questions_details', args=[str(pk)]))
            else:
                return HttpResponseRedirect(reverse('home:questions'))
            
        else:
            return render(request, 'home/questions_details.html', {
                'question': question,
                'question_form': question_form,
                'option_formset': option_formset,
            })
            
    else:
        question_form = QuestionForm(prefix='questions', instance=question)
        option_formset = OptionFormSet(prefix='options', instance=question)
    
    
    
    context = {
        'question': question,
        'question_form': question_form,
        'option_formset': option_formset,
        
    }
    return render(request, 'home/questions_details.html', context = context)

@login_required
@expert_required
def new_questions(request):
    null_session(request)
    if 'extra' not in request.session:
        request.session['extra'] = 0
    OptionFormSet = inlineformset_factory(Question, Option, fk_name='question', form = OptionForm, extra= 3, can_delete=False)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, request.FILES, prefix='questions')
        
        option_formset = OptionFormSet(request.POST, request.FILES, prefix='options')
        if question_form.is_valid() and option_formset.is_valid():
            question = question_form.save()
            option_formset = OptionFormSet(request.POST, request.FILES, prefix='options', instance=question)
            option_formset.is_valid()
            option_formset.save()
            request.session['extra'] = 0
            if 'add_more' in request.POST or 'extra' in request.POST:
                return HttpResponseRedirect(reverse('home:questions_details', args=[str(question.id)]))
            else:
                return HttpResponseRedirect(reverse('home:questions'))
            
        else:
            return render(request, 'home/new_question.html', {
                
                'question_form': question_form,
                'option_formset': option_formset,
            })
            
    else:
        question_form = QuestionForm(prefix='questions')
        option_formset = OptionFormSet(prefix='options')
    
    
    
    context = {
        
        'question_form': question_form,
        'option_formset': option_formset,
        
    }
    return render(request, 'home/new_question.html', context = context)

@login_required
def allreports(request):  
    null_session(request)
    
    
    context = {
        'allreports' : all_reports(request),
        
    }
    
    return render(request, 'home/all_reports.html', context = context)


from django.forms import formset_factory
def check_type_to_get_expert(request):
    user_type_id = request.POST.get('type')
    user_type = UserType.objects.get(id = user_type_id)
    request.session['interested_in'] = user_type.slug    
    if user_type.is_expert:
        request.session['hidden'] = ''
    else:
        request.session['hidden']  = "hidden"
    
    return HttpResponseRedirect(reverse_lazy('accounts:signup'))

def add_extra(request, pk):   
    request.session['extra'] += 1
    return HttpResponseRedirect(reverse_lazy('home:questions_details', args=[str(pk)]))
def sub_extra(request, pk):    
    if request.session['extra'] >= 1:
        request.session['extra'] -= 1
    return HttpResponseRedirect(reverse_lazy('home:questions_details', args=[str(pk)]))




