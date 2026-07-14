import json
from crawler import fetch_latest_post


def main():
    with open("sites.json", "r", encoding="utf-8") as f:
        sites = json.load(f)

    latest = fetch_latest_post(sites[0])
    print(latest)


if __name__ == "__main__":
    main()
