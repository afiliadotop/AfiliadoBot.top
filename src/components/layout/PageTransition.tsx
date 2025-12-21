import React from "react";
import { Outlet } from "react-router-dom";

export const PageTransition: React.FC<{ children?: React.ReactNode }> = React.memo(({ children }) => {
    return (
        <div className="animate-fadeIn">
            {children || <Outlet />}
        </div>
    );
});

PageTransition.displayName = 'PageTransition';
