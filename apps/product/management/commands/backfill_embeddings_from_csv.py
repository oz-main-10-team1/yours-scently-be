import json
import re
import unicodedata

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.product.models import Perfume


def normalize(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).lower()
    # 영숫자만 남기고 나머지 제거
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


class Command(BaseCommand):
    help = "Backfill Perfume.embedding from CSV (columns: name, brand, embedding(JSON list len=512))."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="CSV file path")
        parser.add_argument("--encoding", default="utf-8", help="CSV encoding (e.g., utf-8, cp949)")
        parser.add_argument("--sep", default=",", help="CSV separator (e.g., ',', ';')")

    @transaction.atomic
    def handle(self, *args, **opts):
        path = opts["path"]
        encoding = opts["encoding"]
        sep = opts["sep"]

        df = pd.read_csv(path, encoding=encoding, sep=sep)
        needed = {"name", "brand", "embedding"}
        if not needed.issubset(df.columns):
            raise SystemExit(f"CSV must include {needed}, got: {list(df.columns)}")

        updated = missing = bad = 0
        for _, r in df.iterrows():
            name = str(r["name"]).strip()
            brand = str(r["brand"]).strip()
            raw = r["embedding"]

            try:
                emb = json.loads(raw) if isinstance(raw, str) else list(raw)
                if not isinstance(emb, list) or len(emb) != 512:
                    bad += 1
                    continue
            except Exception:
                bad += 1
                continue

            # 우선 정확 매칭, 없으면 대소문자 무시 매칭
            obj = (
                Perfume.objects.filter(name=name, brand=brand).first()
                or Perfume.objects.filter(name__iexact=name, brand__iexact=brand).first()
            )
            if not obj:
                missing += 1
                continue

            obj.embedding = emb
            obj.save(update_fields=["embedding"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"updated={updated}, missing={missing}, bad_rows={bad}"))
