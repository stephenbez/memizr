from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from spacedRepetition.flashcards.models import Card, get_days_so_far
from spacedRepetition.flashcards.models import get_days_so_far

import random
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render_to_response('home.html', { 'active_tab' : 'home' }, context_instance=RequestContext(request))

def gradeDescriptions(request):
    return render_to_response('gradeDescriptions.html', context_instance=RequestContext(request))

@login_required
def review(request):
    current_day = get_days_so_far() 
    results = Card.objects.filter(next_rep_day__lte = current_day, username = request.user.username)
    if len(results) == 0:
        card = None
    else:
        result_list = list(results)
        random.shuffle(result_list)
        card = result_list[0]
    
    return render_to_response('review.html', { 'card' : card, 'current_day' : get_days_so_far(), 'active_tab' : 'review' },
        context_instance=RequestContext(request))

@login_required
def edit(request):
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
        'active_tab' : 'edit', 'edited' : edited, 'deleted' : deleted }, context_instance=RequestContext(request))

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
    else:
        c = Card.objects.get(pk=card_id, username = request.user.username)
        c.delete()

    return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.edit') + "?deleted=true")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/home/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", {'form': form,}, context_instance=RequestContext(request))

