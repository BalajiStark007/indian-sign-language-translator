import React, { useState, useRef } from "react";
import axios from "axios";
import SignPlayer from "./components/SignPlayer";

function App() {
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [audioURL, setAudioURL] = useState(null);
    const [mode, setMode] = useState("upload"); // 'upload' or 'record'

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // ----------------------------
    // 🎙 Start / Stop Recording
    // ----------------------------
    const startRecording = async () => {
        setResult(null);
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
                const audioUrl = URL.createObjectURL(audioBlob);
                setAudioURL(audioUrl);
                sendAudioBlob(audioBlob);
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            alert("Microphone access denied or unavailable.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    // ----------------------------
    // 🔄 Send audio Blob to backend
    // ----------------------------
    const sendAudioBlob = async (audioBlob) => {
        setLoading(true);
        const form = new FormData();
        form.append("file", audioBlob, "recording.webm");

        try {
            const res = await axios.post("/api/translate", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setResult(res.data);
        } catch (err) {
            alert("Error: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    // ----------------------------
    // 📂 Upload existing audio file
    // ----------------------------
    const handleUpload = async () => {
        if (!file) return alert("Choose an audio file first");
        setLoading(true);
        const form = new FormData();
        form.append("file", file);
        try {
            const res = await axios.post("/api/translate", form, {
                headers: { "Content-Type": "multipart/form-data" },
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
            <h1 className="text-3xl font-bold mb-4 text-blue-700">
                Speech → Indian Sign Language Translator
            </h1>

            {/* Toggle mode */}
            <div className="flex gap-4 mb-6">
                <button
                    onClick={() => setMode("upload")}
                    className={`px-4 py-2 rounded-lg ${mode === "upload"
                            ? "bg-blue-600 text-white"
                            : "bg-white text-blue-600 border border-blue-600"
                        }`}
                >
                    📂 Upload File
                </button>
                <button
                    onClick={() => setMode("record")}
                    className={`px-4 py-2 rounded-lg ${mode === "record"
                            ? "bg-blue-600 text-white"
                            : "bg-white text-blue-600 border border-blue-600"
                        }`}
                >
                    🎙 Live Speech
                </button>
            </div>

            {/* Upload Mode */}
            {mode === "upload" && (
                <div className="flex flex-col items-center">
                    <input type="file" onChange={(e) => setFile(e.target.files[0])} />
                    <button
                        onClick={handleUpload}
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-2 mt-4 rounded-lg shadow hover:bg-blue-700"
                    >
                        {loading ? "Processing..." : "Upload & Translate"}
                    </button>
                </div>
            )}

            {/* Recording Mode */}
            {mode === "record" && (
                <div className="flex flex-col items-center">
                    {!isRecording ? (
                        <button
                            onClick={startRecording}
                            disabled={loading}
                            className="bg-green-600 text-white px-6 py-2 rounded-lg shadow hover:bg-green-700"
                        >
                            🎤 Start Recording
                        </button>
                    ) : (
                        <button
                            onClick={stopRecording}
                            className="bg-red-600 text-white px-6 py-2 rounded-lg shadow hover:bg-red-700"
                        >
                            ⏹ Stop Recording
                        </button>
                    )}

                    {audioURL && (
                        <audio
                            src={audioURL}
                            controls
                            className="mt-4 border rounded shadow w-72"
                        />
                    )}

                    {loading && <p className="text-gray-600 mt-4">Translating...</p>}
                </div>
            )}

            {/* Results */}
            {result && (
                <div className="bg-white mt-6 p-6 rounded-lg shadow-md w-96">
                    <h2 className="text-xl font-semibold text-blue-700 mb-2">Result</h2>
                    <p><strong>Input text:</strong> {result.input_text}</p>
                    <p><strong>Matched phrase:</strong> {result.match}</p>
                    <SignPlayer render={result} />
                </div>
            )}
        </div>
    );
}

export default App;
