type ChatProfileProps = {
    profile: { interests: string[] };
};

export default function ChatProfile({ profile }: ChatProfileProps) {
    return (
        <div className="hc-profile">
            <div className="hc-profileBody">
                <div className="hc-profileTitle">Your profile</div>
                <pre className="hc-profilePre">
                    {JSON.stringify(profile, null, 2)}
                </pre>
            </div>
        </div>
    );
}