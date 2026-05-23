"use client";

import { use } from "react";
import MissionDetail from "@/components/MissionDetail";

interface Props {
  params: Promise<{ id: string }>;
}

export default function MissionPage({ params }: Props) {
  const { id } = use(params);
  return <MissionDetail missionId={id} />;
}