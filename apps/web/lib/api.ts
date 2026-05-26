const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RuntimeStatus {
  api: { status: string };
  floci: { status: string; endpoint: string; checkedAt: string };
  database: { status: string };
  localOnly: { status: string; endpoint: string };
}

export interface Mission {
  id: string;
  order?: number;
  module?: string;
  submodule?: string;
  missionType?: MissionType;
  capability?: string;
  title: string;
  summary: string;
  difficulty: string;
  services: string[];
  xp: number;
  status: string;
  required?: boolean;
  prerequisites?: string[];
  estimatedMinutes: number;
}

export type MissionStatus = "locked" | "available" | "started" | "completed";
export type CapabilityStatus = "locked" | "in_progress" | "unlocked";
export type MissionType = "lesson" | "module_capstone" | "final_capstone";
export type StepStatus = "not_started" | "active" | "passed" | "failed" | "no_checks" | "blocked" | "stale";

export interface CheckResult {
  id: string;
  type: string;
  passed: boolean;
  message: string;
}

export interface CourseMission {
  id: string;
  order: number;
  submodule?: string;
  title: string;
  missionType: MissionType;
  required: boolean;
  status: MissionStatus;
  prerequisites?: string[];
}

export interface CourseModule {
  id: string;
  order: number;
  title: string;
  summary: string;
  required: boolean;
  capability: string;
  capabilityLabel: string;
  status: MissionStatus;
  requiredLessonsCompleted: number;
  requiredLessonsTotal: number;
  requiredCapstonesCompleted: number;
  requiredCapstonesTotal: number;
  capstoneMissionId: string | null;
  capstoneRequired: boolean;
  missions: CourseMission[];
}

export interface CourseProgress {
  status: "not_started" | "in_progress" | "completed";
  requiredLessonsCompleted: number;
  requiredLessonsTotal: number;
  requiredCapstonesCompleted: number;
  requiredCapstonesTotal: number;
  xp: number;
  nextMissionId: string | null;
  completedAt: string | null;
}

export interface CapabilityProgress {
  id: string;
  label: string;
  status: CapabilityStatus;
  moduleId: string;
  missionIds: string[];
}

export interface CourseResponse {
  course: {
    id: string;
    title: string;
    summary: string;
    progress: CourseProgress;
    modules: CourseModule[];
    capabilities: CapabilityProgress[];
  };
}

export interface MissionDetail {
  mission: {
    id: string;
    order: number;
    module?: string;
    submodule?: string;
    missionType?: MissionType;
    capability?: string;
    title: string;
    summary: string;
    difficulty: string;
    services: string[];
    xp: number;
    estimatedMinutes: number;
    required?: boolean;
    prerequisites?: string[];
    status: string;
    story: string;
    motivation?: string | null;
    theory?: string | null;
    thoughtProcess?: string | null;
    debrief?: string | null;
    learningObjectives: string[];
    commands: { id: string; label: string; command: string }[];
    steps: MissionStep[];
    hints?: MissionHint[];
    stepProgress?: StepProgress[];
    helpUsage?: HelpUsage[];
    capstoneScore?: CapstoneScore | null;
    progress: {
      status: string;
      attempts: number;
      xpAwarded: number;
      startedAt: string | null;
      completedAt: string | null;
      capstoneScore?: CapstoneScore | null;
    };
  };
}

export interface MissionStep {
  id: string;
  title: string;
  goal: string;
  why?: string | null;
  targetState: { label: string; value: string }[];
  action: string;
  commandId: string;
  checkIds: string[];
  success?: string | null;
  notes?: string | null;
}

export interface StepProgress {
  stepId: string;
  status: StepStatus;
  lastValidatedAt: string | null;
  attempts: number;
  latestChecks: CheckResult[];
}

export interface HelpUsage {
  hintId: string;
  level: string;
  usedAt: string;
}

export interface MissionHint {
  id: string;
  title: string;
  level?: "nudge" | "diagnosis" | "repair" | string;
  appliesToChecks?: string[];
  text?: string;
  revealed?: boolean;
  isUsed?: boolean;
  penaltyXp: number;
}

export interface ValidationResult {
  missionId: string;
  passed: boolean;
  status: string;
  xpAwarded: number;
  attemptNumber: number;
  checks: CheckResult[];
  unlockedMissionIds: string[];
  scope?: "mission" | "step";
  stepId?: string | null;
  message?: string | null;
  capstoneScore?: CapstoneScore | null;
}

export type ResetMode = "resources" | "progress" | "resources_and_progress";

export interface ResetResult {
  missionId: string;
  mode: ResetMode;
  deleted: { type: string; id: string; status: "deleted" }[];
  skipped: { type?: string; id?: string; status?: string; message?: string }[];
  failed: { type: string; id: string; status: "error"; message: string }[];
}

export interface CapstoneScore {
  score?: number | null;
  latestScore?: number | null;
  bestScore?: number | null;
  masteryLevel?: string | null;
  latestMasteryLevel?: string | null;
  bestMasteryLevel?: string | null;
  dimensions?: {
    id?: string;
    label?: string;
    score?: number | null;
    maxScore?: number | null;
    notes?: string | null;
  }[];
  localSafetyPassed?: boolean | null;
  bestLocalSafetyPassed?: boolean | null;
}

export interface Profile {
  id: string;
  displayName: string;
  totalXp: number;
  completedMissionIds?: string[];
  badges?: { id: string; title?: string; label?: string; awardedAt?: string; earnedAt?: string }[];
  courseProgress?: CourseProgress;
}

export async function getRuntimeStatus(): Promise<RuntimeStatus> {
  const res = await fetch(`${API_BASE}/runtime/status`);
  if (!res.ok) throw new Error("Failed to fetch runtime status");
  return res.json();
}

export async function getMissions(): Promise<{ missions: Mission[] }> {
  const res = await fetch(`${API_BASE}/missions`);
  if (!res.ok) throw new Error("Failed to fetch missions");
  return res.json();
}

export async function getCourse(): Promise<CourseResponse> {
  const res = await fetch(`${API_BASE}/course`);
  if (!res.ok) throw new Error("Failed to fetch course");
  return res.json();
}

export async function getMission(id: string): Promise<MissionDetail> {
  const res = await fetch(`${API_BASE}/missions/${id}`);
  if (!res.ok) throw new Error("Failed to fetch mission");
  return res.json();
}

export async function startMission(id: string): Promise<{ missionId: string; status: string; startedAt: string }> {
  const res = await fetch(`${API_BASE}/missions/${id}/start`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to start mission");
  return res.json();
}

export async function validateMission(id: string, stepId?: string): Promise<ValidationResult> {
  const res = await fetch(`${API_BASE}/missions/${id}/validate`, {
    method: "POST",
    headers: stepId ? { "Content-Type": "application/json" } : undefined,
    body: stepId ? JSON.stringify({ stepId }) : undefined,
  });
  if (!res.ok) throw new Error("Failed to validate mission");
  return res.json();
}

export async function resetMission(id: string, mode: ResetMode): Promise<ResetResult> {
  const res = await fetch(`${API_BASE}/missions/${id}/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
  if (!res.ok) throw new Error("Failed to reset mission");
  return res.json();
}

export async function useHint(missionId: string, hintId: string): Promise<{ missionId: string; hint: { id: string; title: string; text: string; penaltyXp: number; isUsed: boolean }; possibleXp: number }> {
  const res = await fetch(`${API_BASE}/missions/${missionId}/hints/${hintId}/use`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to use hint");
  return res.json();
}

export async function getProfile(): Promise<{ profile: Profile }> {
  const res = await fetch(`${API_BASE}/profile`);
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json();
}

export interface ChatMessage {
  role: "user" | "ai";
  content: string;
  createdAt: string;
}

export async function getChatHistory(
  missionId: string,
): Promise<{ messages: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/missions/${missionId}/chat`);
  if (!res.ok) throw new Error("Failed to fetch chat history");
  return res.json();
}

export async function sendChatMessage(
  missionId: string,
  message: string,
): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE}/missions/${missionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("Failed to send chat message");
  return res.json();
}

export async function useLearnMore(
  missionId: string,
  itemId: string,
): Promise<{ missionId: string; itemId: string; alreadyUsed: boolean; xpAwarded: number }> {
  const res = await fetch(`${API_BASE}/missions/${missionId}/learn/${itemId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to use learn more");
  return res.json();
}
