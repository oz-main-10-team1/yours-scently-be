import pandas as pd
from django.core.management.base import BaseCommand

from apps.product.models import Perfume


class Command(BaseCommand):
    help = "Create missing Perfume rows from embeddings CSV (columns: name, brand, embedding)."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True)
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--sep", default=",")

    def handle(self, *args, **o):
        df = pd.read_csv(o["path"], encoding=o["encoding"], sep=o["sep"])
        needed = {"name", "brand", "embedding"}
        if not needed.issubset(df.columns):
            raise SystemExit(f"CSV must include {needed}, got: {list(df.columns)}")

        created = existed = 0
        for _, r in df.iterrows():
            name = str(r["name"]).strip()
            brand = str(r["brand"]).strip()
            obj, is_created = Perfume.objects.get_or_create(name=name, brand=brand, defaults={"release_year": 0})
            created += int(is_created)
            existed += int(not is_created)

        self.stdout.write(self.style.SUCCESS(f"created={created}, existed={existed}"))
