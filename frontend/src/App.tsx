import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login.js";
import MyCalendar from "./MyCalendar.tsx";
import "../index.css";
import ProtectedRoute from "./ProtectedRoute.tsx";
import { Toaster } from "react-hot-toast"

const App = () => {
  return (
    <BrowserRouter>
      <Toaster
        position="bottom-center"
        reverseOrder={false}
      />
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/" element={
          <ProtectedRoute>
            <MyCalendar />
          </ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>


    </BrowserRouter >
  );
};

export default App;
