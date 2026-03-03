import type { Role } from "../api/types";

export default function Bubble({ role, text }: { role: Role; text: string }) {
    return (
        <div className={`hc-bubbleRow ${role}`}>
            <div className={`hc-bubble ${role}`}>{text}</div>
        </div>
    );
}
