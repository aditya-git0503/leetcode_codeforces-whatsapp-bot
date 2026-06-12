"""
fetch_codeforces.py
───────────────────
Fetches today's solved problems, all-time solved count, and contest rating
from Codeforces' public REST API. Outputs a JSON payload that the Node.js
WhatsApp sender reads via stdout.

Usage:
    python3 fetch_codeforces.py <codeforces_handle>
"""

import sys
import json
import requests
from datetime import datetime, timezone

CF_API = "https://codeforces.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CFBot/1.0)"}

# Codeforces problem ratings → LeetCode-style difficulty buckets
def bucket(rating):
    if rating is None:
        return "Unknown"
    if rating < 1300:
        return "Easy"
    if rating < 1900:
        return "Medium"
    return "Hard"


def api(method: str, params: dict) -> dict:
    r = requests.get(f"{CF_API}/{method}", headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != "OK":
        raise RuntimeError(payload.get("comment", "Codeforces API error"))
    return payload["result"]


# ── Queries ──────────────────────────────────────────────────────────────────

def user_info(handle: str) -> dict | None:
    result = api("user.info", {"handles": handle})
    return result[0] if result else None


def all_submissions(handle: str) -> list:
    # count=0 is rejected; a large count returns the full history.
    return api("user.status", {"handle": handle, "from": 1, "count": 100000})


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_codeforces.py <handle>"}))
        sys.exit(1)

    handle = sys.argv[1]
    today = datetime.now(timezone.utc).date()

    subs = all_submissions(handle)

    # All-time unique solved problems + today's unique solved problems
    solved_all = set()
    today_subs = []
    seen_today = set()
    for s in subs:
        if s.get("verdict") != "OK":
            continue
        prob = s["problem"]
        key = (prob.get("contestId"), prob.get("index"))
        solved_all.add(key)

        d = datetime.fromtimestamp(s["creationTimeSeconds"], tz=timezone.utc).date()
        if d == today and key not in seen_today:
            seen_today.add(key)
            today_subs.append({
                "number": f"{prob.get('contestId', '?')}{prob.get('index', '')}",
                "title": prob.get("name", "Unknown"),
                "difficulty": bucket(prob.get("rating")),
                "rating": prob.get("rating"),
                "topics": prob.get("tags", [])[:3],
            })

    info = user_info(handle)
    contest = None
    if info and info.get("rating") is not None:
        contest = {
            "rating": info.get("rating"),
            "maxRating": info.get("maxRating"),
            "rank": info.get("rank"),
            "maxRank": info.get("maxRank"),
        }

    # Bucket all-time solved by difficulty isn't available without re-fetching
    # ratings per problem; report the unique total, which the API gives us.
    result = {
        "handle": handle,
        "date": str(today),
        "today_solved": today_subs,
        "stats": {"All": len(solved_all)},
        "contest": contest,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
