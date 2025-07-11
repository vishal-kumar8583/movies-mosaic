from django.urls import path
from . import views

urlpatterns = [
    path('', views.popular_movies, name='popular_movies'),  # Home Page
    path('entertainment/', views.entertainment_view, name='entertainment'),
    path('signup/', views.signup_view, name='signup'),      # Signup Page
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('save_review/<int:review_id>/', views.save_review, name='save_review'),
    path('saved_reviews/', views.saved_reviews, name='saved_reviews'),
    path('playlist/', views.playlist, name='playlist'),
    path('add_to_playlist/<int:movie_id>/', views.add_to_playlist, name='add_to_playlist'),
    path('remove_from_playlist/<int:movie_id>/', views.remove_from_playlist, name='remove_from_playlist'),
]
