"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

import boards.views as boards_views
import notifications.views as notifications_views
import search.views as search_views
import subjects.views as subjects_views
import users.views as users_views
from subjects.sitemaps import SubjectSitemap
from messenger.urls import *

sitemaps = {
    'subjects': SubjectSitemap,
}

urlpatterns = [
    

    re_path(r'^home/$',login_required(subjects_views.HomePageView.as_view()), name='home'),
    re_path(r'^$',users_views.user_login,name='login'),
    re_path(r'^s/(?P<board>[-\w]+)/(?P<subject>[-\w]+)/$',
        subjects_views.subject_detail,
        name='subject_detail'),
    re_path(r'^b/$',boards_views.BoardsPageView.as_view(), name='view_all_boards'),
    re_path(r'^b/(?P<board>[-\w]+)/$',
        boards_views.BoardPageView.as_view(),
        name='board'),
    
    re_path(r'^b/(?P<board>[-\w]+)/edit_board_cover/$',
        boards_views.edit_board_cover,
        name='edit_board_cover'),
    re_path(r'^b/(?P<board>[-\w]+)/subscription/$',
        boards_views.subscribe,
        name='subscribe'),
    re_path(r'^b/(?P<subject>[-\w]+)/like/$',
        subjects_views.like_subject,
        name='like'),
    re_path(r'^u/(?P<username>[\w.@+-]+)/subscriptions/$', boards_views.UserSubscriptionListView.as_view(),
        name='user_subscription_list'),
    re_path(r'^u/(?P<username>[\w.@+-]+)/boards/$', boards_views.UserCreatedBoardsPageView.as_view(),
        name='user_created_boards'),
    re_path(r'^new_post/$',subjects_views.new_subject, name='new_subject'),
    re_path(r'^edit_subject/(?P<subject>[-\w]+)/$', subjects_views.edit_subject, name='edit_subject'),
    re_path(r'^new_board/$',boards_views.new_board, name='new_board'),

    # user profiles
    re_path(r'^u/$', users_views.UsersPageView.as_view(), name='view_all_users'),
    re_path(r'^u/following/$', users_views.FollowingPageView.as_view(), name='view_following'),
    re_path(r'^u/followers/$', users_views.FollowersPageView.as_view(), name='view_all_followers'),
    re_path(r'^u/(?P<username>[\w.@+-]+)/$', users_views.UserProfilePageView.as_view(), name='user_profile'),
    re_path(r'^u/follow_user/(?P<user_id>\d+)/$',
        users_views.follow_user,
        name='follow_user'),
    re_path(r'^u/send_message_request/(?P<user_id>\d+)/$',
        users_views.send_message_request,
        name='send_message_request'),
    re_path(r'^u/accept_message_request/(?P<user_id>\d+)/$',
        users_views.accept_message_request,
        name='accept_message_request'),
    re_path(r'^u/friends/all/$', users_views.all_friends, name='all_friends'),
    re_path(r'^u/friends/requests/$', users_views.all_message_requests, name='all_message_requests'),
    re_path(r'^activities/$', notifications_views.ActivitiesPageView.as_view(), name='activities'),
    re_path(r'^activities/check/$', notifications_views.check_activities, name='check_activities'),

    # login / logout urls
    re_path(r'^login/$',users_views.user_login,name='login'),
    re_path(r'^logout/$',users_views.user_logout,
            name='logout'),
    re_path(r'^logout-then-login/$',
            auth_views.logout_then_login,
            name='logout_then_login'),

    # password change re_paths
    re_path(r'^password_change/$',
        auth_views.PasswordChangeView.as_view(),
        name='password_change'),
    re_path(r'^password-change/done/$',
        auth_views.PasswordChangeDoneView.as_view(),
        name='password_change_done'),


    # user registration
    re_path(r'^signup/$',
        users_views.register_user,
        name='signup'),

    # verify username availability in database via ajax request
    re_path(r'^signup/check_username/$', users_views.check_username, name='check_username'),

    # profile edit
    re_path(r'^profile_edit/$', users_views.profile_edit,
        name='profile_edit'),
    re_path(r'^picture_change/$', users_views.change_picture,
        name='picture_change'),

    # search
    re_path(r'^search/$',search_views.search, name='search'),
    re_path(r'^board_search/(?P<board_slug>[-\w]+)/$',search_views.search, name='board_search'),

    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
    
    re_path(r'^messages/', include('messenger.urls')),

    path('', include('pwa.urls'))

]

if True:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

