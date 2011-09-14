from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from spacedRepetition.flashcards.models import Card, get_days_so_far
from spacedRepetition.flashcards.models import get_days_so_far
from spacedRepetition.flashcards.forms import UserCreationFormWithEmail

import random
import logging
import json

logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('home.html', { 'active_tab' : 'home' }, context_instance=RequestContext(request))

def gradeDescriptions(request):
    return render_to_response('gradeDescriptions.html', context_instance=RequestContext(request))

@login_required
def review(request):
    current_day = get_days_so_far() 
    results = Card.objects.filter(next_rep_day__lte = current_day, username = request.user.username)
    num_cards_for_today = len(results)
    if num_cards_for_today == 0:
        all_cards = Card.objects.filter(username = request.user.username).order_by('next_rep_day')

        if len(all_cards) == 0:
            return render_to_response('review.html', { 'active_tab' : 'review', 'user_has_no_cards' : True }, context_instance=RequestContext(request))

        next_rep_day = Card.objects.filter(username = request.user.username). \
                            order_by('next_rep_day')[0].next_rep_day
        days_until_next_rep = next_rep_day - current_day
        return render_to_response('review.html', { 'active_tab' : 'review', 'days_until_next_rep' : days_until_next_rep }, context_instance=RequestContext(request))
    else:
        result_list = list(results)
        random.shuffle(result_list)
        card = result_list[0]
    
    return render_to_response('review.html', { 'card' : card, 'active_tab' : 'review', 'num_cards_for_today' : num_cards_for_today},
        context_instance=RequestContext(request))

@login_required
def edit(request, num_cards_imported=0):
    cards = Card.objects.filter(username = request.user.username).order_by('id')
    
    edited = False
    deleted = False
    
    try:
        edited = request.GET['edited']
    except KeyError:
        pass

    try:
        deleted = request.GET['deleted']
    except KeyError:
        pass

    return render_to_response('edit.html', { 'cards' : cards, 
        'active_tab' : 'edit', 'edited' : edited, 'deleted' : deleted, 'num_cards_imported' : num_cards_imported }, context_instance=RequestContext(request))

@login_required
def editCard(request, card_id):
    c = Card.objects.get(pk=card_id, username = request.user.username)
    return render_to_response('editCard.html', { 'card' : c, 'active_tab' : 'edit' }, context_instance=RequestContext(request))

@login_required
def editCardSubmit(request):
    try:
        q = request.POST['question']
        a = request.POST['answer']
        card_id = request.POST['cardId']
    except KeyError:
        return edit(request)
    else:
        c = Card.objects.get(pk=card_id, username = request.user.username)
        c.question = q
        c.answer = a
        c.save()
    return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.edit') + "?edited=true")

@login_required
def add(request):
    added = False
    try:
        added = request.GET['added']
    except KeyError:
        pass
    
    return render_to_response('add.html', { 'active_tab' : 'add', 'added' : added }, context_instance=RequestContext(request))

@login_required
def addCard(request):
    try:
        q = request.POST['question']
        a = request.POST['answer']
    except KeyError:
        return review(request)
    else:
        c = Card(question=q, answer=a, username = request.user.username)
        c.save()
    return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.add') + "?added=true")

@login_required
def grade(request):
    try:
        card_id = request.POST['cardId']
        new_grade = int(request.POST['grade'])
    except KeyError:
        return review(request)
    else:
        c = Card.objects.get(pk=card_id, username = request.user.username)
        logger.debug("Before grading: " + c.__unicode__())    
        c.process_answer(new_grade)
        c.save()
        logger.debug("After grading: " + c.__unicode__())

        return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.review'))

@login_required
def delete(request):
    try:
        card_id = request.POST['cardId']
    except KeyError:
        return edit(request)
   
    from_review = False
    try:
        from_review = request.POST['fromReview']
    except KeyError:
        pass
 
    c = Card.objects.get(pk=card_id, username = request.user.username)
    c.delete()

    if from_review:
        return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.review'))
    else:
        return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.edit') + "?deleted=true")

@login_required
def export(request):
    cards = Card.objects.filter(username = request.user.username).order_by('id')

    dict_card_list = []
    for card in cards:
        d = {"question" : card.question, "answer" : card.answer}
        dict_card_list.append(d)

    result = json.dumps(dict_card_list)
 
    response = HttpResponse(result, mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=cards.csv'
    return response

@login_required
def import_cards(request):
    return render_to_response('import.html', { 'active_tab' : 'import' }, context_instance=RequestContext(request))

@login_required
def upload(request):
    if request.method == 'POST':
        file = request.FILES['file']
        num_cards_imported = handle_uploaded_file(file, request.user.username)
        return edit(request, num_cards_imported)
    else:
        return import_cards(request)

def handle_uploaded_file(f, username):
    j =  f.read()
    
    try:
        cards = json.loads(j)
    except ValueError:
        return 0    

    for c in cards:
        q = c["question"]
        a = c["answer"]

        c = Card(question=q, answer=a, username = username) 
        c.save()

    return len(cards)

def register(request):
    if request.method == 'POST':
        form = UserCreationFormWithEmail(request.POST)
        if form.is_valid():
            new_user = form.save()
            user = authenticate(username=new_user.username, password=form.cleaned_data["password1"])
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = UserCreationFormWithEmail()
    return render_to_response("registration/register.html", {'form': form,}, context_instance=RequestContext(request))

