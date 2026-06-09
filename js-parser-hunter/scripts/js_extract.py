#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


TEXT_EXTENSIONS = {
    ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".map", ".json", ".html", ".vue"
}

SOURCE_MAP_RE = re.compile(r"(?://[#@]\s*sourceMappingURL=|/\*[#@]\s*sourceMappingURL=)([^\s*]+)", re.I)

PATTERNS = {
    "urls": re.compile(r"https?://[^\s\"'`<>\\)]+", re.I),
    "api_paths": re.compile(
        r"(?P<q>[\"'`])((?:/|\\u002f)(?:api|v\d+|graphql|rest|admin|internal|auth|oauth|sso|billing|webhook|upload|export|import)[^\"'`<>\s\\)]{0,220})(?P=q)",
        re.I,
    ),
    "route_templates": re.compile(r"(?P<q>[\"'`])(/[^\"'`]*?(?::[A-Za-z_][\w-]*|\{[A-Za-z_][\w-]*\})[^\"'`]*)(?P=q)"),
    "params": re.compile(
        r"\b([A-Za-z_][\w-]*(?:Id|ID|Token|Key|Secret|Url|URL|Uri|URI|Role|Permission|Plan|Tier|Status|State|Redirect|Callback|Webhook|File|Path|Bucket|Query|Filter))\b"
    ),
    "functions": re.compile(r"\b(?:function\s+([A-Za-z_$][\w$]*)|(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(?[^=;]{0,80}=>|([A-Za-z_$][\w$]*)\s*:\s*(?:async\s*)?\(?[^=;]{0,80}=>)"),
    "graphql": re.compile(r"\b(query|mutation|subscription)\s+([A-Za-z_][\w]*)?", re.I),
    "storage_keys": re.compile(r"\b(?:localStorage|sessionStorage)\.(?:getItem|setItem|removeItem)\(([^)]+)\)", re.I),
    "secret_candidates": re.compile(
        r"\b(?:AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|sk_live_[0-9A-Za-z]{16,}|xox[baprs]-[0-9A-Za-z-]{20,}|gh[pousr]_[0-9A-Za-z]{36,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})\b"
    ),
    "business_keywords": re.compile(
        r"\b(admin|internal|impersonat\w*|refund\w*|coupon\w*|invoice\w*|subscription\w*|billing|payment|invite\w*|approve\w*|permission\w*|role\w*|tenant\w*|workspace\w*|organization\w*|export\w*|import\w*|webhook\w*|featureFlag\w*|experiment\w*|debug|staging)\b",
        re.I,
    ),
}


def is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def in_scope(url: str, domains: list[str]) -> bool:
    if not domains:
        return True
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    for domain in domains:
        domain = domain.lower().lstrip("*.").rstrip(".")
        if host == domain or host.endswith("." + domain):
            return True
    return False


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data[:4096]:
        return ""
    return data.decode("utf-8", errors="ignore")


def add_match(bucket, value, source, line, context):
    if not value:
        return
    value = value.strip()
    item = bucket.setdefault(value, {"count": 0, "locations": []})
    item["count"] += 1
    if len(item["locations"]) < 8:
        item["locations"].append({"file": str(source), "line": line, "context": context.strip()[:240]})


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def context_for_offset(text: str, offset: int) -> str:
    start = max(0, offset - 100)
    end = min(len(text), offset + 140)
    return " ".join(text[start:end].split())


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def scan_text(source_id: str, text: str, kind: str = "file", metadata: dict | None = None):
    result = {
        "path": source_id,
        "kind": kind,
        "sha256_16": sha16(text),
        "bytes": len(text.encode("utf-8", errors="ignore")),
    }
    if metadata:
        result.update(metadata)
    signals = {name: {} for name in PATTERNS}

    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            if name == "api_paths":
                value = match.group(2).replace("\\u002f", "/")
            elif name == "functions":
                value = next((group for group in match.groups() if group), "")
            elif name == "storage_keys":
                value = match.group(1).strip("\"'` ")
            elif name == "graphql":
                value = " ".join(group for group in match.groups() if group)
            else:
                value = match.group(0)
            add_match(signals[name], value, source_id, line_for_offset(text, match.start()), context_for_offset(text, match.start()))

    result["signals"] = signals
    return result


def scan_file(path: Path, root: Path):
    text = read_text(path)
    source_id = str(path.relative_to(root) if root.is_dir() else path)
    return scan_text(source_id, text, "file")


def read_url_list(path: Path) -> list[str]:
    urls = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def fetch_url(url: str, timeout: float, max_bytes: int, user_agent: str):
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/javascript,text/javascript,application/json,text/plain,*/*",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            data = response.read(max_bytes + 1)
            truncated = len(data) > max_bytes
            if truncated:
                data = data[:max_bytes]
            text = data.decode("utf-8", errors="ignore")
            return {
                "ok": True,
                "url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "content_type": response.headers.get("content-type", ""),
                "truncated": truncated,
                "text": text,
            }
    except HTTPError as exc:
        body = exc.read(min(max_bytes, 65536)).decode("utf-8", errors="ignore")
        return {
            "ok": False,
            "url": url,
            "final_url": exc.geturl(),
            "status": exc.code,
            "content_type": exc.headers.get("content-type", "") if exc.headers else "",
            "error": str(exc),
            "text": body,
        }
    except URLError as exc:
        return {"ok": False, "url": url, "error": str(exc), "text": ""}
    except TimeoutError as exc:
        return {"ok": False, "url": url, "error": str(exc), "text": ""}


def source_map_urls_for_url(js_url: str, text: str) -> list[dict]:
    candidates = []
    seen = set()

    for match in SOURCE_MAP_RE.finditer(text):
        value = match.group(1).strip().strip("\"'")
        if value.startswith("data:"):
            continue
        resolved = urljoin(js_url, value)
        if resolved not in seen:
            seen.add(resolved)
            candidates.append({"url": resolved, "source": "sourceMappingURL"})

    parsed = urlparse(js_url)
    no_query = parsed._replace(query="", fragment="").geturl()
    implicit = [no_query + ".map"]
    if no_query.endswith(".js"):
        implicit.append(no_query[:-3] + ".map")
    for candidate in implicit:
        if candidate not in seen:
            seen.add(candidate)
            candidates.append({"url": candidate, "source": "implicit"})
    return candidates


def source_map_files_for_path(path: Path, text: str) -> list[dict]:
    candidates = []
    seen = set()

    for match in SOURCE_MAP_RE.finditer(text):
        value = match.group(1).strip().strip("\"'")
        if value.startswith(("data:", "http://", "https://")):
            continue
        candidate = (path.parent / value).resolve()
        if candidate not in seen:
            seen.add(candidate)
            candidates.append({"path": candidate, "source": "sourceMappingURL"})

    implicit = [Path(str(path) + ".map")]
    if path.suffix == ".js":
        implicit.append(path.with_suffix(".map"))
    for candidate in implicit:
        candidate = candidate.resolve()
        if candidate not in seen:
            seen.add(candidate)
            candidates.append({"path": candidate, "source": "implicit"})
    return candidates


def safe_filename_for_url(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}".strip("/") or "index"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", raw)
    digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    return f"{safe}.{digest}"


def maybe_save(save_dir: Path | None, url: str, text: str) -> str | None:
    if not save_dir:
        return None
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / safe_filename_for_url(url)
    path.write_text(text, encoding="utf-8", errors="ignore")
    return str(path)


def scan_urls(urls: list[str], args):
    files = []
    fetches = []
    source_maps = []
    seen = set()
    save_dir = Path(args.save_dir).expanduser().resolve() if args.save_dir else None

    def fetch_and_scan(url: str, kind: str, discovered_from: str | None = None, map_source: str | None = None):
        if url in seen:
            return None
        seen.add(url)
        if not in_scope(url, args.scope_domain):
            fetches.append({"url": url, "skipped": True, "reason": "out_of_scope"})
            return None
        fetched = fetch_url(url, args.timeout, args.max_bytes, args.user_agent)
        fetch_meta = {key: value for key, value in fetched.items() if key != "text"}
        fetches.append(fetch_meta)
        text = fetched.get("text", "")
        if not text:
            return fetched
        saved_path = maybe_save(save_dir, fetched.get("final_url") or url, text)
        metadata = {
            "url": url,
            "final_url": fetched.get("final_url", url),
            "status": fetched.get("status"),
            "content_type": fetched.get("content_type", ""),
            "saved_path": saved_path,
        }
        if discovered_from:
            metadata["discovered_from"] = discovered_from
        if map_source:
            metadata["source_map_source"] = map_source
        files.append(scan_text(fetched.get("final_url") or url, text, kind, metadata))
        return fetched

    for index, url in enumerate(urls):
        fetched = fetch_and_scan(url, "url")
        if args.discover_source_maps and fetched and fetched.get("text"):
            for item in source_map_urls_for_url(fetched.get("final_url") or url, fetched["text"]):
                source_maps.append({"js_url": url, **item})
                if index or args.rate:
                    time.sleep(args.rate)
                fetch_and_scan(item["url"], "source_map_url", url, item["source"])
        if index < len(urls) - 1 and args.rate:
            time.sleep(args.rate)

    return files, fetches, source_maps


def scan_local(root: Path, discover_source_maps: bool):
    files = []
    source_maps = []
    seen = set()

    for path in iter_files(root):
        real = path.resolve()
        if real in seen:
            continue
        seen.add(real)
        text = read_text(path)
        files.append(scan_text(str(path.relative_to(root) if root.is_dir() else path), text, "file"))
        if discover_source_maps and path.suffix.lower() in {".js", ".mjs", ".cjs"}:
            for item in source_map_files_for_path(path, text):
                source_maps.append({"js_file": str(path), "path": str(item["path"]), "source": item["source"]})
                if item["path"].is_file() and item["path"] not in seen:
                    seen.add(item["path"])
                    files.append(scan_text(str(item["path"]), read_text(item["path"]), "source_map_file", {
                        "discovered_from": str(path),
                        "source_map_source": item["source"],
                    }))
    return files, source_maps


def summarize(files):
    summary = {name: {} for name in PATTERNS}
    for file_result in files:
        for name, values in file_result["signals"].items():
            for value, item in values.items():
                target = summary[name].setdefault(value, {"count": 0, "locations": []})
                target["count"] += item["count"]
                target["locations"].extend(item["locations"][: max(0, 8 - len(target["locations"]))])
    return summary


def to_markdown(report):
    lines = ["# JS Extraction Report", "", "## Corpus", ""]
    for item in report["files"]:
        label = item.get("url") or item["path"]
        extra = []
        if item.get("kind"):
            extra.append(item["kind"])
        if item.get("status"):
            extra.append(f"HTTP {item['status']}")
        if item.get("content_type"):
            extra.append(item["content_type"].split(";")[0])
        suffix = ", ".join(extra)
        lines.append(f"- `{label}` ({item['bytes']} bytes, sha256:{item['sha256_16']}{', ' + suffix if suffix else ''})")

    if report.get("source_maps"):
        lines.extend(["", "## Source Maps", ""])
        for item in report["source_maps"]:
            source = item.get("url") or item.get("path")
            parent = item.get("js_url") or item.get("js_file")
            lines.append(f"- `{source}` from `{parent}` via `{item.get('source')}`")

    if report.get("fetches"):
        failed = [item for item in report["fetches"] if not item.get("ok") and not item.get("skipped")]
        skipped = [item for item in report["fetches"] if item.get("skipped")]
        if failed or skipped:
            lines.extend(["", "## Fetch Issues", ""])
            for item in failed[:80]:
                lines.append(f"- `{item.get('url')}` failed: {item.get('status', '')} {item.get('error', '')}".strip())
            for item in skipped[:80]:
                lines.append(f"- `{item.get('url')}` skipped: {item.get('reason')}")

    for section, values in report["summary"].items():
        lines.extend(["", f"## {section.replace('_', ' ').title()}", ""])
        if not values:
            lines.append("- No matches.")
            continue
        for value, item in sorted(values.items(), key=lambda pair: (-pair[1]["count"], pair[0].lower()))[:80]:
            loc = item["locations"][0] if item["locations"] else {}
            lines.append(f"- `{value}` ({item['count']}x) first seen at `{loc.get('file', '?')}:{loc.get('line', '?')}`")
    return "\n".join(lines) + "\n"


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Extract bug bounty recon signals from JavaScript, URLs, source maps, and frontend artifacts.")
    parser.add_argument("path", nargs="?", help="File, directory, or single JS URL to scan")
    parser.add_argument("--url", action="append", default=[], help="JS URL to fetch and scan; can be repeated")
    parser.add_argument("--url-list", help="File containing JS URLs, one per line")
    parser.add_argument("--scope-domain", action="append", default=[], help="Allowed domain or wildcard domain; repeat for multiple domains")
    parser.add_argument("--discover-source-maps", action=argparse.BooleanOptionalAction, default=True, help="Discover and scan source maps")
    parser.add_argument("--save-dir", help="Optional directory to save fetched JS/source maps")
    parser.add_argument("--timeout", type=float, default=15.0, help="HTTP timeout in seconds")
    parser.add_argument("--rate", type=float, default=0.0, help="Delay between HTTP requests in seconds")
    parser.add_argument("--max-bytes", type=int, default=10_000_000, help="Maximum bytes to read per URL")
    parser.add_argument("--user-agent", default="Mozilla/5.0 js-parser-hunter/1.0", help="HTTP User-Agent")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    urls = list(args.url)
    if args.url_list:
        urls.extend(read_url_list(Path(args.url_list).expanduser()))

    files = []
    fetches = []
    source_maps = []
    roots = []

    if args.path:
        if is_url(args.path):
            urls.append(args.path)
        else:
            root = Path(args.path).expanduser().resolve()
            roots.append(str(root))
            local_files, local_maps = scan_local(root, args.discover_source_maps)
            files.extend(local_files)
            source_maps.extend(local_maps)

    if urls:
        url_files, fetches, url_maps = scan_urls(urls, args)
        files.extend(url_files)
        source_maps.extend(url_maps)

    if not files and not urls and not args.path:
        parser.error("provide a file/directory path, --url, or --url-list")

    report = {
        "roots": roots,
        "url_count": len(urls),
        "file_count": len(files),
        "files": files,
        "fetches": fetches,
        "source_maps": source_maps,
        "summary": summarize(files),
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(to_markdown(report), end="")


if __name__ == "__main__":
    main()
