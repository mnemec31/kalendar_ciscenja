import { useState } from "react";
import { login } from "./api/login.ts";
import { register } from "./api/register.ts";

const Login = () => {
    const [credentials, setCredentials] = useState({
        username: "",
        password: ""
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setCredentials((prevState) => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleLogin = async (e) => {
        e.preventDefault();

        try {
            const data = await login(credentials);
            console.log("Access Token:", data.access_token);
            localStorage.setItem("access_token", data.access_token);
        }
        catch (err) {
            console.error("Error:", err);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();

        try {
            const data = await register(credentials);
            localStorage.setItem("access_token", data.access_token);
        }
        catch (err) {
            console.error("Error:", err);
        }
    };

    return (
        <div>
            <h2>Login</h2>
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
                <button onClick={handleRegister}>Register</button>
                <button onClick={handleLogin}>Login</button>
            </form>
        </div>
    );
};

export default Login;
