interface TrackedObjectsListProps {
  tracks: { track_id: number; label: string; confidence: number }[];
}

export function TrackedObjectsList({ tracks }: TrackedObjectsListProps) {
  if (tracks.length === 0) {
    return (
      <p className="text-center text-sm text-slate-500">
        No objects currently tracked.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {tracks.map((track) => (
        <div
          key={track.track_id}
          className="flex items-center justify-between rounded-lg border bg-white px-4 py-2.5"
        >
          <span className="text-sm font-medium capitalize text-slate-900">
            {track.label} #{track.track_id}
          </span>
          <span className="text-sm text-slate-500">
            {Math.round(track.confidence * 100)}%
          </span>
        </div>
      ))}
    </div>
  );
}
