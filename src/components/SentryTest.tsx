import React from 'react';

export const SentryTest: React.FC = () => {
    const [shouldError, setShouldError] = React.useState(false);

    if (shouldError) {
        throw new Error("Sentry Test Error: This is a test error to verify Sentry integration.");
    }

    return (
        <button
            onClick={() => setShouldError(true)}
            className="fixed bottom-4 right-4 z-50 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors shadow-lg"
        >
            Test Sentry Error
        </button>
    );
};
