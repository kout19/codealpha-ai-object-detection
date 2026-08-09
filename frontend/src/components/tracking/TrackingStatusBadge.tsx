import { Badge } from "@/components/ui/badge";
import type { TrackingUIStatus } from "@/types/tracking";

const STATUS_CONFIG: Record <
 TrackingUIStatus,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  idle: { label: "Ready", variant: "outline" },
  starting: { label: "Starting…", variant: "secondary" },
  tracking: { label: "Tracking", variant: "default" },
  stopping: { label: "Stopping…", variant: "secondary" },
  error: { label: "Error", variant: "destructive" },
};

export function TrackingStatusBadge({ status }: { status: TrackingUIStatus }) {
  const config = STATUS_CONFIG[status];
  return <Badge variant={config.variant}>● {config.label}</Badge>;
}