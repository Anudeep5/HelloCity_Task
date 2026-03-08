import Bubble from "../Bubble";
import ChatExamples from "./ChatExamples";
import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ChatProfile from "./ChatProfile";
import { useHelloCityChat } from "./useHelloCityChat";

export default function Chat() {
    const {
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
    } = useHelloCityChat();

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        void submitInput();
    }

    return (
        <div className="hc-app">
            <div className="hc-shell">
                <ChatHeader
                    interestsCount={interests.length}
                    loading={loading}
                    onReset={() => void resetChat()}
                />

                <div className="hc-body">
                    {messages.map((message, index) => (
                        <Bubble
                            key={index}
                            role={message.role}
                            text={message.text}
                        />
                    ))}

                    {examples?.length && pendingInterest ? (
                        <ChatExamples
                            pendingInterest={pendingInterest}
                            examples={examples}
                            loading={loading}
                            onYes={() => void sendFeedback("yes")}
                            onNo={() => void sendFeedback("no")}
                        />
                    ) : null}

                    {profile ? <ChatProfile profile={profile} /> : null}

                    <div ref={bottomRef} />
                </div>

                <ChatInput
                    input={input}
                    loading={loading}
                    disabled={inputDisabled}
                    showExamplesHint={!!examples?.length}
                    onChange={setInput}
                    onSubmit={handleSubmit}
                />
            </div>
        </div>
    );
}
