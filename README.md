# Movies Mosaic

Movies Mosaic is a web application that lets users search for movies, view posters, and create a personalized mosaic of their favorite films using the TMDB API.

## Features

- Search for movies by title
- Display movie posters in a responsive grid
- Select movies to create a custom mosaic
- Dark mode support for comfortable viewing
- Error handling and loading indicators for API requests
- Options to clear search results, selected movies, mosaic, or all data

## Getting Started

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/vishal-kumar8583/movies-mosaic.git
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

4. **Start the development server:**
   ```powershell
   python manage.py runserver
   ```

5. **Access the app:**
   Open your browser and go to `http://127.0.0.1:8000/`

## Project Structure

- core – Django app with models, views, forms, and URLs
- MoviesMosaic – Project settings and configuration
- static – Static files (CSS, images)
- templates – HTML templates for the UI

## API

This project uses the [TMDB API](https://www.themoviedb.org/documentation/api) for movie data. You’ll need an API key to enable search and poster display.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

## License

This project is licensed under the MIT License.