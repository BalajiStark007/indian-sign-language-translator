import React, { useState, useEffect } from "react";

export default function SignPlayer({ render }) {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        if (render?.type === "letters" && render.urls?.length) {
            const interval = setInterval(() => {
                setIndex((prev) => (prev + 1) % render.urls.length);
            }, 800);
            return () => clearInterval(interval);
        }
    }, [render]);

    if (!render) return null;

    if (render.type === "gif") {
        return (
            <div>
                <h4 className="font-semibold">Sign (GIF):</h4>
                <img
                    src={render.url}
                    alt="ISL sign"
                    className="rounded-lg border shadow max-w-full"
                />
            </div>
        );
    }

    if (render.type === "letters") {
        return (
            <div>
                <h4 className="font-semibold">Spelled Letters:</h4>
                {render.urls?.length > 0 && (
                    <img
                        src={render.urls[index]}
                        alt="letter"
                        className="w-24 h-24 border rounded-lg shadow"
                    />
                )}
            </div>
        );
    }

    return <p className="italic text-gray-600">No matching sign found.</p>;
}
