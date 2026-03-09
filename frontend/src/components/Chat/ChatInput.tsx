import { useEffect, useRef } from "react";

type ChatInputProps = {
    input: string;
    loading: boolean;
    disabled: boolean;
    showExamplesHint: boolean;
    onChange: (value: string) => void;
    onSubmit: (e: React.FormEvent) => void;
};

export default function ChatInput({
    input,
    loading,
    disabled,
    showExamplesHint,
    onChange,
    onSubmit,
}: ChatInputProps) {
    const inputRef = useRef<HTMLInputElement | null>(null);

    // focus when component loads
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    // focus again after assistant reply
    useEffect(() => {
        if (!loading && !disabled) {
            inputRef.current?.focus();
        }
    }, [loading, disabled]);

    return (
        <form className="hc-footer" onSubmit={onSubmit}>
            <div className="hc-inputRow">
                <input
                    ref={inputRef}
                    className="hc-input"
                    value={input}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={loading ? "Thinking..." : "Type or speak..."}
                    disabled={disabled}
                />

                <button
                    className="hc-send"
                    type="submit"
                    disabled={disabled || !input.trim()}
                >
                    Send
                </button>
            </div>

            {showExamplesHint ? (
                <div className="hc-hint">
                    You can type again after confirming.
                </div>
            ) : null}
        </form>
    );
}
