import AppShell from "@/components/AppShell";
import MissionMap from "@/components/MissionMap";
import XpSummary from "@/components/XpSummary";

export default function HomePage() {
  return (
    <AppShell>
      <div className="grid gap-8 lg:grid-cols-4">
        <div className="lg:col-span-3">
          <MissionMap />
        </div>
        <div className="lg:col-span-1">
          <XpSummary />
        </div>
      </div>
    </AppShell>
  );
}
