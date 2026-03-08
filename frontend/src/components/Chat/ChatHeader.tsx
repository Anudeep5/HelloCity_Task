type ChatHeaderProps = {
    interestsCount: number;
    loading: boolean;
    onReset: () => void;
};

export default function ChatHeader({
    interestsCount,
    loading,
    onReset,
}: ChatHeaderProps) {
    return (
        <div className="hc-header">
            <div className="hc-brandRow">
                <div>
                    <div className="hc-title">
                        Hello<span className="hc-city">City</span>
                    </div>
                    <div className="hc-sub">Interests: {interestsCount}/3</div>
                </div>

                <div className="hc-headerActions">
                    <button
                        className="hc-reset-button"
                        onClick={onReset}
                        disabled={loading}
                        title="Reset this onboarding session"
                    >
                        Reset
                    </button>

                    <div className="hc-pill">Miami</div>
                </div>
            </div>
        </div>
    );
}
