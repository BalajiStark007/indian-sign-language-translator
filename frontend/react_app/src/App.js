import React, { useState } from "react";
import axios from "axios";
import SignPlayer from "./components/SignPlayer";

function App() {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleDrop = (e) => {
        e.preventDefault();
        setFile(e.dataTransfer.files[0]);
    };

    const handleDragOver = (e) => e.preventDefault();

    const upload = async () => {
        if (!file) return alert("Choose an audio file (.wav/.mp3)");
        setLoading(true);
        setProgress(0);
        setResult(null);

        const form = new FormData();
        form.append("file", file, file.name);

        try {
            const res = await axios.post("/api/translate", form, {
                headers: { "Content-Type": "multipart/form-data" },
                onUploadProgress: (progressEvent) => {
                    const percent = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    setProgress(percent);
                },
            });
            setResult(res.data);
        } catch (err) {
            alert("Error: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6 font-sans">
            <h1 className="text-3xl font-bold mb-6 text-blue-700">
                Speech → Indian Sign Language Translator
            </h1>

            {/* Drag and drop box */}
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="border-2 border-dashed border-blue-400 w-96 h-40 flex items-center justify-center bg-white mb-4 cursor-pointer rounded-lg shadow"
            >
                {file ? (
                    <p className="text-gray-700">{file.name}</p>
                ) : (
                    <p className="text-gray-400">Drag & drop audio file here</p>
                )}
            </div>

            {/* Upload button */}
            <input
                type="file"
                accept="audio/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="mb-4"
            />
            <button
                onClick={upload}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg shadow hover:bg-blue-700"
            >
                {loading ? "Processing..." : "Upload & Translate"}
            </button>

            {/* Progress bar */}
            {loading && (
                <div className="w-96 mt-4">
                    <div className="bg-gray-300 h-3 rounded">
                        <div
                            className="bg-blue-600 h-3 rounded"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{progress}%</p>
                </div>
            )}

            {/* Results */}
            {result && (
                <div className="bg-white mt-6 p-6 rounded-lg shadow-md w-96">
                    <h2 className="text-xl font-semibold text-blue-700 mb-2">Result</h2>
                    <p>
                        <strong>Input text:</strong> {result.input_text}
                    </p>
                    <p>
                        <strong>Matched phrase:</strong> {result.match.phrase} (
                        {result.match.method}, score: {result.match.score})
                    </p>
                    <div className="mt-4">
                        <SignPlayer render={result.render} />
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
