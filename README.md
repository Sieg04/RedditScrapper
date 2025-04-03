# Reddit Loan Tracker 📊

A tool for tracking and analyzing posts from the r/SimpleLoans subreddit, with a focus on identifying lending patterns, borrower history, and potential suspicious behavior.

## 🔍 Features

- Scrapes post data from r/SimpleLoans using Reddit API or Pushshift (depending on setup).
- Outputs a **Google Sheet** with:
  - Links to all relevant posts
  - Post titles (sortable)
  - Date, user, and post type ([Req], [Paid], [Unpaid], etc.)
- Filters to group posts by type
- Basic charts for visualizing activity (e.g. number of requests, repayments, top users)
- Optional user-level analysis for deeper investigations

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Reddit API credentials (client ID, secret, and user agent)
- Google Sheets API credentials (if exporting to Sheets)

### Installation

1. Clone the repo:
```bash
git clone https://github.com/yourusername/reddit-loan-tracker.git
cd reddit-loan-tracker
