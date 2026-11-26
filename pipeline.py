"""Build a validated local database; optionally retrieve source via KaggleHub."""
import argparse
from python_eda.validated_etl import build

def ingest(source, destination):
    return build(source, destination)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--source", default="data")
    parser.add_argument("--database", default="data/olist.db")
    args = parser.parse_args()
    if args.download:
        import kagglehub
        args.source = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    print(ingest(args.source, args.database))
