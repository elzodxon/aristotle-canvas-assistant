import { existsSync } from "node:fs";
import path from "node:path";

let envLoaded = false;

export function getDataDir(): string {
  const configured = process.env.ARISTOTLE_DATA_DIR;
  if (configured && configured.trim().length > 0) {
    return path.resolve(configured);
  }

  return path.resolve(process.cwd(), "aristotle-data");
}

export function getInboxDir(dataDir = getDataDir()): string {
  return path.join(dataDir, "inbox");
}

export function getArchiveDir(dataDir = getDataDir()): string {
  return path.join(dataDir, "archive");
}

export function getFailedDir(dataDir = getDataDir()): string {
  return path.join(dataDir, "failed");
}

export function getLatestReportPath(dataDir = getDataDir()): string {
  return path.join(dataDir, "latest-report.txt");
}

export interface CanvasConfig {
  baseUrl: string;
  accessToken: string;
}

export interface GoogleCalendarConfig {
  credentialsPath: string;
  tokenPath: string;
  calendarId: string;
}

export interface GoogleTasksConfig {
  credentialsPath: string;
  tokenPath: string;
  taskListId?: string;
}

export interface TrelloConfig {
  apiKey: string;
  token: string;
  boardId?: string;
  defaultListId?: string;
}

export interface TodoistConfig {
  apiToken: string;
  defaultProjectId?: string;
}

export interface NotionConfig {
  apiToken: string;
  parentPageId?: string;
}

export interface MicrosoftGraphConfig {
  accessToken: string;
  todoListId?: string;
  calendarId?: string;
  timeZone: string;
}

export interface TelegramConfig {
  botToken: string;
  chatId?: string;
}

export function loadLocalEnv(): void {
  if (envLoaded) {
    return;
  }

  const candidatePaths = [
    path.resolve(process.cwd(), ".env"),
    path.resolve(process.cwd(), ".env.local"),
  ];

  for (const candidatePath of candidatePaths) {
    if (existsSync(candidatePath)) {
      process.loadEnvFile(candidatePath);
    }
  }

  envLoaded = true;
}

export function getCanvasConfig(): CanvasConfig {
  loadLocalEnv();

  const baseUrl = process.env.CANVAS_BASE_URL?.trim();
  const accessToken = process.env.CANVAS_ACCESS_TOKEN?.trim();

  if (!baseUrl) {
    throw new Error("Missing CANVAS_BASE_URL in .env.");
  }

  if (!accessToken) {
    throw new Error("Missing CANVAS_ACCESS_TOKEN in .env.");
  }

  return {
    baseUrl,
    accessToken,
  };
}

export function getGoogleCalendarConfig(): GoogleCalendarConfig {
  loadLocalEnv();

  const credentialsPath = process.env.GOOGLE_CLIENT_CREDENTIALS_PATH?.trim();
  const tokenPath =
    process.env.GOOGLE_CALENDAR_TOKEN_PATH?.trim() ??
    path.resolve(getDataDir(), "google-calendar-token.json");
  const calendarId = process.env.GOOGLE_CALENDAR_ID?.trim() || "primary";

  if (!credentialsPath) {
    throw new Error("Missing GOOGLE_CLIENT_CREDENTIALS_PATH in .env.");
  }

  return {
    credentialsPath: path.resolve(credentialsPath),
    tokenPath: path.resolve(tokenPath),
    calendarId,
  };
}

export function getGoogleTasksConfig(): GoogleTasksConfig {
  loadLocalEnv();

  const credentialsPath = process.env.GOOGLE_CLIENT_CREDENTIALS_PATH?.trim();
  const tokenPath =
    process.env.GOOGLE_TASKS_TOKEN_PATH?.trim() ??
    path.resolve(getDataDir(), "google-tasks-token.json");
  const taskListId = process.env.GOOGLE_TASKS_LIST_ID?.trim();

  if (!credentialsPath) {
    throw new Error("Missing GOOGLE_CLIENT_CREDENTIALS_PATH in .env.");
  }

  return {
    credentialsPath: path.resolve(credentialsPath),
    tokenPath: path.resolve(tokenPath),
    ...(taskListId ? { taskListId } : {}),
  };
}

export function getTrelloConfig(): TrelloConfig {
  loadLocalEnv();

  const apiKey = process.env.TRELLO_API_KEY?.trim();
  const token = process.env.TRELLO_TOKEN?.trim();
  const boardId = process.env.TRELLO_BOARD_ID?.trim();
  const defaultListId = process.env.TRELLO_DEFAULT_LIST_ID?.trim();

  if (!apiKey) {
    throw new Error("Missing TRELLO_API_KEY in .env.");
  }

  if (!token) {
    throw new Error("Missing TRELLO_TOKEN in .env.");
  }

  return {
    apiKey,
    token,
    ...(boardId ? { boardId } : {}),
    ...(defaultListId ? { defaultListId } : {}),
  };
}

export function getTodoistConfig(): TodoistConfig {
  loadLocalEnv();

  const apiToken = process.env.TODOIST_API_TOKEN?.trim();
  const defaultProjectId = process.env.TODOIST_PROJECT_ID?.trim();

  if (!apiToken) {
    throw new Error("Missing TODOIST_API_TOKEN in .env.");
  }

  return {
    apiToken,
    ...(defaultProjectId ? { defaultProjectId } : {}),
  };
}

export function getNotionConfig(): NotionConfig {
  loadLocalEnv();

  const apiToken = process.env.NOTION_API_TOKEN?.trim();
  const parentPageId = process.env.NOTION_PARENT_PAGE_ID?.trim();

  if (!apiToken) {
    throw new Error("Missing NOTION_API_TOKEN in .env.");
  }

  return {
    apiToken,
    ...(parentPageId ? { parentPageId } : {}),
  };
}

export function getMicrosoftGraphConfig(): MicrosoftGraphConfig {
  loadLocalEnv();

  const accessToken = process.env.MICROSOFT_GRAPH_ACCESS_TOKEN?.trim();
  const todoListId = process.env.MICROSOFT_TODO_LIST_ID?.trim();
  const calendarId = process.env.MICROSOFT_CALENDAR_ID?.trim();
  const timeZone = process.env.MICROSOFT_TIME_ZONE?.trim() || "America/Chicago";

  if (!accessToken) {
    throw new Error("Missing MICROSOFT_GRAPH_ACCESS_TOKEN in .env.");
  }

  return {
    accessToken,
    timeZone,
    ...(todoListId ? { todoListId } : {}),
    ...(calendarId ? { calendarId } : {}),
  };
}

export function getTelegramConfig(): TelegramConfig {
  loadLocalEnv();

  const botToken = process.env.TELEGRAM_BOT_TOKEN?.trim();
  const chatId = process.env.TELEGRAM_CHAT_ID?.trim();

  if (!botToken) {
    throw new Error("Missing TELEGRAM_BOT_TOKEN in .env.");
  }

  return {
    botToken,
    ...(chatId ? { chatId } : {}),
  };
}
