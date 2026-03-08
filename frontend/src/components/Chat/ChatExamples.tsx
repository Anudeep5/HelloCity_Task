import PlaceCard from "../PlaceCard";
import type { PlaceCard as PlaceCardT } from "../../api/types";

type ChatExamplesProps = {
    pendingInterest: string;
    examples: PlaceCardT[];
    loading: boolean;
    onYes: () => void;
    onNo: () => void;
};

export default function ChatExamples({
    pendingInterest,
    examples,
    loading,
    onYes,
    onNo,
}: ChatExamplesProps) {
    return (
        <div>
            <div className="hc-sectionTitle">
                Emily’s Picks: {pendingInterest}
            </div>

            <div className="hc-cardGrid">
                {examples.map((place, index) => (
                    <PlaceCard key={index} p={place} />
                ))}
            </div>

            <div className="hc-actions">
                <button
                    className="hc-btn hc-btnPrimary"
                    onClick={onYes}
                    disabled={loading}
                    type="button"
                >
                    Yes, that’s what I meant
                </button>

                <button
                    className="hc-btn hc-btnGhost"
                    onClick={onNo}
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
    );
}
