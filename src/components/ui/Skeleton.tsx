import React from "react";

export const Skeleton: React.FC<{ className?: string }> = React.memo(({ className = "" }) => {
    return (
        <div
            className={`animate-pulse bg-slate-200 dark:bg-slate-800 rounded ${className}`}
            aria-label="Loading..."
        />
    );
});

Skeleton.displayName = 'Skeleton';
