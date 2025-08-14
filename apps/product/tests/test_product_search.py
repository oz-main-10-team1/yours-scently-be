import uuid
from decimal import Decimal

import pytest
from django.db import IntegrityError, models
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import Product

pytestmark = pytest.mark.django_db


# --------- small helpers ---------
def _has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


def _choices(model, name: str):
    try:
        f = model._meta.get_field(name)
        return list(f.choices) if getattr(f, "choices", None) else []
    except Exception:
        return []


def _build_minimal_instance(model):
    """모델의 NOT NULL 필드를 합리적 기본값으로 채워 1개 생성"""
    data = {}
    for f in model._meta.get_fields():
        if getattr(f, "auto_created", False) or getattr(f, "primary_key", False):
            continue
        if isinstance(f, (models.ManyToManyRel, models.ManyToOneRel, models.ManyToManyField)):
            continue
        if f.has_default():
            continue

        if isinstance(f, models.ForeignKey):
            rel = _build_minimal_instance(f.remote_field.model)
            data[f.name] = rel
            continue

        ch = getattr(f, "choices", None)
        if ch:
            data[f.name] = ch[0][0]
            continue

        if isinstance(f, models.CharField):
            data[f.name] = f"t-{uuid.uuid4().hex[:6]}" if getattr(f, "unique", False) else "test"
        elif isinstance(f, models.TextField):
            data[f.name] = "test"
        elif isinstance(f, models.DecimalField):
            data[f.name] = Decimal("0")
        elif isinstance(
            f,
            (
                models.IntegerField,
                models.BigIntegerField,
                models.SmallIntegerField,
                models.PositiveIntegerField,
                models.PositiveSmallIntegerField,
            ),
        ):
            data[f.name] = 0
        elif isinstance(f, models.FloatField):
            data[f.name] = 0.0
        elif isinstance(f, models.BooleanField):
            data[f.name] = False
        elif isinstance(f, models.DateField):
            from django.utils import timezone

            data[f.name] = timezone.now().date()
        elif isinstance(f, models.DateTimeField):
            from django.utils import timezone

            data[f.name] = timezone.now()
        else:
            # nullable 아니면 최소값
            if not getattr(f, "null", True):
                data[f.name] = "test"

    return model.objects.create(**data)


def _create_perfume_for_product():
    """Product.perfume/perfume_id 요구 충족용 Perfume 1개 생성"""
    if _has_field(Product, "perfume"):
        perfume_model = Product._meta.get_field("perfume").remote_field.model
    elif _has_field(Product, "perfume_id"):
        # 같은 app 안에 있다고 가정 (필요시 경로 수정)
        from apps.product.models import Perfume as perfume_model  # noqa
    else:
        return None
    return _build_minimal_instance(perfume_model)


def create_product(**over):
    """NOT NULL 기본값 채우고 perfume FK 자동 주입"""
    defaults = dict(
        name="기본상품",
        volume_ml=50,
        price=Decimal("1000"),
        stock=0,
        product_img_url="https://example.com/img.jpg",
    )
    if _has_field(Product, "category"):
        ch = _choices(Product, "category")
        defaults["category"] = ch[0][0] if ch else "인기상품"

    # perfume FK/ID 자동 채움
    if _has_field(Product, "perfume"):
        defaults.setdefault("perfume", _create_perfume_for_product())
    elif _has_field(Product, "perfume_id"):
        if "perfume_id" not in over:
            p = _create_perfume_for_product()
            defaults["perfume_id"] = getattr(p, "id")

    defaults.update(over)
    return Product.objects.create(**defaults)


# --------- APIClient ---------
@pytest.fixture
def client():
    return APIClient()


# --------- tests ---------
def test_search_basic_pagination(client):
    for i in range(1, 21):
        create_product(name=f"상품{i}", price=1000 * i)

    url = reverse("product-search")
    res = client.get(url, {"page": 1, "limit": 10})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 20
    assert body["page"] == 1
    assert body["limit"] == 10
    assert len(body["results"]) == 10
    assert {"product_id", "name", "price", "brand", "notes", "thumbnail_url"} <= set(body["results"][0].keys())


def test_search_keyword_filters_name_and_price_type(client):
    create_product(name="시트러스 프레쉬", price=65000, product_img_url="https://x/y.jpg")
    create_product(name="우디 머스크", price=70000)

    url = reverse("product-search")
    res = client.get(url, {"keyword": "시트러스", "limit": 10})
    assert res.status_code == 200

    results = res.json()["results"]
    names = [r["name"] for r in results]
    assert any("시트러스" in n for n in names)
    assert all(n != "우디 머스크" for n in names)
    assert isinstance(results[0]["price"], int)
    for r in results:
        if r["name"] == "시트러스 프레쉬":
            assert r["thumbnail_url"] == "https://x/y.jpg"


def test_search_sort_price_desc(client):
    create_product(name="A", price=1000)
    create_product(name="B", price=3000)
    create_product(name="C", price=2000)

    url = reverse("product-search")
    res = client.get(url, {"sort": "price_desc", "limit": 3})
    assert res.status_code == 200
    prices = [item["price"] for item in res.json()["results"]]
    assert prices == sorted(prices, reverse=True)


def test_search_invalid_price_range_returns_400(client):
    url = reverse("product-search")
    res = client.get(url, {"price_min": 10000, "price_max": 100})
    assert res.status_code == 400
    assert "detail" in res.json()


def test_search_category_filter_if_available(client):
    if not _has_field(Product, "category"):
        pytest.skip("Product.category 없음 — 스킵")

    ch = _choices(Product, "category")
    cat_a = ch[0][0] if ch else "인기상품"
    cat_b = ch[1][0] if len(ch) > 1 else (cat_a if ch else "신상품")

    create_product(name="A", price=1000, category=cat_a)
    create_product(name="B", price=2000, category=cat_b)

    url = reverse("product-search")
    res = client.get(url, {"category": cat_a})
    assert res.status_code == 200
    names = [item["name"] for item in res.json()["results"]]
    assert "A" in names
    if cat_a != cat_b:
        assert "B" not in names


def test_search_notes_and_filter_if_perfume_relation_exists(client):
    if not _has_field(Product, "perfume"):
        pytest.skip("Product.perfume 없음 — 스킵")

    perfume_model = Product._meta.get_field("perfume").remote_field.model
    rel_name = None
    for cand in ("notes", "main_accords"):
        if _has_field(perfume_model, cand):
            rel_name = cand
            break
    if rel_name is None:
        pytest.skip("Perfume에 notes/main_accords 없음 — 스킵")

    rel_field = perfume_model._meta.get_field(rel_name)
    note_model = rel_field.remote_field.model
    if not _has_field(note_model, "name"):
        pytest.skip("Note 모델에 name 없음 — 스킵")

    woody = note_model.objects.create(name="우디")
    fresh = note_model.objects.create(name="프레쉬")

    p1 = _build_minimal_instance(perfume_model)
    getattr(p1, rel_name).add(woody)
    p2 = _build_minimal_instance(perfume_model)
    getattr(p2, rel_name).add(fresh)
    p3 = _build_minimal_instance(perfume_model)
    getattr(p3, rel_name).add(woody, fresh)

    create_product(name="우디향1", price=1000, perfume=p1)
    create_product(name="프레쉬향1", price=2000, perfume=p2)
    create_product(name="복합향", price=3000, perfume=p3)

    url = reverse("product-search")
    res = client.get(url, {"note": ["우디", "프레쉬"], "limit": 10})
    assert res.status_code == 200
    names = [item["name"] for item in res.json()["results"]]
    assert names == ["복합향"]
