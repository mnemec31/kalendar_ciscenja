import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
    const token = localStorage.getItem("access_token");

    return token ? children : <Navigate to="/" />;
};

export default ProtectedRoute;