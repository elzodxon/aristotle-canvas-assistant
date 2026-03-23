import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { existsSync } from "node:fs";
import { writeFile, readFile } from "node:fs/promises";
import path from "node:path";

interface SetupResult {
  canvasBaseUrl: string;
  canvasAccessToken: string;
  telegramBotToken?: string | undefined;
  telegramChatId?: string | undefined;
}

export async function runSetupWizard(): Promise<void> {
  const rl = createInterface({ input, output });

  try {
    printBanner();

    const envPath = path.resolve(process.cwd(), ".env");
    if (existsSync(envPath)) {
      const overwrite = await askYesNo(
        rl,
        "A .env file already exists. Do you want to reconfigure?",
      );
      if (!overwrite) {
        console.log("\nSetup cancelled. Your existing .env is unchanged.");
        return;
      }
    }

    // Step 1: Canvas setup
    console.log("\n--- Step 1/4: Canvas LMS ---");
    console.log("Aristotle needs your Canvas URL and access token to pull assignments.");
    console.log("Your Canvas URL looks like: https://yourschool.instructure.com\n");

    const canvasBaseUrl = await askRequired(rl, "Canvas URL");
    const cleanUrl = canvasBaseUrl.replace(/\/+$/, "");

    console.log("\nTo get your access token:");
    console.log("  1. Log in to Canvas");
    console.log("  2. Go to Account > Settings");
    console.log("  3. Scroll to Approved Integrations > + New Access Token");
    console.log("  4. Copy the token\n");

    const canvasAccessToken = await askRequired(rl, "Canvas access token");

    // Verify Canvas connection
    console.log("\nVerifying Canvas connection...");
    const profile = await verifyCanvas(cleanUrl, canvasAccessToken);

    if (!profile) {
      console.log("Could not connect to Canvas. Please check your URL and token.");
      const retry = await askYesNo(rl, "Continue anyway?");
      if (!retry) {
        console.log("Setup cancelled.");
        return;
      }
    } else {
      console.log(`Connected! Welcome, ${profile.name} (${profile.email ?? "no email"}).`);
    }

    // Step 2: Telegram (optional)
    console.log("\n--- Step 2/4: Telegram Bot (optional) ---");
    console.log("Aristotle can send you assignment PDFs and reminders via Telegram.");
    const wantTelegram = await askYesNo(rl, "Set up Telegram?");

    let telegramBotToken: string | undefined;
    let telegramChatId: string | undefined;

    if (wantTelegram) {
      console.log("\nTo create a Telegram bot:");
      console.log("  1. Open Telegram and search for @BotFather");
      console.log("  2. Send /newbot and follow the prompts");
      console.log("  3. Copy the bot token\n");

      telegramBotToken = await askRequired(rl, "Bot token");

      console.log("\nTo get your chat ID:");
      console.log("  1. Send any message to your bot");
      console.log("  2. Enter your Telegram chat ID (numeric)\n");

      telegramChatId = await askRequired(rl, "Chat ID");

      console.log("\nVerifying Telegram bot...");
      const bot = await verifyTelegram(telegramBotToken);
      if (bot) {
        console.log(`Bot connected: @${bot.username}`);
      } else {
        console.log("Could not verify bot. Check the token later.");
      }
    }

    // Step 3: Write .env
    console.log("\n--- Step 3/4: Saving configuration ---");
    const envContent = buildEnvFile({
      canvasBaseUrl: cleanUrl,
      canvasAccessToken,
      telegramBotToken,
      telegramChatId,
    });

    await writeFile(envPath, envContent, "utf-8");
    console.log("Configuration saved to .env");

    // Step 4: First sync
    console.log("\n--- Step 4/4: First sync ---");
    const doSync = await askYesNo(rl, "Sync your Canvas assignments now?");

    if (doSync) {
      console.log("\nSyncing...");
      await firstSync(cleanUrl, canvasAccessToken);
    }

    printSuccess(profile?.name);
  } finally {
    rl.close();
  }
}

function printBanner(): void {
  console.log("=".repeat(50));
  console.log("  Aristotle Canvas Assistant - Setup");
  console.log("=".repeat(50));
  console.log("");
  console.log("This wizard will configure Aristotle in ~2 minutes.");
  console.log("You will need:");
  console.log("  - Your Canvas LMS URL and access token");
  console.log("  - (Optional) A Telegram bot token");
}

function printSuccess(name?: string): void {
  console.log("");
  console.log("=".repeat(50));
  console.log("  Setup complete!");
  console.log("=".repeat(50));
  console.log("");
  if (name) {
    console.log(`  Welcome aboard, ${name}.`);
    console.log("");
  }
  console.log("  Try these commands:");
  console.log("    npm run canvas:preview    - see upcoming deadlines");
  console.log("    npm run canvas:sync       - sync assignments");
  console.log("    npm run updates -- --days 7  - weekly plan");
  console.log("    npm run prep -- --course \"Course Name\"");
  console.log("");
  console.log("  Or use the Aristotle skill in Claude Code:");
  console.log("    npm run skill:install");
  console.log("    then: use $aristotle to check my next 7 days");
  console.log("");
}

async function verifyCanvas(
  baseUrl: string,
  token: string,
): Promise<{ name: string; email?: string | undefined } | null> {
  try {
    const url = new URL("/api/v1/users/self/profile", baseUrl);
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) return null;

    const data = (await response.json()) as {
      name: string;
      primary_email?: string;
    };
    return { name: data.name, email: data.primary_email };
  } catch {
    return null;
  }
}

async function verifyTelegram(
  botToken: string,
): Promise<{ username: string } | null> {
  try {
    const response = await fetch(
      `https://api.telegram.org/bot${botToken}/getMe`,
    );
    const data = (await response.json()) as {
      ok: boolean;
      result?: { username: string };
    };
    if (!data.ok || !data.result) return null;
    return { username: data.result.username };
  } catch {
    return null;
  }
}

async function firstSync(baseUrl: string, token: string): Promise<void> {
  try {
    const url = new URL("/api/v1/users/self/upcoming_events", baseUrl);
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      console.log("Could not fetch assignments. Run `npm run canvas:sync` later.");
      return;
    }

    const events = (await response.json()) as Array<{
      type?: string;
      title: string;
      end_at?: string;
      context_name?: string;
      assignment?: { name?: string };
    }>;

    const assignments = events.filter(
      (e) => (e.type ?? "assignment") === "assignment",
    );

    if (assignments.length === 0) {
      console.log("No upcoming assignments found on Canvas.");
      return;
    }

    console.log(`\nFound ${assignments.length} upcoming assignment(s):\n`);
    for (const a of assignments) {
      const title = a.assignment?.name?.trim() || a.title.trim();
      const course = a.context_name?.trim() || "Unknown course";
      const due = a.end_at
        ? new Date(a.end_at).toLocaleDateString("en-US", {
            weekday: "short",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })
        : "no date";
      console.log(`  - ${title} (${course}) -- due ${due}`);
    }

    console.log("\nRun `npm run canvas:sync` to import these into Aristotle.");
  } catch {
    console.log("Sync failed. Run `npm run canvas:sync` later.");
  }
}

function buildEnvFile(config: SetupResult): string {
  const lines: string[] = [
    "ARISTOTLE_DATA_DIR=./aristotle-data",
    "",
    `CANVAS_BASE_URL=${config.canvasBaseUrl}`,
    `CANVAS_ACCESS_TOKEN=${config.canvasAccessToken}`,
    "",
    "# Google Calendar + Google Tasks",
    "GOOGLE_CLIENT_CREDENTIALS_PATH=",
    "GOOGLE_CALENDAR_TOKEN_PATH=./aristotle-data/google-calendar-token.json",
    "GOOGLE_CALENDAR_ID=primary",
    "GOOGLE_TASKS_TOKEN_PATH=./aristotle-data/google-tasks-token.json",
    "GOOGLE_TASKS_LIST_ID=",
    "",
    "# Trello",
    "TRELLO_API_KEY=",
    "TRELLO_TOKEN=",
    "TRELLO_BOARD_ID=",
    "TRELLO_DEFAULT_LIST_ID=",
    "",
    "# Todoist",
    "TODOIST_API_TOKEN=",
    "TODOIST_PROJECT_ID=",
    "",
    "# Notion",
    "NOTION_API_TOKEN=",
    "NOTION_PARENT_PAGE_ID=",
    "",
    "# Microsoft Graph (Outlook Calendar + Microsoft To Do)",
    "MICROSOFT_GRAPH_ACCESS_TOKEN=",
    "MICROSOFT_CALENDAR_ID=",
    "MICROSOFT_TODO_LIST_ID=",
    "MICROSOFT_TIME_ZONE=America/Chicago",
    "",
    "# Telegram Bot",
  ];

  if (config.telegramBotToken) {
    lines.push(`TELEGRAM_BOT_TOKEN=${config.telegramBotToken}`);
  } else {
    lines.push("TELEGRAM_BOT_TOKEN=");
  }

  if (config.telegramChatId) {
    lines.push(`TELEGRAM_CHAT_ID=${config.telegramChatId}`);
  } else {
    lines.push("TELEGRAM_CHAT_ID=");
  }

  lines.push("");
  return lines.join("\n");
}

async function askRequired(
  rl: ReturnType<typeof createInterface>,
  label: string,
): Promise<string> {
  while (true) {
    const value = (await rl.question(`${label}: `)).trim();
    if (value.length > 0) return value;
    console.log(`  ${label} is required.`);
  }
}

async function askYesNo(
  rl: ReturnType<typeof createInterface>,
  question: string,
): Promise<boolean> {
  const answer = (await rl.question(`${question} (y/n): `)).trim().toLowerCase();
  return answer === "y" || answer === "yes";
}
