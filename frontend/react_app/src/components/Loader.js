import React from "react";
import { PulseLoader } from "react-spinners";

export default function Loader({ text }) {
    return (
        <div className="mt-6 flex flex-col items-center">
            <PulseLoader color="#2563eb" />
            <p className="text-gray-700 mt-2">{text || "Loading..."}</p>
        </div>
    );
}
