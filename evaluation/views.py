from django.shortcuts import render
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from .forms import *
from .models import *
from accounts.models import UserType
from django.contrib import messages
from django.urls import reverse
from django_xhtml2pdf.utils import generate_pdf
from django.db.models import Count
from . helper import label_assesment_for_donot_know, label_assesment_for_positive, overall_assesment_for_donot_know, overall_assesment_for_positive, get_current_evaluator
import random
from django.contrib.auth.decorators import login_required
from accounts.decorators import expert_required, producer_required, consumer_required
from gfvp import null_session
from django.core.exceptions import PermissionDenied


# def get_current_evaluator(request):
#     evaluator = Evaluator.objects.get(email = request.session['evaluator'])
#     return evaluator


@login_required
@producer_required
def eva_index(request):  
    
    null_session(request)
    try:
        session_evaluator = Evaluator.objects.get(id = request.session['evaluator'])
    except:
        session_evaluator = False

    if  (session_evaluator is False) or ('question' not in request.session):
        '''Catch Primary Data'''
        if request.method == "POST": 
            form = EvaluatorForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                email = form.cleaned_data['email'] 
                phone = form.cleaned_data['phone']
                orgonization = form.cleaned_data['orgonization']
                biofuel = form.cleaned_data['biofuel']

                new_evaluator = Evaluator(creator = request.user, name = name, email = email, phone = phone, orgonization = orgonization, biofuel = biofuel )
                new_evaluator.save()

                request.session['evaluator'] = new_evaluator.id

                first_question = Question.objects.filter(is_active=True).order_by('sort_order').first()
                '''note next question to ask'''
                request.session['question'] = first_question.id
                request.session['total_question'] = 0



                defined_label = DifinedLabel.objects.all()


                for dl in defined_label:
                    new_evalabel = EvaLabel(label = dl, evaluator = get_current_evaluator(request), sort_order=dl.sort_order)
                    new_evalabel.save()
                request.session['option'] = ''

                return HttpResponseRedirect(reverse('evaluation:evaluation'))

        else:
            if request.user.is_authenticated:
                type = UserType.objects.get(slug = request.user.type.slug )
                name = request.user.get_full_name
                email = request.user.email
                phone = request.user.phone
                orgonization = request.user.orgonization
            else:
                type = UserType.objects.get(slug = request.session['interested_in'] )
                name = ''
                email = ''
                phone = ''
                orgonization = ''
            initial_dict = {
            "type" : type,
            "email" : email,
            "phone":phone,
            "orgonization":orgonization,
            "name":name
            }
            form = EvaluatorForm(initial = initial_dict)
        total_ques = Question.objects.all().count()
        box_timing = f"Depending on how many answers you provide, the self assessment will take anywhere from {round(total_ques/10)} to {round(total_ques/3)} minutes. At the end of the assessment, a PDF report will be provided, which can be retrieved via the Dashboard at a later stage."
        
        
        
        
        

        context = {
        'form': form,
        'evaluator': False,
        'box_timing': box_timing
        
        
        }
        return render(request, 'evaluation/index.html', context = context)
    else:
        '''Catch Answers'''
        '''if option yet not submited for the question comments field should not active'''
        if 'active' not in request.session:
            request.session['active'] = ''
            
        question = Question.objects.get(id = request.session['question'])
        options = Option.objects.filter(question = question)
        evaluator_data = get_current_evaluator(request)
        total_ques = Question.objects.all().count() - request.session['total_question']
        try:
            selected_option = Option.objects.get(id = request.session['option'])
        except Exception as e:
            selected_option = ''
        eva_lebels = EvaLabel.objects.filter(evaluator = evaluator_data).order_by('sort_order')
        timing_text = f"Depending on how you are answering the questions may take {round(total_ques/6)} to {round(total_ques/2)} min."
        
        
        
        
        
        context = {
            'question': question,
            'optns': options,
            'evaluator': True,
            'evaluator_data': evaluator_data,
            'eva_lebels': eva_lebels,
            'selected_option': selected_option,
            'acive': request.session['active'],
            'total_question': request.session['total_question'],
            'qualified_rang' : 0,
            'timing_text': timing_text,
            
            

        }
        return render(request, 'evaluation/index.html', context = context)

@login_required
@producer_required
def option_add(request):
    null_session(request) 
    if request.method == 'POST':
        try:
            option_id = request.POST['option_id']
        except:
            messages.warning(request, 'Please select an option to continue!')
            return HttpResponseRedirect(reverse('evaluation:evaluation'))

        comment = request.POST['comment']
        question = Question.objects.get(id = request.session['question'])
        # evaluator = Evaluator.objects.get(email = request.session['evaluator'])
        new_eva_comment = EvaComments(evaluator = get_current_evaluator(request), question = question, comments = comment)
        new_eva_comment.save()

        request.session['option'] = option_id
        '''Field set to be disabled'''
        request.session['active'] = 'disabled'


        return HttpResponseRedirect(reverse('evaluation:evaluation'))
    

    

def Genarator(request, selected_option):
    question = selected_option.question
    set_labels = Label.objects.filter(question =  question, value = 1)

    for set_label in set_labels:
        defined_label = DifinedLabel.objects.get(name = set_label.name)
        eva_label = EvaLabel.objects.get(label = defined_label, evaluator = get_current_evaluator(request))
        new_evalebel_statement = EvaLebelStatement(evalebel = eva_label, option_id = selected_option.id, statement = selected_option.statement, next_step = selected_option.next_step, dont_know = selected_option.dont_know, question = selected_option.question, positive = selected_option.positive, evaluator =  get_current_evaluator(request))
        new_evalebel_statement.save()

        EvaLebelStatement.objects.filter(evalebel = eva_label, evaluator = get_current_evaluator(request), assesment = True).delete()

        summery_statement_do_not_know = EvaLebelStatement(evalebel = eva_label, statement = label_assesment_for_donot_know(request, eva_label),  evaluator =  get_current_evaluator(request), assesment = True)
        summery_statement_do_not_know.save()

        summery_statement_positive = EvaLebelStatement(evalebel = eva_label, statement = label_assesment_for_positive(request, eva_label),  evaluator =  get_current_evaluator(request), assesment = True)
        summery_statement_positive.save()

    logical_strings = LogicalString.objects.all()
    logical_options = []

    for logical_string in logical_strings:
        ls_id = logical_string.id
        text = logical_string.text
        overall = logical_string.overall
        positive = logical_string.positive
        sting_options = logical_string.options.all()
        option_list = []
        for s_o in sting_options:
            option_list.append(str(s_o.id))
        logical_options.append(option_list)

        try:
            '''
            edit if any changed
            '''
            option_set = OptionSet.objects.get(option_list = option_list)
            option_set.id = ls_id
            option_set.text = text
            option_set.overall = overall
            option_set.positive = positive
            option_set.save()
        except Exception as e:
            '''
            delete changed to re input
            '''
            lo_except_last = [x for x in logical_options if x != option_list]
            unmatched = [item for item in logical_options if not item in lo_except_last ]
            try:
                for u in unmatched:
                    OptionSet.objects.get(option_list = u).delete()
            except Exception as e:
                pass
            new_option_set = OptionSet(option_list = option_list, text = text, overall = overall , positive = positive, ls_id = ls_id )
            new_option_set.save()

    eva_statement = EvaLebelStatement.objects.filter(evaluator = get_current_evaluator(request))
    es_option_id = set()
    for es in eva_statement:
        es_option_id.add(es.option_id)
    eoi = list(es_option_id)

    defined_common_label = DifinedLabel.objects.get(common_status = True)
    eva_label_common = EvaLabel.objects.get(label = defined_common_label, evaluator = get_current_evaluator(request))

    EvaLebelStatement.objects.filter(evalebel = eva_label_common, evaluator =  get_current_evaluator(request), assesment = True).delete()

    summery_statement_do_not_know = EvaLebelStatement(evalebel = eva_label_common, statement = overall_assesment_for_donot_know(request, eva_label_common),  evaluator =  get_current_evaluator(request), assesment = True)
    summery_statement_do_not_know.save()

    summery_statement_positive = EvaLebelStatement(evalebel = eva_label_common, statement = overall_assesment_for_positive(request, eva_label_common),  evaluator =  get_current_evaluator(request), assesment = True)
    summery_statement_positive.save()

    try:
        logical_statement = OptionSet.objects.get(option_list = eoi)

        ls_labels = Lslabel.objects.filter(logical_string =  logical_statement, value = 1)

        if (eoi in logical_options) and (logical_statement.overall == str(1)):
            new_evalebel_statement_common = EvaLebelStatement(evalebel = eva_label_common, statement = logical_statement.text, evaluator =  get_current_evaluator(request), positive = logical_statement.positive,)
            new_evalebel_statement_common.save()
        elif (eoi in logical_options) and (logical_statement.overall == str(0)):
            for ls_label in ls_labels:
                defined_label = DifinedLabel.objects.get(name = ls_label.name)
                ls_eva_label = EvaLabel.objects.get(label = defined_label, evaluator = get_current_evaluator(request))
                new_evalebel_statement_g = EvaLebelStatement(evalebel = ls_eva_label, statement = logical_statement.text, evaluator =  get_current_evaluator(request), positive = logical_statement.positive,)
                new_evalebel_statement_g.save()
        else:
            pass
    except Exception as e:
        pass

    if selected_option.overall == str(1):
        new_evalebel_statement_common = EvaLebelStatement(evalebel = eva_label_common, statement = selected_option.statement, evaluator =  get_current_evaluator(request))
        new_evalebel_statement_common.save()

@login_required
@producer_required
def option_append(request):
    null_session(request) 
    request.session['active'] = ''
    try:
        selected_option = Option.objects.get(id = request.session['option'])
    except Exception as e:
        messages.warning(request, 'Option didnt Submitted!')
        return HttpResponseRedirect(reverse('evaluation:evaluation'))
    new_evaluation = Evaluation(evaluator = get_current_evaluator(request), option = selected_option, question = Question.objects.get(id = request.session['question'] ) )
    new_evaluation.save()
    

    try:
        next_question_id = selected_option.next_question.id
        request.session['question'] = next_question_id
        '''placement sequence for below line in important'''
        request.session['total_question'] += 1
        request.session['option'] = ''

        Genarator(request, selected_option)
        

        return HttpResponseRedirect(reverse('evaluation:evaluation'))

    except Exception as e:
        
        qualified_ans_rang = 2
        '''if no next question found and sumited ans blw rang will not genarate report'''        
        if request.session['total_question'] < int(qualified_ans_rang):            
            messages.warning(request, 'Need to submit minimum '+ str(qualified_ans_rang) + ' qualified answer! Current is ' + str(request.session['total_question']) + '!')
            return HttpResponseRedirect(reverse('evaluation:evaluation'))      

        try:
            selected_option = Option.objects.get(id = request.session['option'])
        except Exception as e:
            messages.warning(request, 'Option didnt Submitted!')
            return HttpResponseRedirect(reverse('evaluation:evaluation'))
        Genarator(request, selected_option)
        # evaluator =  Evaluator.objects.get(email = request.session['evaluator'])
        evaluator = Evaluator.objects.filter(id = request.session['evaluator'])
        for e in evaluator:
            e.report_genarated = True
            e.save() 
            
        return HttpResponseRedirect(reverse('evaluation:thanks'))
    
        
    
@login_required
@producer_required    
def thanks(request):
    null_session(request)
    try:
        non_genarated_reports = Evaluator.objects.filter(creator = request.user, report_genarated = False).exclude(id = request.session['evaluator'])
        for non_genarated_report in non_genarated_reports:  
            Evaluation.objects.filter(evaluator = non_genarated_report).delete()
            EvaLebelStatement.objects.filter(evaluator = non_genarated_report).delete()
            EvaLabel.objects.filter(evaluator = non_genarated_report).delete()
            EvaComments.objects.filter(evaluator = non_genarated_report).delete()
        non_genarated_report.delete()
    except:
        pass
    
    
    
    if request.session['evaluator'] == '':
        messages.warning(request, 'Please Fillup The Form To Get Started!')
        return HttpResponseRedirect(reverse('evaluation:evaluation'))
    
    ans_ques = EvaLebelStatement.objects.filter(evaluator = get_current_evaluator(request), question__isnull = False, assesment = False).values('question').distinct().count()
    dont_know_ans = EvaLebelStatement.objects.filter(evaluator = get_current_evaluator(request), question__isnull = False, dont_know = 1, assesment = False).values('question').distinct().count()
    pos_ans = EvaLebelStatement.objects.filter(evaluator = get_current_evaluator(request), question__isnull = False, positive = 1, assesment = False).values('question').distinct().count()
    positive_percent = (int(pos_ans) * 100)/int(ans_ques)
    dont_know_percent = (int(dont_know_ans) * 100)/int(ans_ques)
    reports = Evaluator.objects.filter(creator = request.user,  report_genarated = True).order_by('-id')
    
    gretings = 'Thank You! Your supplied data has been recorded!'
    button = reverse('evaluation:report', args=[request.session['evaluator']])
    
    
    context = {
        'gretings': gretings,
        'button': button,
        'ans_ques': ans_ques,
        'dont_know_ans': dont_know_ans,
        'pos_ans': pos_ans,
        'positive_percent': str("%.2f" % positive_percent) + '%',
        'dont_know_percent': str("%.2f" % dont_know_percent) + '%',
        'reports': reports
    }
    
    return render(request, 'evaluation/thanks.html', context = context)


@login_required
def report(request, report_id):
    null_session(request) 
    
    try:
        del request.session['question']
        del request.session['total_question']            
    except KeyError:
        pass

    

    # if request.session['evaluator'] == '':
    #     messages.warning(request, 'Please Fillup The Form To Get Started!')
    #     return HttpResponseRedirect(reverse('evaluation:evaluation'))
    if request.user.is_producer:
        try:
            get_report = Evaluator.objects.get(id = report_id, creator = request.user)
        except:
            raise PermissionDenied            
    elif request.user.is_staff or request.user.is_superuser:
        get_report = Evaluator.objects.get(id = report_id)
    else:
        raise PermissionDenied
    evaluation = Evaluation.objects.filter(evaluator = get_report)
    eva_label = EvaLabel.objects.filter(evaluator = get_report).order_by('sort_order')
    eva_statment = EvaLebelStatement.objects.filter(evaluator = get_report).order_by('pk')

    context = {
        'evaluation': evaluation,
        'current_evaluator': get_report,
        'eva_label': eva_label,
        'eva_statment': eva_statment
    }

    resp = HttpResponse(content_type='application/pdf')
    # resp['Content-Disposition'] = 'attachment; filename=Client_Summary.pdf'
    result = generate_pdf( 'evaluation/report.html', context = context, file_object=resp)
    return result








