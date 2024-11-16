import { useState, Dispatch, SetStateAction } from "react";
import toast from "react-hot-toast";
import "../index.css"

const UploadButton = ({ token, setTrigger }: { token: string, setTrigger: Dispatch<SetStateAction<boolean>> }) => {
    const [file, setFile] = useState(null);

    const handleFileChange = (event: any) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            toast.error("Please select a file before uploading.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:3107/import-calendar", {
                method: "POST",
                headers: {
                    authorization: `Bearer ${token}`
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Error uploading file: ${response.status}`);
            }

            toast.success('Successfully uploaded!')
            setTrigger(prev => !prev)

        } catch (error) {
            console.error("Error uploading file:", error);
            toast.error("Failed to upload file.");
        }
    };

    return (
        <div className="uploadSection">
            <input className="fileInput" type="file" accept=".ics" onChange={handleFileChange} />
            <button className="uploadButton" onClick={handleUpload}>Upload</button>
        </div>
    );
};

export default UploadButton;
