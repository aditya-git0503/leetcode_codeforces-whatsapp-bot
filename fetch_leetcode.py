"""
fetch_leetcode.py
─────────────────
Fetches today's solved problems, all-time stats, and contest rating
from LeetCode's public GraphQL API. Outputs a JSON payload that the
Node.js WhatsApp sender reads via stdout.

Usage:
    python3 fetch_leetcode.py <leetcode_username>
"""

import sys
import json
import requests
from datetime import datetime, timezone
from collections import defaultdict

LEETCODE_GQL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0 (compatible; LeetBot/1.0)",
}

def gql(query: str, variables: dict) -> dict:
    r = requests.post(
        LEETCODE_GQL,
        headers=HEADERS,
        json={"query": query, "variables": variables},
        timeout=20,
    )
    r.raise_for_status()
    return r.json().get("data", {})


# ── Queries ────────────────────────────────────────────────────────────────────

def recent_submissions(username: str) -> list:
    data = gql("""
        query($username: String!, $limit: Int!) {
          recentAcSubmissionList(username: $username, limit: $limit) {
            id title titleSlug timestamp
          }
        }
    """, {"username": username, "limit": 50})
    return data.get("recentAcSubmissionList", [])


def problem_detail(slug: str) -> dict:
    data = gql("""
        query($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionFrontendId difficulty
            topicTags { name }
          }
        }
    """, {"titleSlug": slug})
    return data.get("question", {})


def user_stats(username: str) -> dict:
    data = gql("""
        query($username: String!) {
          matchedUser(username: $username) {
            submitStatsGlobal {
              acSubmissionNum { difficulty count }
            }
          }
        }
    """, {"username": username})
    counts = (data.get("matchedUser") or {}) \
                 .get("submitStatsGlobal", {}) \
                 .get("acSubmissionNum", [])
    out = {"All": 0, "Easy": 0, "Medium": 0, "Hard": 0}
    for item in counts:
        out[item["difficulty"]] = item["count"]
    return out


def contest_rating(username: str) -> dict | None:
    data = gql("""
        query($username: String!) {
          userContestRanking(username: $username) {
            rating globalRanking topPercentage
          }
        }
    """, {"username": username})
    return data.get("userContestRanking")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: fetch_leetcode.py <username>"}))
        sys.exit(1)

    username = sys.argv[1]
    today = datetime.now(timezone.utc).date()

    # Filter to today's unique solved problems
    subs = recent_submissions(username)
    seen, today_subs = set(), []
    for s in subs:
        d = datetime.fromtimestamp(int(s["timestamp"]), tz=timezone.utc).date()
        if d == today and s["titleSlug"] not in seen:
            today_subs.append(s)
            seen.add(s["titleSlug"])

    # Enrich with difficulty + topics
    enriched = []
    for s in today_subs:
        detail = problem_detail(s["titleSlug"])
        enriched.append({
            "number": detail.get("questionFrontendId", "?"),
            "title": s["title"],
            "difficulty": detail.get("difficulty", "Unknown"),
            "topics": [t["name"] for t in detail.get("topicTags", [])][:3],
        })

    stats   = user_stats(username)
    contest = contest_rating(username)

    result = {
        "username": username,
        "date": str(today),
        "today_solved": enriched,
        "stats": stats,
        "contest": contest,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
