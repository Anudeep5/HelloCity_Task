import { useEffect, useMemo, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import Bubble from "./Bubble";
import PlaceCard from "./PlaceCard";
import { postChat, postFeedback } from "../api/hellocityApi";
import type { ChatMessage, PlaceCard as PlaceCardT } from "../api/types";

function getSessionId(): string {
    const key = "hellocity_session_id";
    let v = localStorage.getItem(key);
    if (!v) {
        v = uuidv4();
        localStorage.setItem(key, v);
    }
    return v;
}

export default function Chat() {
    const sessionId = useMemo(() => getSessionId(), []);
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: "assistant",
            text: "Hey! I’m HelloCity. What do you like doing when you go out in Miami?",
        },
    ]);

    const [input, setInput] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);

    const [pendingInterest, setPendingInterest] = useState<string | null>(null);
    const [examples, setExamples] = useState<PlaceCardT[] | null>(null);
    const [profile, setProfile] = useState<{ interests: string[] } | null>(
        null,
    );
    const [interests, setInterests] = useState<string[]>([]);

    const bottomRef = useRef<HTMLDivElement | null>(null);
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, examples, profile]);

    async function handleSend(text: string) {
        setLoading(true);
        try {
            const data = await postChat({
                session_id: sessionId,
                message: text,
            });

            setMessages((m) => [
                ...m,
                { role: "assistant", text: data.assistant_message },
            ]);
            setInterests(data.interests ?? []);

            if (data.onboarding_complete && data.profile) {
                setProfile(data.profile);
                setPendingInterest(null);
                setExamples(null);
                return;
            }

            if (
                data.interest_detected &&
                data.examples?.length &&
                data.interest_added
            ) {
                setPendingInterest(data.interest_added);
                setExamples(data.examples);
            } else {
                setPendingInterest(null);
                setExamples(null);
            }
        } catch (e: any) {
            setMessages((m) => [
                ...m,
                {
                    role: "assistant",
                    text: `Something went wrong. ${e?.message ?? ""}`.trim(),
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    async function handleFeedback(choice: "yes" | "no") {
        if (!pendingInterest) return;

        setLoading(true);
        try {
            const data = await postFeedback({
                session_id: sessionId,
                interest: pendingInterest,
                choice,
            });

            setMessages((m) => [
                ...m,
                { role: "assistant", text: data.assistant_message },
            ]);

            setPendingInterest(null);
            setExamples(null);
            setInterests(data.interests ?? interests);

            if (data.onboarding_complete && data.profile) {
                setProfile(data.profile);
            }
        } catch (e: any) {
            setMessages((m) => [
                ...m,
                {
                    role: "assistant",
                    text: `Something went wrong. ${e?.message ?? ""}`.trim(),
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        const text = input.trim();
        if (!text || loading) return;

        setInput("");
        setMessages((m) => [...m, { role: "user", text }]);
        handleSend(text);
    }

    const inputDisabled = loading || !!examples || !!profile;

    return (
        <div
            style={{
                minHeight: "100vh",
                background: "#050a14",
                display: "flex",
                justifyContent: "center",
            }}
        >
            <div
                style={{
                    width: "100%",
                    maxWidth: 460,
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                <div
                    style={{
                        padding: "14px 16px",
                        color: "white",
                        borderBottom: "1px solid rgba(255,255,255,0.08)",
                    }}
                >
                    <div style={{ fontWeight: 800, fontSize: 16 }}>
                        HelloCity
                    </div>
                    <div
                        style={{
                            fontSize: 12,
                            color: "rgba(255,255,255,0.7)",
                            marginTop: 4,
                        }}
                    >
                        Interests: {interests.length}/3
                    </div>
                </div>

                <div style={{ padding: 16, flex: 1, overflowY: "auto" }}>
                    {messages.map((m, idx) => (
                        <Bubble key={idx} role={m.role} text={m.text} />
                    ))}

                    {examples?.length ? (
                        <div style={{ marginTop: 12 }}>
                            <div
                                style={{
                                    color: "white",
                                    fontWeight: 700,
                                    marginBottom: 10,
                                }}
                            >
                                Miami picks for: {pendingInterest}
                            </div>

                            <div style={{ display: "grid", gap: 10 }}>
                                {examples.map((p, i) => (
                                    <PlaceCard key={i} p={p} />
                                ))}
                            </div>

                            <div
                                style={{
                                    display: "flex",
                                    gap: 10,
                                    marginTop: 12,
                                }}
                            >
                                <button
                                    onClick={() => void handleFeedback("yes")}
                                    disabled={loading}
                                    style={{
                                        flex: 1,
                                        borderRadius: 12,
                                        padding: 12,
                                        border: "none",
                                        background: "#1b5cff",
                                        color: "white",
                                        fontWeight: 700,
                                    }}
                                >
                                    Yes, that’s what I meant
                                </button>

                                <button
                                    onClick={() => void handleFeedback("no")}
                                    disabled={loading}
                                    style={{
                                        flex: 1,
                                        borderRadius: 12,
                                        padding: 12,
                                        border: "1px solid rgba(255,255,255,0.18)",
                                        background: "transparent",
                                        color: "white",
                                        fontWeight: 700,
                                    }}
                                >
                                    No
                                </button>
                            </div>

                            <div
                                style={{
                                    marginTop: 8,
                                    fontSize: 12,
                                    color: "rgba(255,255,255,0.65)",
                                }}
                            >
                                Confirm the examples first, then continue.
                            </div>
                        </div>
                    ) : null}

                    {profile ? (
                        <div
                            style={{
                                marginTop: 16,
                                padding: 14,
                                borderRadius: 14,
                                background: "#0b1220",
                                color: "white",
                            }}
                        >
                            <div style={{ fontWeight: 800, marginBottom: 8 }}>
                                Your profile
                            </div>
                            <pre
                                style={{
                                    margin: 0,
                                    whiteSpace: "pre-wrap",
                                    color: "rgba(255,255,255,0.85)",
                                }}
                            >
                                {JSON.stringify(profile, null, 2)}
                            </pre>
                        </div>
                    ) : null}

                    <div ref={bottomRef} />
                </div>

                <form
                    onSubmit={onSubmit}
                    style={{
                        padding: 12,
                        borderTop: "1px solid rgba(255,255,255,0.08)",
                    }}
                >
                    <div style={{ display: "flex", gap: 10 }}>
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={
                                loading ? "Thinking..." : "Type your answer..."
                            }
                            disabled={inputDisabled}
                            style={{
                                flex: 1,
                                padding: 12,
                                borderRadius: 12,
                                border: "1px solid rgba(255,255,255,0.12)",
                                background: "#0b1220",
                                color: "white",
                                outline: "none",
                            }}
                        />
                        <button
                            type="submit"
                            disabled={inputDisabled || !input.trim()}
                            style={{
                                padding: "0 14px",
                                borderRadius: 12,
                                border: "none",
                                background: "#1b5cff",
                                color: "white",
                                fontWeight: 800,
                            }}
                        >
                            Send
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
