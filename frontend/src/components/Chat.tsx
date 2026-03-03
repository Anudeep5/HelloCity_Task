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
            text: "Welcome to HelloCity. What do you like doing when you go out in Miami?",
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

    const inputDisabled = loading || !!examples || !!profile;

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
            setPendingInterest(null);
            setExamples(null);
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
        void handleSend(text);
    }

    return (
        <div className="hc-app">
            <div className="hc-shell">
                {/* Header */}
                <div className="hc-header">
                    <div className="hc-brandRow">
                        <div>
                            <div className="hc-title">
                                Hello<span className="hc-city">City</span>
                            </div>
                            <div className="hc-sub">
                                Interests: {interests.length}/3
                            </div>
                        </div>
                        <div className="hc-pill">Miami</div>
                    </div>
                </div>

                {/* Body */}
                <div className="hc-body">
                    {messages.map((m, idx) => (
                        <Bubble key={idx} role={m.role} text={m.text} />
                    ))}

                    {/* Examples + Yes/No */}
                    {examples?.length ? (
                        <div>
                            <div className="hc-sectionTitle">
                                Emily’s Picks: {pendingInterest}
                            </div>

                            <div className="hc-cardGrid">
                                {examples.map((p, i) => (
                                    <PlaceCard key={i} p={p} />
                                ))}
                            </div>

                            <div className="hc-actions">
                                <button
                                    className="hc-btn hc-btnPrimary"
                                    onClick={() => void handleFeedback("yes")}
                                    disabled={loading}
                                    type="button"
                                >
                                    Yes, that’s what I meant
                                </button>

                                <button
                                    className="hc-btn hc-btnGhost"
                                    onClick={() => void handleFeedback("no")}
                                    disabled={loading}
                                    type="button"
                                >
                                    No
                                </button>
                            </div>

                            <div className="hc-hint">
                                Confirm the picks first, then continue.
                            </div>
                        </div>
                    ) : null}

                    {/* Profile */}
                    {profile ? (
                        <div className="hc-profile">
                            <div className="hc-profileBody">
                                <div className="hc-profileTitle">
                                    Your profile
                                </div>
                                <pre className="hc-profilePre">
                                    {JSON.stringify(profile, null, 2)}
                                </pre>
                            </div>
                        </div>
                    ) : null}

                    <div ref={bottomRef} />
                </div>

                {/* Footer input */}
                <form className="hc-footer" onSubmit={onSubmit}>
                    <div className="hc-inputRow">
                        <input
                            className="hc-input"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={
                                loading ? "Thinking..." : "Type or speak..."
                            }
                            disabled={inputDisabled}
                        />
                        <button
                            className="hc-send"
                            type="submit"
                            disabled={inputDisabled || !input.trim()}
                        >
                            Send
                        </button>
                    </div>
                    {examples?.length ? (
                        <div className="hc-hint">
                            You can type again after confirming.
                        </div>
                    ) : null}
                </form>
            </div>
        </div>
    );
}
