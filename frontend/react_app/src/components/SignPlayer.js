import React from "react";

export default function SignPlayer({ render }) {
    if (!render) return null;

    if (render.type === "gif") {
        return (
            <div>
                <h4>Sign (GIF):</h4>
                <img src={render.url} alt="ISL sign" style={{ maxWidth: 400 }} />
            </div>
        );
    }

    if (render.type === "letters") {
        return (
            <div>
                <h4>Spelled Letters:</h4>
                <div style={{ display: "flex", gap: 8 }}>
                    {render.urls && render.urls.map((u, i) => (
                        <img src={u} key={i} alt={`letter-${i}`} style={{ width: 80, height: 80 }} />
                    ))}
                </div>
            </div>
        );
    }

    return <div><em>No matching sign found.</em></div>;
}
