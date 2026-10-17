"""Build the local-only live listing feed from property alert emails.

The portals send the alerts; this script only reads saved mail and never visits
or crawls a property portal. It uses the Python standard library (no API/token).
"""
from __future__ import annotations

import argparse
import ctypes
import email
import email.policy
import hashlib
import html
import imaplib
import json
import os
import re
import email.utils
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "local-data" / "property-alerts"
OUTPUT = ROOT / "dist" / "bangkok-local-listings.js"
CATALOGUE = ROOT / "dist" / "bangkok-catalogue.js"
MAIL_SETTINGS = ROOT / "local-data" / "mail-settings.json"
ALLOWED = {"propertyhub.in.th", "www.propertyhub.in.th", "ddproperty.com", "www.ddproperty.com"}
DDPROPERTY_RSS = {
    "sale": "https://www.ddproperty.com/rss/sale/N:",
    "rent": "https://www.ddproperty.com/rss/rent/N:",
}


class AlertHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.body: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if tag == "a" and attrs_map.get("href"):
            self.current = {"url": html.unescape(attrs_map["href"] or ""), "text": ""}

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.body.append(value)
            if self.current is not None:
                self.current["text"] += " " + value

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current is not None:
            self.links.append({key: value.strip() for key, value in self.current.items()})
            self.current = None


def load_array(path: Path, symbol: str) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(symbol)}\s*=\s*(\[.*\]);", source, re.S)
    if not match:
        raise ValueError(f"Missing {symbol} in {path}")
    return json.loads(match.group(1))


def decode_message(msg: email.message.Message, fallback_date: str) -> tuple[str, str, str]:
    subject = str(msg.get("subject", ""))
    chunks: list[str] = []
    for part in msg.walk():
        if part.get_content_maintype() != "text":
            continue
        try:
            content = part.get_content()
        except (LookupError, UnicodeDecodeError):
            continue
        if part.get_content_subtype() == "html":
            chunks.append(content)
        elif not chunks:
            chunks.append(content)
    date_value = msg.get("date")
    try:
        observed = email.utils.parsedate_to_datetime(str(date_value)).astimezone(timezone.utc).date().isoformat()
    except (TypeError, ValueError, AttributeError):
        observed = fallback_date
    return subject, "\n".join(chunks), observed


def clean_listing_url(raw_url: str) -> str | None:
    url = html.unescape(raw_url).strip()
    parsed = urlparse(url)
    # Accept direct portal URLs only. Do not follow third-party tracking links.
    if parsed.hostname not in ALLOWED:
        return None
    path = unquote(parsed.path).lower()
    is_listing = ("propertyhub.in.th" in (parsed.hostname or "") and "/listings/" in path) or (
        "ddproperty.com" in (parsed.hostname or "") and bool(re.search(r"/(?:property|listing|condo)/", path))
    )
    if not is_listing:
        return None
    return url.split("#", 1)[0]


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9ก-๙]+", " ", value.lower()).strip()


def match_project(text: str, projects: list[dict]) -> dict | None:
    haystack = f" {normalized(text)} "
    matches = [project for project in projects if f" {normalized(str(project.get('name', '')))} " in haystack]
    return matches[0] if len(matches) == 1 else None


def extract_number(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, re.I)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


def parse_content(subject: str, body: str, observed: str, projects: list[dict]) -> tuple[list[dict], list[dict]]:
    parser = AlertHTML()
    parser.feed(body)
    searchable = html.unescape(re.sub(r"<[^>]+>", " ", body))
    searchable = re.sub(r"\s+", " ", searchable)
    listings, review = [], []
    for anchor in parser.links:
        url = clean_listing_url(anchor["url"])
        if not url:
            continue
        title = re.sub(r"\s+", " ", anchor["text"]).strip() or subject.strip()
        # Email alerts often put price and size in adjacent plain text. Match a
        # bounded window around the linked title to avoid using another card.
        offset = searchable.lower().find(title.lower()) if title else -1
        context = searchable[max(0, offset - 120): offset + len(title) + 180] if offset >= 0 else title
        text = f"{subject} {title} {context}"
        project = match_project(text, projects)
        price = extract_number(r"(?:฿|THB\s*)\s*([\d,]+(?:\.\d+)?)", text)
        area = extract_number(r"([\d.]+)\s*(?:sq\.?\s*m|sqm|m²|㎡)", text)
        bedrooms = extract_number(r"(\d+)\s*(?:bed(?:room)?s?|ห้องนอน|房)", text)
        low = (url + " " + text).lower()
        kind = "rent" if any(word in low for word in ("for-rent", "for rent", "rent", "ให้เช่า", "เช่า")) else "sale" if any(word in low for word in ("for-sale", "for sale", "sale", "ขาย")) else None
        if not kind:
            continue
        price_sqm = round(price / area) if price and area else None
        row = {"id": hashlib.sha256(url.encode()).hexdigest()[:16], "projectId": int(project["id"]) if project else None,
               "kind": kind, "title": title[:240], "url": url, "price": round(price) if price else None,
               "area": area, "priceSqm": price_sqm, "bedrooms": int(bedrooms) if bedrooms else None,
               "observedAt": observed, "sourceName": "DDproperty" if "ddproperty.com" in url else "PropertyHub"}
        # Avoid accidentally storing contact details from the email body.
        if project and price and area:
            listings.append(row)
        else:
            review.append({"title": row["title"], "url": url, "kind": kind,
                           "reason": "無法唯一配對 Condo" if not project else "郵件未提供可核對的總價與面積"})
    return listings, review


def parse_file(path: Path, projects: list[dict]) -> tuple[list[dict], list[dict]]:
    fallback_date = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat()
    if path.suffix.lower() == ".eml":
        message = BytesParser(policy=email.policy.default).parsebytes(path.read_bytes())
        subject, body, observed = decode_message(message, fallback_date)
    else:
        body = path.read_text(encoding="utf-8", errors="replace")
        subject, observed = "", fallback_date
    return parse_content(subject, body, observed, projects)


def rss_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return re.sub(r"\s+", " ", html.unescape(" ".join(element.itertext()))).strip()


def parse_ddproperty_rss(xml_bytes: bytes, kind: str, projects: list[dict]) -> tuple[list[dict], list[dict]]:
    """Parse only DDproperty's published RSS feeds (no listing-page crawling)."""
    root = ET.fromstring(xml_bytes)
    listings: list[dict] = []
    review: list[dict] = []
    for item in root.iter():
        if item.tag.rsplit("}", 1)[-1].lower() not in {"item", "entry"}:
            continue
        values = {child.tag.rsplit("}", 1)[-1].lower(): child for child in list(item)}
        title = rss_text(values.get("title"))
        description = rss_text(values.get("description") or values.get("summary") or values.get("content"))
        raw_link = rss_text(values.get("link"))
        if not raw_link:
            link_element = values.get("link")
            raw_link = str(link_element.attrib.get("href", "")) if link_element is not None else ""
        url = clean_listing_url(raw_link)
        if not url:
            continue
        published = rss_text(values.get("pubdate") or values.get("published") or values.get("updated"))
        try:
            observed = email.utils.parsedate_to_datetime(published).date().isoformat()
        except (TypeError, ValueError, AttributeError):
            observed = datetime.now(timezone.utc).date().isoformat()
        text = f"{title} {description}"
        project = match_project(text, projects)
        price = extract_number(r"(?:฿|THB\s*)\s*([\d,]+(?:\.\d+)?)", text)
        area = extract_number(r"([\d.]+)\s*(?:sq\.?\s*m|sqm|m²|㎡)", text)
        bedrooms = extract_number(r"(\d+)\s*(?:bed(?:room)?s?|ห้องนอน|房)", text)
        row = {"id": hashlib.sha256(url.encode()).hexdigest()[:16], "projectId": int(project["id"]) if project else None,
               "kind": kind, "title": title[:240], "url": url, "price": round(price) if price else None,
               "area": area, "priceSqm": round(price / area) if price and area else None,
               "bedrooms": int(bedrooms) if bedrooms else None, "observedAt": observed,
               "sourceName": "DDproperty RSS"}
        if project and price and area:
            listings.append(row)
        else:
            reason = "無法唯一配對 Condo" if not project else "RSS 未提供可核對的總價與面積"
            review.append({"title": row["title"], "url": url, "kind": kind, "reason": reason})
    return listings, review


def fetch_ddproperty_rss(projects: list[dict]) -> tuple[list[dict], list[dict], list[str]]:
    listings: list[dict] = []
    review: list[dict] = []
    errors: list[str] = []
    request_headers = {"User-Agent": "BangkokCondoMapRSS/1.0 (local RSS reader)", "Accept": "application/rss+xml, application/xml, text/xml"}
    for kind, url in DDPROPERTY_RSS.items():
        request = urllib.request.Request(url, headers=request_headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                parsed, needs_review = parse_ddproperty_rss(response.read(), kind, projects)
            listings.extend(parsed)
            review.extend(needs_review)
        except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError) as error:
            errors.append(f"DDproperty {kind} RSS unavailable: {error}")
    return listings, review, errors


def read_windows_credential(target: str) -> str:
    if sys.platform != "win32":
        raise RuntimeError("Windows Credential Manager is available only on Windows")
    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]
    class CREDENTIALW(ctypes.Structure):
        _fields_ = [("Flags", ctypes.c_uint32), ("Type", ctypes.c_uint32), ("TargetName", ctypes.c_wchar_p),
                    ("Comment", ctypes.c_wchar_p), ("LastWritten", FILETIME),
                    ("CredentialBlobSize", ctypes.c_uint32), ("CredentialBlob", ctypes.c_void_p),
                    ("Persist", ctypes.c_uint32), ("AttributeCount", ctypes.c_uint32),
                    ("Attributes", ctypes.c_void_p), ("TargetAlias", ctypes.c_wchar_p), ("UserName", ctypes.c_wchar_p)]
    pointer = ctypes.POINTER(CREDENTIALW)()
    advapi = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
    advapi.CredReadW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(CREDENTIALW))]
    advapi.CredReadW.restype = ctypes.c_int
    advapi.CredFree.argtypes = [ctypes.c_void_p]
    advapi.CredFree.restype = None
    if not advapi.CredReadW(target, 1, 0, ctypes.byref(pointer)):
        raise RuntimeError(f"No Windows generic credential found for {target}")
    try:
        credential = pointer.contents
        blob = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        return blob.decode("utf-16-le").rstrip("\x00")
    finally:
        advapi.CredFree(pointer)


def fetch_imap_alerts() -> list[bytes]:
    if not MAIL_SETTINGS.exists():
        return []
    settings = json.loads(MAIL_SETTINGS.read_text(encoding="utf-8"))
    host, username = str(settings.get("host", "")).strip(), str(settings.get("username", "")).strip()
    if not host or not username:
        return []
    credential_name = str(settings.get("credentialName") or "BangkokCondoDailyIMAP")
    password = read_windows_credential(credential_name)
    since = (datetime.now(timezone.utc).date()).fromordinal(datetime.now(timezone.utc).date().toordinal() - int(settings.get("days", 45)))
    since_text = since.strftime("%d-%b-%Y")
    messages: list[bytes] = []
    client = imaplib.IMAP4_SSL(host, int(settings.get("port", 993)), timeout=40)
    try:
        client.login(username, password)
        status, _ = client.select(str(settings.get("folder") or "INBOX"), readonly=True)
        if status != "OK":
            raise RuntimeError("Could not open the configured IMAP folder")
        status, data = client.search(None, "SINCE", since_text)
        if status != "OK":
            raise RuntimeError("IMAP search failed")
        ids = (data[0] or b"").split()[-1000:]
        allowed = tuple(str(domain).lower().lstrip("@") for domain in settings.get("fromDomains", ["ddproperty.com", "propertyhub.in.th"]))
        for message_id in ids:
            status, fetched = client.fetch(message_id, "(RFC822)")
            if status != "OK":
                continue
            raw = next((part[1] for part in fetched if isinstance(part, tuple) and isinstance(part[1], bytes)), None)
            if not raw:
                continue
            parsed = BytesParser(policy=email.policy.default).parsebytes(raw)
            sender = email.utils.parseaddr(str(parsed.get("from", "")))[1].lower()
            sender_domain = sender.rsplit("@", 1)[-1] if "@" in sender else ""
            if any(sender_domain == domain or sender_domain.endswith("." + domain) for domain in allowed):
                messages.append(raw)
    finally:
        try:
            client.logout()
        except imaplib.IMAP4.error:
            pass
    return messages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inbox", type=Path, default=INBOX)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    projects = load_array(CATALOGUE, "BANGKOK_HIPFLAT_PROJECTS")
    existing: dict[str, dict] = {}
    if args.output.exists():
        source = args.output.read_text(encoding="utf-8")
        match = re.search(r"window\.BANGKOK_LOCAL_LISTINGS\s*=\s*(\[.*\]);", source, re.S)
        if match:
            for group in json.loads(match.group(1)):
                for row in group.get("listings", []):
                    existing[row["id"]] = row
    review: dict[str, dict] = {}
    scanned = 0
    args.inbox.mkdir(parents=True, exist_ok=True)
    for path in sorted(args.inbox.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".eml", ".html", ".htm", ".txt"}:
            continue
        scanned += 1
        rows, needs_review = parse_file(path, projects)
        existing.update({row["id"]: row for row in rows})
        review.update({row["url"]: row for row in needs_review})
    imap_count = 0
    for raw_message in fetch_imap_alerts():
        message = BytesParser(policy=email.policy.default).parsebytes(raw_message)
        subject, body, observed = decode_message(message, datetime.now(timezone.utc).date().isoformat())
        rows, needs_review = parse_content(subject, body, observed, projects)
        existing.update({row["id"]: row for row in rows})
        review.update({row["url"]: row for row in needs_review})
        imap_count += 1
    rss_rows, rss_review, rss_errors = fetch_ddproperty_rss(projects)
    existing.update({row["id"]: row for row in rss_rows})
    review.update({row["url"]: row for row in rss_review})
    grouped: dict[int, list[dict]] = {}
    for row in existing.values():
        grouped.setdefault(int(row["projectId"]), []).append(row)
    feed = [{"projectId": project_id, "listings": sorted(rows, key=lambda row: (row["observedAt"], row["id"]), reverse=True)}
            for project_id, rows in sorted(grouped.items())]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("window.BANGKOK_LOCAL_LISTINGS = " + json.dumps(feed, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    review_path = args.inbox.parent / "needs-review.json"
    review_path.write_text(json.dumps({"updatedAt": datetime.now().astimezone().isoformat(), "listings": list(review.values())}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"mailFilesScanned": scanned, "imapAlertsScanned": imap_count, "ddpropertyRssListings": len(rss_rows),
                      "matchedListings": len(existing), "matchedCondos": len(grouped), "needsReview": len(review),
                      "feed": str(args.output), "review": str(review_path), "sourceErrors": rss_errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()
