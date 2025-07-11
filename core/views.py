import requests
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.db import IntegrityError
from .models import Review, SavedReview, Movie, UserMoviePlaylist
import logging

TMDB_API_KEY = settings.TMDB_API_KEY
logger = logging.getLogger(__name__)


def popular_movies(request):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&page=1"
    response = requests.get(url)

    if response.status_code != 200:
        messages.error(request, "TMDB API Error: Could not load movies.")
        return render(request, "Home.html", {"movies": [], "user": request.user})

    data = response.json()

    movies = []
    for movie in data.get("results", []):
        movies.append(
            {
                "id": movie["id"],  # Added id for linking to details
                "title": movie["title"],
                "poster_url": (
                    f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                    if movie["poster_path"]
                    else ""
                ),
                "rating": movie["vote_average"],
                "release_date": movie["release_date"],
            }
        )

    return render(request, "Home.html", {"movies": movies, "user": request.user})


def entertainment_view(request):
    query = request.GET.get("query")
    filter_type = request.GET.get("filter")
    page = request.GET.get("page", 1)

    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    movies = []
    total_pages = 1

    if query:  # Search mode
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&include_adult=false&page={page}"
        response = requests.get(search_url)
        if response.status_code != 200:
            messages.error(request, "TMDB API Error: Could not load search results.")
            return render(
                request,
                "entertainment.html",
                {
                    "movies": [],
                    "query": query or "",
                    "filter": filter_type or "popular",
                    "page": page,
                    "total_pages": total_pages,
                },
            )

        data = response.json()
        results = data.get("results", [])
        total_pages = data.get("total_pages", 1)

        filtered = [
            movie
            for movie in results
            if (
                movie.get("vote_average", 0) >= 4
                and not movie.get("adult", False)
                and movie.get("poster_path")
            )
        ]

        query_lower = query.lower()

        def sort_key(m):
            title = m.get("title", "").lower()
            title_contains = query_lower in title
            return (not title_contains, -m.get("vote_average", 0))

        filtered.sort(key=sort_key)

        movies = filtered

    else:
        if filter_type == "latest":
            url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=en-US&page={page}&include_adult=false"
        else:  # default popular
            url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}&include_adult=false"

        response = requests.get(url)
        if response.status_code != 200:
            messages.error(request, "TMDB API Error: Could not load movies.")
            return render(
                request,
                "entertainment.html",
                {
                    "movies": [],
                    "query": query or "",
                    "filter": filter_type or "popular",
                    "page": page,
                    "total_pages": total_pages,
                },
            )

        data = response.json()
        results = data.get("results", [])
        total_pages = data.get("total_pages", 1)

        movies = [
            movie
            for movie in results
            if (
                movie.get("vote_average", 0) >= 4
                and not movie.get("adult", False)
                and movie.get("poster_path")
            )
        ]

    movies = [
        {
            "id": m["id"],
            "title": m["title"],
            "poster_url": f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
            "rating": round(m.get("vote_average", 0), 1),
            "release_date": m.get("release_date", "N/A"),
        }
        for m in movies
    ]

    return render(
        request,
        "entertainment.html",
        {
            "movies": movies,
            "query": query or "",
            "filter": filter_type or "popular",
            "page": page,
            "total_pages": total_pages,
        },
    )


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "Login.html")


@login_required
def dashboard_view(request):
    user = request.user
    return render(request, "UserDashboard.html", {"user": user})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            context = {"username": username, "email": email}
            return render(request, "Signup.html", context)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            context = {"username": username, "email": email}
            return render(request, "Signup.html", context)

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.save()

        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("/")

    return render(request, "Signup.html")


def movie_detail(request, movie_id):
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US"

    movie_resp = requests.get(movie_url).json()
    credits_resp = requests.get(credits_url).json()

    director = next(
        (c["name"] for c in credits_resp.get("crew", []) if c["job"] == "Director"), ""
    )
    cast = [c["name"] for c in credits_resp.get("cast", [])[:5]]

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        review_text = request.POST.get("review", "").strip()
        rating = request.POST.get("rating")

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            rating = 0.0

        try:
            movie_id_int = int(movie_id)
        except ValueError:
            messages.error(request, "Invalid movie ID.")
            return redirect("entertainment")

        # Ensure Movie object exists for this movie_id
        movie_obj, created = Movie.objects.get_or_create(
            tmdb_id=movie_id_int,
            defaults={
                'title': movie_resp.get('title', ''),
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie_resp['poster_path']}" if movie_resp.get('poster_path') else '',
                'release_date': movie_resp.get('release_date') or None,
                'rating': movie_resp.get('vote_average', 0.0),
            }
        )
        logger.info(f"Movie object {'created' if created else 'found'}: {movie_obj}")

        if review_text and rating > 0:
            try:
                review = Review.objects.create(
                    user=request.user,
                    movie_id=movie_id_int,
                    review_text=review_text,
                    rating=rating,
                )
                logger.info(f"Review created: {review}")
                # Add movie to user's playlist if not already present
                UserMoviePlaylist.objects.get_or_create(user=request.user, movie=movie_obj)
                # Also save the review to SavedReview
                SavedReview.objects.get_or_create(user=request.user, movie=movie_obj, review=review)
                messages.success(request, "Review submitted successfully!")
            except IntegrityError:
                logger.warning(f"Duplicate review for user {request.user} and movie {movie_id_int}")
                messages.error(
                    request, "You have already submitted a review for this movie."
                )
            return redirect(request.path)
        else:
            logger.warning("Invalid review or rating submitted.")
            messages.error(request, "Please enter a valid review and rating.")

    context = {
        "movie": {
            "title": movie_resp.get("title"),
            "release_date": movie_resp.get("release_date"),
            "overview": movie_resp.get("overview"),
            "poster_url": (
                f"https://image.tmdb.org/t/p/w500{movie_resp['poster_path']}"
                if movie_resp.get("poster_path")
                else ""
            ),
            "director": director,
            "cast": cast,
            "rating": movie_resp.get("vote_average"),
            "genres_names": [g["name"] for g in movie_resp.get("genres", [])],
        },
        "reviews": Review.objects.filter(movie_id=movie_id).order_by("-created_at"),
        "movie_id": movie_id,
    }

    return render(request, "movie_detail.html", context)


@login_required
def save_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    try:
        movie = Movie.objects.get(tmdb_id=review.movie_id)
    except Movie.DoesNotExist:
        # Fetch movie data from TMDB and create Movie object
        tmdb_id = review.movie_id
        movie_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
        resp = requests.get(movie_url)
        if resp.status_code == 200:
            data = resp.json()
            movie = Movie.objects.create(
                tmdb_id=tmdb_id,
                title=data.get('title', ''),
                poster_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else '',
                release_date=data.get('release_date') or None,
                rating=data.get('vote_average', 0.0),
            )
        else:
            messages.error(request, "Could not fetch movie data to save review.")
            return redirect('movie_detail', movie_id=tmdb_id)
    saved_review, created = SavedReview.objects.get_or_create(user=request.user, movie=movie, review=review)
    logger.info(f"SavedReview object {'created' if created else 'found'}: {saved_review}")
    messages.success(request, "Review saved to your playlist!")
    return redirect('saved_reviews')


@login_required
def saved_reviews(request):
    saved = SavedReview.objects.filter(user=request.user).select_related('review', 'movie').order_by('-saved_at')
    return render(request, 'saved_reviews.html', {'saved_reviews': saved})


@login_required
def playlist(request):
    from .models import UserMoviePlaylist
    saved = SavedReview.objects.filter(user=request.user).select_related('review', 'movie').order_by('-saved_at')
    movies = UserMoviePlaylist.objects.filter(user=request.user).select_related('movie').order_by('-added_at')
    return render(request, 'playlist.html', {'saved_reviews': saved, 'movies': movies})


@login_required
def add_to_playlist(request, movie_id):
    movie_obj, created = Movie.objects.get_or_create(
        tmdb_id=movie_id,
        defaults={
            'title': request.GET.get('title', ''),
            'poster_url': request.GET.get('poster_url', ''),
            'release_date': request.GET.get('release_date') or None,
            'rating': request.GET.get('rating', 0.0),
        }
    )
    UserMoviePlaylist.objects.get_or_create(user=request.user, movie=movie_obj)
    messages.success(request, f"{movie_obj.title} added to your playlist!")
    return redirect('playlist')


@login_required
def remove_from_playlist(request, movie_id):
    UserMoviePlaylist.objects.filter(user=request.user, movie__tmdb_id=movie_id).delete()
    messages.success(request, "Movie removed from your playlist.")
    return redirect('playlist')
