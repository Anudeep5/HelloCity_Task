import type { Role } from "../api/types";

export default function Bubble({ role, text }: { role: Role; text: string }) {
    const isUser = role === "user";
    return (
        <div
            style={{
                display: "flex",
                justifyContent: isUser ? "flex-end" : "flex-start",
                marginBottom: 10,
            }}
        >
            <div
                style={{
                    maxWidth: "80%",
                    padding: "10px 12px",
                    borderRadius: 14,
                    background: isUser ? "#1b5cff" : "#111827",
                    color: "white",
                    fontSize: 14,
                    lineHeight: 1.35,
                    whiteSpace: "pre-wrap",
                }}
            >
                {text}
            </div>
        </div>
    );
}
