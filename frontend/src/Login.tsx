import { useState } from "react";
import { login } from "./api/login.ts";
import { register } from "./api/register.ts";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

const Login = () => {
    const [credentials, setCredentials] = useState({
        username: "",
        password: ""
    });
    const navigate = useNavigate();

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = event.target;
        setCredentials((prevState) => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleLogin = async (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();

        try {
            const data = await login(credentials);
            localStorage.setItem("access_token", data.access_token);
            toast.success("Logged in! Enjoy cleaning 🧽🧽🧽")
            navigate("/calendar");
        }
        catch (err) {
            toast.error(`Login failed!`)
        }
    };

    const handleRegister = async (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();

        try {
            const data = await register(credentials);
            localStorage.setItem("access_token", data.access_token);
            toast.success("Register completed! Now login!")
        }
        catch (err) {
            toast.error("Register failed!")
        }
    };

    return (
        <div className="login">
            <form>
                <div>
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={credentials.username}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={credentials.password}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="flexContainer">
                    <button onClick={handleRegister}>Register</button>
                    <button onClick={handleLogin}>Login</button>
                </div>
            </form>
        </div>
    );
};

export default Login;
