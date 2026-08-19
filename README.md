# ARIRANG - BTS Fan Site + Shop (Flask College Project)

An unofficial fan site for BTS's 2026 album *ARIRANG*, combining an info section
(album facts, tracklist) with a small merch shop (login required to purchase).

## Features
- **Info pages:** home page with album hero + full 14-track tracklist, an About
  page with verified release facts
- **Shop:** merch catalog filterable by category (Photocards / Light Sticks / Albums)
- **Accounts:** register/login (passwords hashed with Werkzeug)
- **Cart:** add/remove items, running total, dummy checkout

## How to Run

1. Install Python 3.9+
2. In this folder, create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open **http://127.0.0.1:5000**

The database and sample data (real tracklist + placeholder merch) are created
automatically on first run.

## Project Structure
```
arirang_site/
├── app.py
├── requirements.txt
├── templates/
│   ├── base.html      # navbar + footer
│   ├── home.html      # hero + tracklist
│   ├── about.html      # album facts
│   ├── shop.html
│   ├── cart.html
│   ├── login.html
│   └── register.html
└── static/
    └── style.css      # red/black theme
```

## Notes for your project report
- Album facts (release date, tracklist, producers) are real and verified —
  cite BigHit Music / Billboard / Wikipedia if your report needs sources.
- Product images are emoji placeholders, not real photos — swap them for
  licensed images only if you have rights to use them; otherwise the
  placeholders are safer for a public project.
- This is clearly an unofficial fan project (see footer disclaimer) — keep
  that disclaimer if you present or publish it, since it's not affiliated
  with BTS or BigHit Music.

## Ideas to extend it
- Add member profile pages
- Add a comments/guestbook section for fans
- Add release countdown timer (JS) for future tour dates
- Add search bar for merch
