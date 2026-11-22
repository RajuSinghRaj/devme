# DevTrack

A small black-and-white developer activity log with a Flask dashboard, SQLite storage, and a JSON API.

## Run locally

Install dependencies with `python -m pip install -r requirements.txt`, then start the app with `python run.py`. Open `http://127.0.0.1:5000`.

Set `DEVTRACK_SECRET_KEY` to a private random value before deployment. Set `DEVTRACK_DATABASE` to choose the SQLite database file.

## API

- `GET /health` reports service health.
- `GET /api/events` lists entries. Optional `q` and `limit` query parameters filter results.
- `POST /api/events` accepts a JSON object with `title` and optional `details`, `category`, and `severity` (`low`, `normal`, or `high`).
- `GET`, `PUT`, and `DELETE /api/events/<id>` retrieve, update, or remove an entry.
