import React from 'react';

interface ProgressBarProps {
    progress: number; // 0-100
    label?: string;
    showPercentage?: boolean;
    className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = React.memo(({
    progress,
    label,
    showPercentage = true,
    className = ''
}) => {
    const clampedProgress = Math.min(100, Math.max(0, progress));

    return (
        <div className={`w-full ${className}`}>
            {(label || showPercentage) && (
                <div className="flex justify-between items-center mb-2">
                    {label && <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{label}</span>}
                    {showPercentage && <span className="text-sm text-slate-500 dark:text-slate-400">{Math.round(clampedProgress)}%</span>}
                </div>
            )}
            <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 transition-all duration-300 ease-out rounded-full"
                    style={{ width: `${clampedProgress}%` }}
                />
            </div>
        </div>
    );
});

ProgressBar.displayName = 'ProgressBar';
