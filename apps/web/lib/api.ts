const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RuntimeStatus {
  api: { status: string };
  floci: { status: string; endpoint: string; checkedAt: string };
  database: { status: string };
  localOnly: { status: string; endpoint: string };
}

export interface Mission {
  id: string;
  title: string;
  summary: string;
  difficulty: string;
  services: string[];
  xp: number;
  status: string;
  prerequisites?: string[];
  estimatedMinutes: number;
}

export interface MissionDetail {
  mission: {
    id: string;
    order: number;
    title: string;
    summary: string;
    difficulty: string;
    services: string[];
    xp: number;
    estimatedMinutes: number;
    status: string;
    story: string;
    learningObjectives: string[];
    commands: { id: string; label: string; command: string }[];
    steps: MissionStep[];
    hints?: { id: string; title: string; text?: string; isUsed: boolean; penaltyXp: number }[];
    progress: {
      status: string;
      attempts: number;
      hintsUsed: string[];
      xpAwarded: number;
      startedAt: string | null;
      completedAt: string | null;
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

export interface ValidationResult {
  missionId: string;
  passed: boolean;
  status: string;
  xpAwarded: number;
  attemptNumber: number;
  checks: { id: string; type: string; passed: boolean; message: string }[];
  unlockedMissionIds: string[];
  scope?: "mission" | "step";
  stepId?: string | null;
}

export interface Profile {
  id: string;
  displayName: string;
  totalXp: number;
  completedMissionIds?: string[];
  badges?: { id: string; title: string; awardedAt: string }[];
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

export async function resetMission(id: string, mode: string = "practice"): Promise<{ missionId: string; status: string; resourcesRemoved: string[] }> {
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
