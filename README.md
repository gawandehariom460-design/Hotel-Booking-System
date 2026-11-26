# Hotel Booking System

A small hotel room search and reservation app for practicing web development.

## Stack
Python 3, Flask, Flask-SQLAlchemy (SQLite), HTML, CSS, vanilla JavaScript.

## Changes in this customized version
- Room type and nightly-rate filters
- Check-in/check-out validation and date-overlap availability checks
- Reservation confirmation and cancellation
- Responsive room cards with sample inventory

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. The app creates a local SQLite database and sample rooms on first run.

## Source and attribution
Feature inspiration: [dhavalveera/hotel-booking](https://github.com/dhavalveera/hotel-booking), MIT License. This repository contains a simplified, reworked implementation for practice; original copyright notice is retained in LICENSE.

Demo only: use fictional data. No real bookings or payments are processed.
