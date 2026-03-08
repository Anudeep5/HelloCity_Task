import { useEffect, useMemo, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import { postChat, postFeedback, postReset } from "../../api/hellocityApi";
import type { ChatMessage, PlaceCard as PlaceCardT } from "../../api/types";

type Profile = { interests: string[] } | null;

function getSessionId(): string {
    const key = "hellocity_session_id";

    let value = sessionStorage.getItem(key);
    if (!value) {
        value = uuidv4();
        sessionStorage.setItem(key, value);
    }

    return value;
}

const INITIAL_ASSISTANT_MESSAGE =
    "Hey! I’m HelloCity. What do you like doing when you go out in Miami?";

export function useHelloCityChat() {
    const sessionId = useMemo(() => getSessionId(), []);

    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: "assistant",
            text: INITIAL_ASSISTANT_MESSAGE,
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const [pendingInterest, setPendingInterest] = useState<string | null>(null);
    const [examples, setExamples] = useState<PlaceCardT[] | null>(null);
    const [profile, setProfile] = useState<Profile>(null);
    const [interests, setInterests] = useState<string[]>([]);

    const bottomRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, examples, profile]);

    const inputDisabled = loading || !!examples || !!profile;

    function clearExampleState() {
        setPendingInterest(null);
        setExamples(null);
    }

    function applyResponseState(data: {
        assistant_message: string;
        interests?: string[];
        onboarding_complete: boolean;
        profile?: { interests: string[] } | null;
        interest_detected?: boolean;
        interest_added?: string | null;
        examples?: PlaceCardT[] | null;
    }) {
        setMessages((prev) => [
            ...prev,
            { role: "assistant", text: data.assistant_message },
        ]);

        setInterests(data.interests ?? []);

        if (data.onboarding_complete && data.profile) {
            setProfile(data.profile);
            clearExampleState();
            return;
        }

        if (
            data.interest_detected &&
            data.interest_added &&
            data.examples?.length
        ) {
            setPendingInterest(data.interest_added);
            setExamples(data.examples);
            return;
        }

        clearExampleState();
    }

    async function sendMessage(text: string) {
        setLoading(true);

        try {
            const data = await postChat({
                session_id: sessionId,
                message: text,
            });

            applyResponseState(data);
        } catch (error: any) {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: `Something went wrong. ${error?.message ?? ""}`.trim(),
                },
            ]);
            clearExampleState();
        } finally {
            setLoading(false);
        }
    }

    async function submitInput() {
        const text = input.trim();
        if (!text || loading) return;

        setInput("");
        setMessages((prev) => [...prev, { role: "user", text }]);
        await sendMessage(text);
    }

    async function sendFeedback(choice: "yes" | "no") {
        if (!pendingInterest) return;

        setLoading(true);

        try {
            const data = await postFeedback({
                session_id: sessionId,
                interest: pendingInterest,
                choice,
            });

            applyResponseState(data);
        } finally {
            setLoading(false);
        }
    }

    async function resetChat() {
        if (loading) return;

        setLoading(true);

        try {
            await postReset(sessionId);

            setMessages([
                {
                    role: "assistant",
                    text: INITIAL_ASSISTANT_MESSAGE,
                },
            ]);
            setInput("");
            clearExampleState();
            setProfile(null);
            setInterests([]);
        } catch (error: any) {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: `Couldn’t reset right now. ${error?.message ?? ""}`.trim(),
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    return {
        messages,
        input,
        setInput,
        loading,
        pendingInterest,
        examples,
        profile,
        interests,
        inputDisabled,
        bottomRef,
        submitInput,
        sendFeedback,
        resetChat,
    };
}
