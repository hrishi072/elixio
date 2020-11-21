from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import OperationalError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView

import requests
from django.http import HttpResponseRedirect
from mysite.decorators import ajax_required
from notifications.models import Notification
from utils import image_compression

from .decorators import user_is_subject_author
from .forms import SubjectForm
from .models import Subject




def get_home_subjects():
    try:
        home_subjects = Subject.get_subjects()
    except OperationalError:
        home_subjects = None
    return home_subjects


class HomePageView(ListView):
    model = Subject
    queryset = get_home_subjects()
    paginate_by = 15
    template_name = 'subjects/home.html'
    context_object_name = 'subjects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



def subject_detail(request, board, subject):
    """
    Displays the subject details and handles comment action.
    """
    subject = get_object_or_404(Subject,
                                board__slug=board,
                                slug=subject)
    board = subject.board
    bv = True
    user = request.user
    admins = board.admins.all()


    return render(request, 'subjects/subject.html', {
        'subject': subject,
        'board': board,
        'bv': bv,
        'admins': admins
    })


@login_required
def new_subject(request):
    """
    Displays a form & handle action for creating new subject.
    """
    subject_form = SubjectForm(**{'user': request.user})

    if request.method == 'POST':
        subject_form = SubjectForm(request.POST, request.FILES)
        if subject_form.is_valid():
            new_subject = subject_form.save(commit=False)
            author = request.user
            new_subject.author = author
            new_subject.save()
            new_subject.points.add(author)
            new_subject.save()
            if new_subject.photo:
                image_compression(new_subject.photo.name)

            return HttpResponseRedirect('/u/%s/' % new_subject.author)

    form_filling = True

    return render(request, 'subjects/new_subject.html', {
        'subject_form': subject_form, 'form_filling': form_filling
    })


@login_required
@ajax_required
def like_subject(request, subject):
    """
    Ajax call to like a subject & return status.
    """
    data = dict()
    subject = get_object_or_404(Subject,
                                slug=subject)
    user = request.user
    if subject in user.liked_subjects.all():
        subject.points.remove(user)
        data['is_starred'] = False
    else:
        subject.points.add(user)
        data['is_starred'] = True

    data['total_points'] = subject.points.count()
    return JsonResponse(data)



@login_required
@user_is_subject_author
def edit_subject(request, subject):
    """
    Displays edit form for subjects and handles edit action.
    """
    subject = get_object_or_404(Subject,
                                slug=subject)
    if request.method == 'POST':
        subject_form = SubjectForm(instance=subject,
                                   data=request.POST,
                                   files=request.FILES)
        if subject_form.is_valid():
            subject_form.save()
            return redirect(subject.get_absolute_url())
        else:
            subject_form = SubjectForm(instance=subject)
    else:
        subject_form = SubjectForm(instance=subject)

    form_filling = True

    return render(request, 'subjects/edit_subject.html', {
        'subject_form': subject_form, 'form_filling': form_filling
    })
