from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# Store movies from TMDB API
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    poster_url = models.URLField()
    release_date = models.DateField(null=True, blank=True)
    rating = models.FloatField()

    def __str__(self):
        return self.title


# User's custom playlists
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField(Movie, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Playlist - {self.name}"


# Reviews linked to saved Movie objects
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.BigIntegerField()
    review_text = models.TextField()
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie_id")  # One review per user per movie

    def __str__(self):
        return f"{self.user.username} on movie {self.movie_id}"


class SavedReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "review")  # Prevent duplicate saves

    def __str__(self):
        return f"{self.user.username} saved review {self.review.id} for {self.movie.title}"


class UserMoviePlaylist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user.username} added {self.movie.title} to playlist"
