require("dotenv").config();
const { execSync } = require("child_process");
const path = require("path");

const LEETCODE_USERNAME = process.env.LEETCODE_USERNAME;
const RECIPIENT        = process.env.RECIPIENT_NUMBER;
const PYTHON_BIN       = process.env.PYTHON_BIN || "python3";
const WHAPI_TOKEN      = process.env.WHAPI_TOKEN;

if (!LEETCODE_USERNAME || !RECIPIENT || !WHAPI_TOKEN) {
  console.error("Error: Set LEETCODE_USERNAME, RECIPIENT_NUMBER, WHAPI_TOKEN in .env");
  process.exit(1);
}

function fetchData() {
  console.log("Fetching LeetCode data...");
  const script = path.join(__dirname, "fetch_leetcode.py");
  return JSON.parse(
    execSync(`${PYTHON_BIN} "${script}" "${LEETCODE_USERNAME}"`, { timeout: 60_000 }).toString()
  );
}

function formatMessage(data) {
  const { username, date, today_solved, stats, contest } = data;
  const dateStr = new Date(date + "T00:00:00Z").toLocaleDateString("en-IN", {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });
  const divider = "─".repeat(28);

  let msg = `*LeetCode Daily Report*\n${dateStr}\n${username}\n${divider}\n\n`;

  if (today_solved.length === 0) {
    msg += `No problems solved today.\n`;
  } else {
    msg += `*Solved Today: ${today_solved.length} problem${today_solved.length > 1 ? "s" : ""}*\n\n`;
    const groups = { Easy: [], Medium: [], Hard: [] };
    today_solved.forEach(p => (groups[p.difficulty] || groups.Easy).push(p));
    for (const diff of ["Easy", "Medium", "Hard"]) {
      const problems = groups[diff];
      if (!problems.length) continue;
      msg += `*${diff}* (${problems.length})\n`;
      problems.forEach(p => {
        const topics = p.topics.length ? p.topics.join(", ") : "General";
        msg += `  #${p.number} ${p.title}\n  ${topics}\n`;
      });
      msg += "\n";
    }
  }

  msg += `${divider}\n*All-Time Solved*\n`;
  msg += `Easy: *${stats.Easy}*   Medium: *${stats.Medium}*   Hard: *${stats.Hard}*\n`;
  msg += `Total: *${stats.All}*\n`;

  if (contest) {
    const rating = Math.round(contest.rating);
    const rank   = contest.globalRanking?.toLocaleString("en-IN") ?? "N/A";
    const top    = contest.topPercentage ? ` (Top ${contest.topPercentage.toFixed(1)}%)` : "";
    msg += `\n${divider}\n*Contest Stats*\nRating: *${rating}*\nGlobal Rank: *${rank}*${top}\n`;
  }

  return msg;
}

async function sendWhatsApp(message) {
  const chatId = RECIPIENT.includes("@") ? RECIPIENT : `${RECIPIENT}@c.us`;
  const res = await fetch("https://gate.whapi.cloud/messages/text", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${WHAPI_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ to: chatId, body: message }),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(json));
  return json;
}

async function main() {
  const data    = fetchData();
  const message = formatMessage(data);
  console.log("\nMessage preview:\n");
  console.log(message);
  console.log("\nSending via Whapi...");
  try {
    const result = await sendWhatsApp(message);
    console.log("Sent! Message ID:", result.sent_id || result.id);
  } catch (err) {
    console.error("Failed:", err.message);
  }
}

main();
