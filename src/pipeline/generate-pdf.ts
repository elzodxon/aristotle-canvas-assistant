import { writeFile } from "node:fs/promises";
import path from "node:path";
import type { CanvasConfig } from "../config.js";

interface CanvasAssignment {
  id: number;
  name: string;
  description: string | null;
  due_at: string | null;
  points_possible: number;
  html_url: string;
  submission_types: string[];
}

interface CanvasFileInfo {
  filename: string;
  url: string;
  size: number;
}

interface GeneratePdfOptions {
  courseId: number;
  assignmentId: number;
  studentName: string;
  outputDir: string;
}

interface GeneratedPdf {
  filePath: string;
  fileName: string;
  assignmentName: string;
  courseName: string;
}

async function canvasFetch<T>(config: CanvasConfig, pathname: string): Promise<T> {
  const url = new URL(pathname, config.baseUrl);
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${config.accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`Canvas API ${response.status}: ${response.statusText}`);
  }

  return (await response.json()) as T;
}

async function fetchAssignment(
  config: CanvasConfig,
  courseId: number,
  assignmentId: number,
): Promise<CanvasAssignment> {
  return canvasFetch<CanvasAssignment>(
    config,
    `/api/v1/courses/${courseId}/assignments/${assignmentId}`,
  );
}

function extractFileIds(description: string): number[] {
  const pattern = /\/files\/(\d+)/g;
  const ids: number[] = [];
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(description)) !== null) {
    ids.push(parseInt(match[1]!, 10));
  }
  return [...new Set(ids)];
}

async function downloadFile(
  config: CanvasConfig,
  courseId: number,
  fileId: number,
  outputDir: string,
): Promise<string> {
  const fileInfo = await canvasFetch<CanvasFileInfo>(
    config,
    `/api/v1/courses/${courseId}/files/${fileId}`,
  );

  const response = await fetch(fileInfo.url);
  if (!response.ok) {
    throw new Error(`Failed to download file: ${response.statusText}`);
  }

  const buffer = Buffer.from(await response.arrayBuffer());
  const outputPath = path.join(outputDir, fileInfo.filename);
  await writeFile(outputPath, buffer);
  return outputPath;
}

export async function fetchAssignmentDetails(
  config: CanvasConfig,
  courseId: number,
  assignmentId: number,
): Promise<{ assignment: CanvasAssignment; attachedFileIds: number[] }> {
  const assignment = await fetchAssignment(config, courseId, assignmentId);
  const attachedFileIds = assignment.description
    ? extractFileIds(assignment.description)
    : [];

  return { assignment, attachedFileIds };
}

export async function downloadAssignmentFiles(
  config: CanvasConfig,
  courseId: number,
  fileIds: number[],
  outputDir: string,
): Promise<string[]> {
  const paths: string[] = [];
  for (const fileId of fileIds) {
    const filePath = await downloadFile(config, courseId, fileId, outputDir);
    paths.push(filePath);
  }
  return paths;
}

export async function listCourseAssignments(
  config: CanvasConfig,
  courseId: number,
): Promise<CanvasAssignment[]> {
  return canvasFetch<CanvasAssignment[]>(
    config,
    `/api/v1/courses/${courseId}/assignments?per_page=100&order_by=due_at`,
  );
}

export async function getStudentName(config: CanvasConfig): Promise<string> {
  const profile = await canvasFetch<{ name: string }>(
    config,
    "/api/v1/users/self/profile",
  );
  return profile.name;
}

export async function getCourseName(
  config: CanvasConfig,
  courseId: number,
): Promise<string> {
  const course = await canvasFetch<{ name: string }>(
    config,
    `/api/v1/courses/${courseId}`,
  );
  return course.name;
}

export { type CanvasAssignment, type GeneratePdfOptions, type GeneratedPdf };
