import type { PlaceCard as PlaceCardT } from "../api/types";

export default function PlaceCard({ p }: { p: PlaceCardT }) {
    return (
        <a
            href={p.maps_url ?? "#"}
            target="_blank"
            rel="noreferrer"
            style={{ textDecoration: "none", color: "inherit" }}
        >
            <div
                style={{
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 14,
                    overflow: "hidden",
                    background: "#0b1220",
                }}
            >
                {p.photo_url ? (
                    <img
                        src={p.photo_url}
                        alt={p.name}
                        style={{
                            width: "100%",
                            height: 140,
                            objectFit: "cover",
                        }}
                    />
                ) : null}

                <div style={{ padding: 12 }}>
                    <div
                        style={{
                            fontWeight: 700,
                            color: "white",
                            marginBottom: 6,
                        }}
                    >
                        {p.name}
                    </div>

                    {p.address ? (
                        <div
                            style={{
                                color: "rgba(255,255,255,0.75)",
                                fontSize: 13,
                            }}
                        >
                            {p.address}
                        </div>
                    ) : null}

                    <div
                        style={{
                            marginTop: 8,
                            color: "rgba(255,255,255,0.75)",
                            fontSize: 13,
                        }}
                    >
                        {typeof p.rating === "number" ? `⭐ ${p.rating}` : ""}
                        {typeof p.user_ratings_total === "number"
                            ? ` (${p.user_ratings_total})`
                            : ""}
                    </div>
                </div>
            </div>
        </a>
    );
}
