import type { PlaceCard as PlaceCardT } from "../api/types";

export default function PlaceCard({ p }: { p: PlaceCardT }) {
    return (
        <a
            href={p.maps_url ?? "#"}
            target="_blank"
            rel="noreferrer"
            style={{ textDecoration: "none" }}
        >
            <div className="hc-card">
                {p.photo_url ? (
                    <img
                        className="hc-cardImg"
                        src={p.photo_url}
                        alt={p.name}
                    />
                ) : null}
                <div className="hc-cardBody">
                    <div className="hc-cardTitle">{p.name}</div>
                    {p.address ? (
                        <div className="hc-cardMeta">{p.address}</div>
                    ) : null}
                    <div className="hc-cardRating">
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
