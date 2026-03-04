import re


TAG_MAP: list[tuple[re.Pattern[str], str]] = [
    # Coffee / cafes
    (re.compile(r"\b(coffee|cafe|espresso|latte)\b", re.I), '["amenity"="cafe"]'),
    # Restaurants / food
    (
        re.compile(r"\b(restaurant|food|dinner|lunch|eat|dining)\b", re.I),
        '["amenity"="restaurant"]',
    ),
    # Bars / nightlife
    (re.compile(r"\b(bar|pub|drinks|cocktail)\b", re.I), '["amenity"~"^(bar|pub)$"]'),
    (re.compile(r"\b(club|nightclub|nightlife)\b", re.I), '["amenity"="nightclub"]'),
    # Breweries
    (re.compile(r"\b(brewery|beer|taproom)\b", re.I), '["craft"="brewery"]'),
    # Parks
    (re.compile(r"\b(park|garden|green)\b", re.I), '["leisure"="park"]'),
    # Museums / art
    (re.compile(r"\b(museum)\b", re.I), '["tourism"="museum"]'),
    (re.compile(r"\b(gallery|art|exhibit)\b", re.I), '["tourism"="gallery"]'),
    # Beaches
    (re.compile(r"\b(beach|ocean|shore)\b", re.I), '["natural"="beach"]'),
    # Zoo / aquarium
    (
        re.compile(r"\b(zoo|aquarium|wildlife)\b", re.I),
        '["tourism"~"^(zoo|aquarium)$"]',
    ),
    # Shopping
    (re.compile(r"\b(mall|shopping|shops|boutique)\b", re.I), '["shop"]'),
    # Gyms / fitness
    (re.compile(r"\b(gym|fitness|workout)\b", re.I), '["leisure"="fitness_centre"]'),
    # Yoga
    (re.compile(r"\b(yoga|pilates)\b", re.I), '["sport"="yoga"]'),
    # Spa / wellness
    (re.compile(r"\b(spa|massage|wellness)\b", re.I), '["leisure"="spa"]'),
    # Bakery
    (re.compile(r"\b(bakery|pastry|bread)\b", re.I), '["shop"="bakery"]'),
    # Ice cream / dessert
    (re.compile(r"\b(ice\s*cream|gelato|dessert)\b", re.I), '["amenity"="ice_cream"]'),
    # Pizza
    (re.compile(r"\b(pizza)\b", re.I), '["cuisine"="pizza"]'),
    # Seafood (very Miami relevant)
    (re.compile(r"\b(seafood|fish)\b", re.I), '["cuisine"="seafood"]'),
    # Latin food
    (re.compile(r"\b(cuban|latin|mexican)\b", re.I), '["cuisine"]'),
    # Rooftop bars
    (re.compile(r"\b(rooftop)\b", re.I), '["amenity"="bar"]'),
    # Live music
    (
        re.compile(r"\b(live\s*music|concert|music)\b", re.I),
        '["amenity"="music_venue"]',
    ),
    # Theaters
    (re.compile(r"\b(theater|theatre|play|drama)\b", re.I), '["amenity"="theatre"]'),
    # Cinema
    (re.compile(r"\b(cinema|movie|film)\b", re.I), '["amenity"="cinema"]'),
    # Bowling
    (re.compile(r"\b(bowling)\b", re.I), '["leisure"="bowling_alley"]'),
    # Arcade
    (re.compile(r"\b(arcade|gaming)\b", re.I), '["leisure"="amusement_arcade"]'),
    # Marina / boats
    (re.compile(r"\b(marina|boating|yacht)\b", re.I), '["leisure"="marina"]'),
    # Kayaking / water sports
    (
        re.compile(r"\b(kayak|kayaking|paddle|canoe)\b", re.I),
        '["sport"~"^(canoe|kayak)$"]',
    ),
    # Swimming pools
    (re.compile(r"\b(swim|pool)\b", re.I), '["leisure"="swimming_pool"]'),
    # Stadiums / sports
    (re.compile(r"\b(stadium|sports|arena)\b", re.I), '["leisure"="stadium"]'),
    # Libraries
    (re.compile(r"\b(library|reading)\b", re.I), '["amenity"="library"]'),
    # Hotels (staycation vibes)
    (re.compile(r"\b(hotel|resort)\b", re.I), '["tourism"="hotel"]'),
    (re.compile(r"\b(waterfront|bay|harbor)\b", re.I), '["leisure"="marina"]'),
    # Stand-up comedy / comedy clubs
    (
        re.compile(r"\b(stand\s*up|standup|comedy|comedian)\b", re.I),
        '["amenity"="theatre"]',
    ),
    # Performing arts / improv / stage shows
    (
        re.compile(r"\b(improv|performance|performing\s*arts|stage\s*show)\b", re.I),
        '["amenity"="arts_centre"]',
    ),
    # Live shows / concerts
    (
        re.compile(r"\b(show|live\s*show|concert|gig)\b", re.I),
        '["amenity"="music_venue"]',
    ),
    # General entertainment venues
    (
        re.compile(r"\b(entertainment|event|venue)\b", re.I),
        '["amenity"="events_venue"]',
    ),
]
