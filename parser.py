import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

KEYWORDS = [
    "автопром", "утилизационный сбор", "акцизы", "субсидии", "экотранспорт",
    "электромобили", "импортозамещение", "технический осмотр", "логистика",
    "автомобили", "автотранспорт", "автопроизводители", "господдержка"
]

FAILED_SOURCES = []  # Список источников, которые не ответили

def get_documents_for_days(days):
    global FAILED_SOURCES
    FAILED_SOURCES = []  # сбрасываем список при каждом новом запросе

    all_docs = []
    all_docs += get_pravo_docs(days)
    all_docs += get_regulation_docs(days)
    all_docs += get_duma_docs(days)
    all_docs += get_kremlin_docs(days)
    all_docs += get_consultant_docs(days)
    return all_docs

def get_failed_sources():
    return FAILED_SOURCES

# Пример функции (1 из 5): publication.pravo.gov.ru
def get_pravo_docs(days):
    urls = [
        "http://publication.pravo.gov.ru/documents/government/daily",
        "http://publication.pravo.gov.ru/documents/government/weekly",
        "http://publication.pravo.gov.ru/documents/government/monthly"
    ]

    today = datetime.now()
    start_date = today - timedelta(days=days)
    results = []

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select(".entry"):
                title_tag = item.select_one(".title")
                date_tag = item.select_one(".date")

                if not title_tag or not date_tag:
                    continue

                title = title_tag.text.strip()
                date_str = date_tag.text.strip()
                try:
                    pub_date = datetime.strptime(date_str, "%d.%m.%Y")
                except:
                    continue

                if pub_date < start_date:
                    continue

                matched = [k for k in KEYWORDS if k.lower() in title.lower()]
                if matched:
                    results.append({
                        "title": title,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "url": "http://publication.pravo.gov.ru" + title_tag["href"],
                        "source": "publication.pravo.gov.ru",
                        "topics": matched
                    })
        except Exception as e:
            FAILED_SOURCES.append("publication.pravo.gov.ru")
    return results

# regulation.gov.ru
def get_regulation_docs(days):
    url = "https://regulation.gov.ru/projects"
    results = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        today = datetime.now()
        start_date = today - timedelta(days=days)

        for row in soup.select("div.project-list__item"):
            title_elem = row.select_one("a.project-list__title")
            date_elem = row.select_one("div.project-list__date")
            if not title_elem or not date_elem:
                continue

            title = title_elem.text.strip()
            doc_url = "https://regulation.gov.ru" + title_elem["href"]
            date_text = date_elem.text.strip().replace("Дата публикации:", "").strip()

            try:
                pub_date = datetime.strptime(date_text, "%d.%m.%Y")
            except:
                continue

            if pub_date < start_date:
                continue

            matched = [k for k in KEYWORDS if k.lower() in title.lower()]
            if matched:
                results.append({
                    "title": title,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": doc_url,
                    "source": "regulation.gov.ru",
                    "topics": matched
                })
    except Exception:
        FAILED_SOURCES.append("regulation.gov.ru")
    return results

# sozd.duma.gov.ru
def get_duma_docs(days):
    url = "https://sozd.duma.gov.ru/oz?b[ClassOfTheObjectLawmakingId]=1"
    results = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        today = datetime.now()
        start_date = today - timedelta(days=days)

        for row in soup.select("div.media-body"):
            title_tag = row.select_one("a")
            date_tag = row.select_one("small")

            if not title_tag or not date_tag:
                continue

            title = title_tag.text.strip()
            date_str = date_tag.text.strip().split(" ")[-1]

            try:
                pub_date = datetime.strptime(date_str, "%d.%m.%Y")
            except:
                continue

            if pub_date < start_date:
                continue

            matched = [k for k in KEYWORDS if k.lower() in title.lower()]
            if matched:
                results.append({
                    "title": title,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": "https://sozd.duma.gov.ru" + title_tag["href"],
                    "source": "sozd.duma.gov.ru",
                    "topics": matched
                })
    except Exception:
        FAILED_SOURCES.append("sozd.duma.gov.ru")
    return results

# kremlin.ru
def get_kremlin_docs(days):
    url = "https://kremlin.ru/acts/assignments/orders"
    results = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        today = datetime.now()
        start_date = today - timedelta(days=days)

        for item in soup.select(".b_announcement"):
            title_tag = item.select_one("a")
            date_tag = item.select_one("span.date")

            if not title_tag or not date_tag:
                continue

            title = title_tag.text.strip()
            date_str = date_tag.text.strip()

            try:
                pub_date = datetime.strptime(date_str, "%d %B %Y")
            except:
                try:
                    pub_date = datetime.strptime(date_str, "%d.%m.%Y")
                except:
                    continue

            if pub_date < start_date:
                continue

            matched = [k for k in KEYWORDS if k.lower() in title.lower()]
            if matched:
                results.append({
                    "title": title,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": "https://kremlin.ru" + title_tag["href"],
                    "source": "kremlin.ru",
                    "topics": matched
                })
    except Exception:
        FAILED_SOURCES.append("kremlin.ru")
    return results

# consultant.ru
def get_consultant_docs(days):
    url = "https://www.consultant.ru/law/review/fed/"
    results = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        today = datetime.now()
        start_date = today - timedelta(days=days)

        for item in soup.select(".doc_card"):
            title_tag = item.select_one(".card__title")
            date_tag = item.select_one(".card__date")
            link_tag = item.select_one("a")

            if not title_tag or not date_tag or not link_tag:
                continue

            title = title_tag.text.strip()
            date_str = date_tag.text.strip()

            try:
                pub_date = datetime.strptime(date_str, "%d.%m.%Y")
            except:
                continue

            if pub_date < start_date:
                continue

            matched = [k for k in KEYWORDS if k.lower() in title.lower()]
            if matched:
                results.append({
                    "title": title,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": "https://www.consultant.ru" + link_tag["href"],
                    "source": "consultant.ru",
                    "topics": matched
                })
    except Exception:
        FAILED_SOURCES.append("consultant.ru")
    return results
