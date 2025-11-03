import React from "react";

export default function SignPlayer({ render }) {
    if (render.gif) {
        return (
            <div className="mt-4">
                <img src={render.gif} alt="ISL sign" className="rounded-lg shadow" />
            </div>
        );
    }

    if (render.letters) {
        return (
            <div className="flex flex-wrap gap-2 mt-4 justify-center">
                {render.letters.map((u, i) => (
                    <img key={i} src={u} alt={`letter-${i}`} className="w-12 h-12" />
                ))}
            </div>
        );
    }

    return <p>No matching sign found.</p>;
}
