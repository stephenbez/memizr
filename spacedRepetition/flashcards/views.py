from django.shortcuts import render_to_response
from spacedRepetition.flashcards.models import Card, get_days_so_far
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.core.urlresolvers import reverse
from spacedRepetition.flashcards.models import get_days_so_far
import random

def home(request):
    return render_to_response('home.html', { 'active_tab' : 'home' })

def gradeDescriptions(request):
    return render_to_response('gradeDescriptions.html')

def review(request):
    current_day = get_days_so_far() 
    results = Card.objects.filter(next_rep_day__lte = current_day)
    if len(results) == 0:
        card = None
    else:
        result_list = list(results)
        random.shuffle(result_list)
        card = result_list[0]
    
    return render_to_response('review.html', { 'card' : card, 'current_day' : get_days_so_far(), 'active_tab' : 'review' })

def edit(request):
    cards = Card.objects.all()
    return render_to_response('edit.html', { 'cards' : cards, 'active_tab' : 'edit' })

def editCard(request, card_id):
    c = Card.objects.get(pk=card_id)
    return render_to_response('editCard.html', { 'card' : c, 'active_tab' : 'edit' })

def editCardSubmit(request):
    try:
        q = request.POST['question']
        a = request.POST['answer']
        card_id = request.POST['cardId']
    except KeyError:
        return edit(request)
    else:
        c = Card.objects.get(pk=card_id)
        c.question = q
        c.answer = a
        c.save()
    return edit(request)


def add(request):
    try:
        success = request.GET['success']
    except KeyError:
        return render_to_response('add.html', { 'active_tab' : 'add'})
    else:    
        return render_to_response('add.html', { 'active_tab' : 'add', 'success' : True })

def addCard(request):
    try:
        q = request.POST['question']
        a = request.POST['answer']
    except KeyError:
        return review(request)
    else:
        c = Card(question=q, answer=a)
        c.save()
    return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.add') + "?success=true")

def grade(request):
    try:
        card_id = request.POST['cardId']
        new_grade = int(request.POST['grade'])
    except KeyError:
        return review(request)
    else:
        c = Card.objects.get(pk=card_id)
        c.process_answer(new_grade)
        c.save()

        return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.review'))

def delete(request):
    try:
        card_id = request.POST['cardId']
    except KeyError:
        return edit(request)
    else:
        c = Card.objects.get(pk=card_id)
        c.delete()

    return HttpResponseRedirect(reverse('spacedRepetition.flashcards.views.edit'))
