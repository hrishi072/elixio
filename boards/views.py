from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

import requests
from PIL import Image

from mysite.decorators import ajax_required
from subjects.models import Subject
from utils import check_image_extension

from .decorators import user_is_board_admin
from .forms import BoardForm
from .models import Board


class BoardsPageView(ListView):
    model = Board
    queryset = Board.objects.all()
    paginate_by = 20
    template_name = 'boards/view_all_boards.html'
    context_object_name = 'boards'


class BoardPageView(ListView):
    model = Subject
    paginate_by = 20
    template_name = 'boards/board.html'
    context_object_name = 'subjects'

    def get_queryset(self, **kwargs):
        self.board = get_object_or_404(Board,
                                       slug=self.kwargs['board'])
        return self.board.submitted_subjects.filter(active=True)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["bv"] = True
        context["admins"] = self.board.admins.all()
        context["board"] = self.board
        return context


class UserSubscriptionListView(LoginRequiredMixin, ListView):
    model = Board
    paginate_by = 10
    template_name = 'boards/user_subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self, **kwargs):
        user = get_object_or_404(User,
                                 username=self.request.user)
        return user.subscribed_boards.all()


@login_required
@ajax_required
def subscribe(request, board):
    board = get_object_or_404(Board,
                              slug=board)
    user = request.user
    if board in user.subscribed_boards.all():
        board.subscribers.remove(user)
    else:
        board.subscribers.add(user)
    return HttpResponse(board.subscribers.count())


class UserCreatedBoardsPageView(LoginRequiredMixin, ListView):
    model = Board
    paginate_by = 20
    template_name = 'boards/user_created_boards.html'
    context_object_name = 'user_boards'

    def get_queryset(self, **kwargs):
        user = get_object_or_404(User,
                                 username=self.request.user)
        return user.inspected_boards.all()


@login_required
def new_board(request):
    board_form = BoardForm()

    if request.method == 'POST':
        board_form = BoardForm(request.POST, request.FILES)
        if board_form.is_valid():
            new_board = board_form.save()
            new_board.admins.add(request.user)
            new_board.subscribers.add(request.user)
            return redirect(new_board.get_absolute_url())
            
    form_filling = True

    return render(request, 'boards/new_board.html', {
        'board_form': board_form, 'form_filling': form_filling
    })


@login_required
@user_is_board_admin
def edit_board_cover(request, board):
    board = get_object_or_404(Board,
                              slug=board)
    if request.method == 'POST':
        board_cover = request.FILES.get('cover')
        if check_image_extension(board_cover.name):
            board.cover = board_cover
            board.save()
            return redirect('board', board=board.slug)
        else:
            return HttpResponse('Filetype not supported. Supported filetypes are .jpg, .png etc.')
    else:
        form_filling = True
        return render(request, 'boards/edit_board_cover.html', {
            'board': board, 'form_filling': form_filling
        })


