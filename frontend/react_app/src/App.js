import React, { useState } from "react";
import axios from "axios";
import SignPlayer from "./components/SignPlayer";

function App() {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const upload = async () => {
        if (!file) return alert("Choose an audio file (.wav/.mp3)");
        setLoading(true);
        const form = new FormData();
        form.append("file", file, file.name);
        try {
            const res = await axios.post("/api/translate", form, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            setResult(res.data);
        } catch (err) {
            alert("Error: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: 20, fontFamily: "Arial" }}>
            <h2>Speech → Indian Sign Language (Demo)</h2>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            <button onClick={upload} disabled={loading} style={{ marginLeft: 10 }}>
                {loading ? "Processing..." : "Upload & Translate"}
            </button>

            {result && (
                <div style={{ marginTop: 24 }}>
                    <h3>Input text (auto):</h3>
                    <pre>{result.input_text}</pre>
                    <h4>Match:</h4>
                    <pre>{JSON.stringify(result.match, null, 2)}</pre>
                    <SignPlayer render={result.render} />
                </div>
            )}
        </div>
    );
}

export default App;
