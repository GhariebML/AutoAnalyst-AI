import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number; height?: string }> = ({
  rows = 3,
  height = 'h-24',
}) => {
  return (
    <div className="space-y-4 animate-pulse">
      {Array.from({ length: rows }).map((_, idx) => (
        <div
          key={idx}
          className={`w-full ${height} rounded-3xl bg-slate-900/60 border border-slate-800/80`}
        />
      ))}
    </div>
  );
};
