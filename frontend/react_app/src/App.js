import React, { useState, useRef } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import Lottie from "lottie-react";
import { FaUpload, FaMicrophone, FaStop } from "react-icons/fa";
import SignPlayer from "./components/SignPlayer";
import AnimatedHeader from "./components/AnimatedHeader";
import Loader from "./components/Loader";
import recordAnim from "./assets/record.json";

function App() {
    const [mode, setMode] = useState("upload");
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [audioURL, setAudioURL] = useState(null);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // 🎙 Start recording
    const startRecording = async () => {
        setResult(null);
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => audioChunksRef.current.push(e.data);
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
                const audioUrl = URL.createObjectURL(audioBlob);
                setAudioURL(audioUrl);
                sendAudio(audioBlob);
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            alert("🎧 Microphone access denied or unavailable.");
        }
    };

    const stopRecording = () => {
        mediaRecorderRef.current?.stop();
        setIsRecording(false);
    };

    // 🔄 Send audio to backend
    const sendAudio = async (blob) => {
        setLoading(true);
        const form = new FormData();
        form.append("file", blob, "recording.webm");
        try {
            const res = await axios.post("/api/translate", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setResult(res.data);
        } catch (err) {
            alert("⚠️ Network Error: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    // 📂 Handle upload
    const handleUpload = async () => {
        if (!file) return alert("Please select an audio file first!");
        setLoading(true);
        const form = new FormData();
        form.append("file", file);
        try {
            const res = await axios.post("/api/translate", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setResult(res.data);
        } catch (err) {
            alert("⚠️ " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-blue-200 flex flex-col items-center p-6 font-sans">
            <AnimatedHeader />

            {/* Mode Switch */}
            <div className="flex gap-4 mb-6">
                <button
                    onClick={() => setMode("upload")}
                    className={`px-5 py-2 rounded-lg shadow-md transition ${mode === "upload"
                            ? "bg-blue-600 text-white"
                            : "bg-white text-blue-600 border border-blue-600"
                        }`}
                >
                    <FaUpload className="inline mr-2" /> Upload
                </button>

                <button
                    onClick={() => setMode("record")}
                    className={`px-5 py-2 rounded-lg shadow-md transition ${mode === "record"
                            ? "bg-blue-600 text-white"
                            : "bg-white text-blue-600 border border-blue-600"
                        }`}
                >
                    <FaMicrophone className="inline mr-2" /> Live Speech
                </button>
            </div>

            {/* Upload Mode */}
            <AnimatePresence mode="wait">
                {mode === "upload" && (
                    <motion.div
                        key="upload"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.4 }}
                        className="flex flex-col items-center"
                    >
                        <input
                            type="file"
                            accept="audio/*"
                            onChange={(e) => setFile(e.target.files[0])}
                            className="mb-4"
                        />
                        <button
                            onClick={handleUpload}
                            disabled={loading}
                            className="bg-blue-600 text-white px-6 py-2 rounded-lg shadow hover:bg-blue-700"
                        >
                            {loading ? "Processing..." : "Upload & Translate"}
                        </button>
                    </motion.div>
                )}

                {/* Record Mode */}
                {mode === "record" && (
                    <motion.div
                        key="record"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.4 }}
                        className="flex flex-col items-center"
                    >
                        {!isRecording ? (
                            <button
                                onClick={startRecording}
                                className="bg-green-600 text-white px-6 py-2 rounded-lg shadow hover:bg-green-700 flex items-center"
                            >
                                <FaMicrophone className="mr-2" /> Start Recording
                            </button>
                        ) : (
                            <button
                                onClick={stopRecording}
                                className="bg-red-600 text-white px-6 py-2 rounded-lg shadow hover:bg-red-700 flex items-center"
                            >
                                <FaStop className="mr-2" /> Stop Recording
                            </button>
                        )}

                        {isRecording && (
                            <div className="w-48 mt-4">
                                <Lottie animationData={recordAnim} loop />
                                <p className="text-sm text-gray-600 mt-2">Listening...</p>
                            </div>
                        )}

                        {audioURL && (
                            <audio
                                src={audioURL}
                                controls
                                className="mt-4 border rounded shadow w-72"
                            />
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Loader */}
            {loading && <Loader text="Translating speech..." />}

            {/* Result */}
            {result && (
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                    className="bg-white mt-6 p-6 rounded-xl shadow-md w-96 backdrop-blur-md bg-white/70"
                >
                    <h2 className="text-xl font-semibold text-blue-700 mb-2">Result</h2>
                    <p><strong>Input Text:</strong> {result.input_text}</p>
                    <p><strong>Matched Phrase:</strong> {result.match}</p>
                    <SignPlayer render={result} />
                </motion.div>
            )}
        </div>
    );
}

export default App;
