# LeetCode WhatsApp Bot

Sends a daily WhatsApp report of your LeetCode activity — problems solved today (with problem number, title, and topics), all-time stats by difficulty, and contest rating. Uses LeetCode's public GraphQL API and Whapi.Cloud's free sandbox plan.

---

## How It Works

1. A Python script queries LeetCode's GraphQL API to fetch today's solved problems, all-time stats, and contest rating for your username.
2. A Node.js script formats the data into a WhatsApp message and sends it via the Whapi.Cloud API.
3. You run one shell script to trigger everything.

No browser automation. No QR codes after initial setup. No cost.

---

## Requirements

- Linux (Ubuntu/Debian)
- Python 3.10+
- Node.js v18+
- A Whapi.Cloud account (free sandbox plan)
- A WhatsApp account linked to Whapi

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/leetcode-whatsapp-bot.git
cd leetcode-whatsapp-bot
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Node dependencies

```bash
npm install
```

### 4. Set up Whapi.Cloud

Whapi.Cloud provides a free WhatsApp API sandbox with 150 messages/day — more than enough for one daily report.

1. Go to [https://whapi.cloud](https://whapi.cloud) and sign up for a free account. No credit card required.
2. After signing in, create a new channel.
3. Scan the QR code shown in your dashboard using WhatsApp on your phone: open WhatsApp → tap the three-dot menu → Linked Devices → Link a Device.
4. Once connected, copy your **API Token** from the dashboard. It will look like a long string of letters and numbers.
5. Note your **API URL** from the dashboard. It is typically `https://gate.whapi.cloud/`.
6. To make your plan permanent, contact Whapi support via live chat on their website and ask them to switch your channel from Trial to Sandbox mode. The sandbox plan is free forever with the same limits.

### 5. Find your WhatsApp recipient ID

**To send to yourself:**
Your recipient ID is your phone number with country code and no `+` sign. For example, if your number is +91 98765 43210, use `919876543210`.

**To send to a WhatsApp group (recommended):**
1. Create a WhatsApp group on your phone.
2. Ask someone else in the group to send a message, or temporarily add a contact and have them message.
3. Check Whapi's received messages to find the group ID:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://gate.whapi.cloud/messages/in
```

The group ID will appear in the `chat_id` field and ends with `@g.us`, for example `120363427603859887@g.us`.

### 6. Configure environment variables

```bash
cp .env.example .env
nano .env
```

Fill in all four values:

```
LEETCODE_USERNAME=your_leetcode_username
RECIPIENT_NUMBER=120363427603859887@g.us
PYTHON_BIN=/home/YOUR_USERNAME/leetcode-whatsapp-bot/venv/bin/python3
WHAPI_TOKEN=your_whapi_token_here
```

To find your exact Python binary path:

```bash
source venv/bin/activate
which python3
```

Copy that output into `PYTHON_BIN`.

### 7. Make the run script executable

```bash
chmod +x run.sh
```

---

## Running the Bot

Each time you want to send the report, run from inside the project folder:

```bash
./run.sh
```

The terminal will show a preview of the message and confirm when it is sent. The WhatsApp message arrives within a few seconds.

---

## Sample Output

```
LeetCode Daily Report
Friday, 30 May 2026
your_username
────────────────────────────

Solved Today: 2 problems

Easy (1)
  #1 Two Sum
  Array, Hash Table

Medium (1)
  #3 Longest Substring Without Repeating Characters
  Hash Table, Sliding Window, String

────────────────────────────
All-Time Solved
Easy: 248   Medium: 103   Hard: 0
Total: 351

────────────────────────────
Contest Stats
Rating: 1531
Global Rank: 3,12,653 (Top 36.2%)
```

---

## Project Structure

```
leetcode-whatsapp-bot/
├── fetch_leetcode.py     # Queries LeetCode GraphQL API
├── send_report.js        # Formats message and sends via Whapi
├── run.sh                # One-command script to run the bot
├── requirements.txt      # Python dependencies (requests)
├── package.json          # Node dependencies (dotenv)
├── .env.example          # Template for environment variables
├── .gitignore            # Excludes .env, venv, node_modules
└── README.md
```

---

## Security

- Your API token and WhatsApp number are stored only in `.env`, which is excluded from Git via `.gitignore`.
- Never commit `.env` to GitHub. The `.env.example` file is safe to commit — it contains no real credentials.
- LeetCode data is fetched from a public API. No LeetCode login or password is needed.

---

## Troubleshooting

**"Error: Set LEETCODE_USERNAME, RECIPIENT_NUMBER, WHAPI_TOKEN in .env"**
One or more required variables are missing from your `.env` file. Open it with `nano .env` and check all four values are filled in.

**"Failed: ..." when sending**
Your Whapi token may be wrong or your trial may have expired. Log in to [https://whapi.cloud](https://whapi.cloud), check your channel is active, and copy the token again.

**No problems showing for today**
LeetCode's API uses UTC time. If you solved problems before midnight UTC, they will appear the next day. This is a LeetCode API limitation.

**Python not found / import errors**
Make sure you activated the venv before running: `source venv/bin/activate`. The `(venv)` prefix should appear in your terminal prompt.

---

## Dependencies

| Name | Purpose | Cost |
|------|---------|------|
| LeetCode GraphQL API | Fetch solve data | Free, no auth needed |
| Whapi.Cloud Sandbox | Send WhatsApp messages | Free, 150 msg/day |
| Python requests | HTTP calls in Python | Free |
| Node.js dotenv | Load .env variables | Free |
