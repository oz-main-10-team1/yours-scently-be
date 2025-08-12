"""
1. 어떤 분위기의 향을 선호하시나요?
- 상쾌한 느낌
- 따뜻하고 포근한 느낌
- 로맨틱하고 부드러운 느낌
- 에너지 넘치고 활기찬 느낌
- 신비롭고 매혹적인 느낌

2. 평소에 어떤 향의 강도를 선호하시나요?
- 은은한 향을 좋아해요
- 적당한 향이 좋아요
- 존재감 있는 강한 향이 좋아요

3. 어떤 상황에서 향을 사용하고 싶으신가요?
- 데일리용
- 잠들기 전
- 운동 후
- 특별한 날

4. 당신을 가장 잘 표현하는 감성 키워드를 골라주세요
- 따뜻한
- 부드러운
- 시크한
- 사랑스러운
- 강렬한
- 몽환적인
"""

# 어떤 분위기의 향을 선호하시나요? -> Perfume.main_accords
MOOD_MAP = {
    "상쾌한 느낌": ["fresh", "green", "herbal", "aromatic", "spicy", "ozonic", "aquatic", "marine"],
    "따뜻하고 포근한 느낌": ["woody", "leather", "oud", "smoky", "earthy", "mossy"],
    "로맨틱하고 부드러운 느낌": [
        "floral",
        "rose",
        "white floral",
        "yellow floral",
        "violet",
        "tuberose",
        "iris",
        "lavender",
    ],
    "에너지 넘치고 활기찬 느낌": ["citrus", "fruity", "tropical", "caramel", "almond", "caramel", "sweet"],
    "신비롭고 매혹적인 느낌": ["warm spicy", "cinnamon", "nutty", "amber", "sweet", "patchouli", "animalic"],
}
# 평소에 어떤 향의 강도를 선호하시나요? -> Perfume.intensity (CharField: IntensityChoices)
INTENSITY_MAP = {
    "은은한 향을 좋아해요": ["eau_fraiche"],
    "적당한 향이 좋아요": ["eau_de_toilette", "eau_de_cologne"],
    "존재감 있는 강한 향이 좋아요": ["parfum", "eau_de_parfum"],
}
# 어떤 상황에서 향을 사용하고 싶으신가요? -> Product.category (CharField: Category)
USAGE_MAP = {
    "데일리용": "Daily",
    "잠들기 전": "Relax",
    "운동 후": "Outdoor",
    "특별한 날": "Special",
}
# 당신을 가장 잘 표현하는 감성 키워드를 골라주세요 -> Perfume.top_notes / middle_notes / base_notes (ManyToManyField to Note.name)
KEYWORD_MAP = {
    "따뜻한": [
        "warm",
        "Spicy Warm",
        "vanilla",
        "cinnamon",
        "nutmeg",
        "ginger",
        "sandalwood",
        "cedarwood",
        "woody",
        "amber",
    ],
    "부드러운": [
        "soft",
        "musk",
        "powdery",
        "iris",
        "violet",
        "light florals",
        "freesia",
        "peony",
        "cream",
        "white musk",
    ],
    "시크한": [
        "chic",
        "leather",
        "patchouli",
        "tea",
        "rosemary",
        "aromatic herbs",
        "sage",
        "basil",
        "galbanum",
        "green tea",
        "vetiver",
    ],
    "사랑스러운": [
        "lavender",
        "rose",
        "peony",
        "strawberry",
        "raspberry",
        "apple",
        "lychee",
        "jasmine",
        "gardenia",
        "honey",
        "praline",
    ],
    "강렬한": [
        "intense",
        "oud",
        "tobacco",
        "incense",
        "black pepper",
        "cardamom",
        "chili",
        "leather",
        "suede",
        "gaiacwood",
        "civet",
        "castoreum",
    ],
    "몽환적인": [
        "dreamy",
        "violet",
        "frankincense",
        "myrrh",
        "metallic",
        "mineral",
        "violet leaf",
        "marine",
        "sea breeze",
        "chamomile",
        "myrrh",
    ],
}
