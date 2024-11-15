import { useState } from "react";
import toast from "react-hot-toast";
import "../index.css"

const ImportFromURL = ({ token, setTrigger }) => {
    const [url, setUrl] = useState("");

    const handleInputChange = (event) => {
        setUrl(event.target.value);
    };

    const handleSubmit = async () => {
        if (!url) {
            toast.error("Please enter a URL before submitting.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/import-from-url/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ url }) // Send the URL in JSON format
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            toast.success("URL imported successfully!");
            setTrigger(prev => !prev)
            console.log("Response data:", data);
        } catch (error) {
            console.error("Error importing URL:", error);
            toast.error("Failed to import URL.");
        }
    };

    return (
        <div className="importSection">
            <input
                className="urlInput"
                type="text"
                value={url}
                onChange={handleInputChange}
                placeholder="Enter URL"
            />
            <button className="importButton" onClick={handleSubmit}>Import</button>
        </div>
    );
};

export default ImportFromURL;
