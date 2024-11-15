import { BrowserRouter, Routes, Route } from "react-router-dom";
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
        <Route path="/" element={<Login />} />

        <Route path="/calendar" element={
          <ProtectedRoute>
            <MyCalendar />
          </ProtectedRoute>} />
      </Routes>


    </BrowserRouter >
  );
};

export default App;
