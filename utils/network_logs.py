
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import pytz

PKT = pytz.timezone("Asia/Karachi")


def _to_pkt_dt(iso_str: str) -> Optional[datetime]:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone(PKT)
    except Exception:
        return None


def _parse_performance_log_entry(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        message = json.loads(entry["message"])["message"]
        return {
            "method": message.get("method"),
            "params": message.get("params", {}),
        }
    except Exception:
        return None


def collect_network_events(driver) -> List[Dict[str, Any]]:
    raw_logs = driver.get_log("performance")
    events = []
    for e in raw_logs:
        parsed = _parse_performance_log_entry(e)
        if parsed:
            events.append(parsed)
    return events


def filter_requests(events: List[Dict[str, Any]], url_filter: str, method_filter: str = "POST") -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for ev in events:
        m = ev["method"]
        p = ev["params"]
        if m == "Network.requestWillBeSent":
            req = p.get("request", {})
            url = req.get("url", "")
            method = req.get("method", "")
            if url_filter in url and method == method_filter:
                rid = p.get("requestId")
                result.setdefault(rid, {})["request"] = {
                    "url": url,
                    "method": method,
                    "headers": req.get("headers", {}),
                    "ts": p.get("timestamp"),
                }
        elif m == "Network.responseReceived":
            resp = p.get("response", {})
            url = resp.get("url", "")
            rid = p.get("requestId")
            if url_filter in url and rid is not None:
                result.setdefault(rid, {})["response"] = {
                    "url": url,
                    "status": resp.get("status"),
                    "statusText": resp.get("statusText"),
                    "headers": resp.get("headers", {}),
                    "mimeType": resp.get("mimeType"),
                    "ts": p.get("timestamp"),
                }
    return result


def get_response_body(driver, request_id: str, retries: int = 3, delay: float = 1.0) -> Optional[Dict[str, Any]]:
    for attempt in range(retries):
        try:
            body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            text = body.get("body", "")
            if not text:
                time.sleep(delay)
                continue
            if body.get("base64Encoded"):
                import base64
                text = base64.b64decode(text).decode("utf-8", errors="ignore")
            return json.loads(text)
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def _get_post_payload(driver, req_id: str, debug: bool = False) -> Optional[Dict[str, Any]]:
    """Fallback: read request POST payload when response body is blocked by CDP."""
    try:
        result = driver.execute_cdp_cmd(
            "Network.getRequestPostData", {"requestId": req_id}
        )
        post_data = result.get("postData", "")
        if debug:
            print(f"📤 POST payload: {post_data[:300]}")
        if post_data:
            parsed = json.loads(post_data)
            # Signize sends PATCH with {"records": [{"id": "rec...", "fields": {...}}]}
            records = parsed.get("records", [])
            if records:
                return {
                    "airtable_data": {
                        "id":          records[0].get("id", ""),
                        "fields":      records[0].get("fields", {}),
                        "createdTime": ""
                    }
                }
            return parsed
    except Exception as e:
        if debug:
            print(f"⚠️ getRequestPostData failed: {e}")
    return None


def _dig(data: Dict[str, Any], path: str) -> Any:
    cur: Any = data
    for key in path.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def map_report_row(row_cfg: List[Dict[str, Any]], body: Dict[str, Any], meta: Dict[str, Any]) -> List[str]:
    out = []
    for col in row_cfg:
        src = col["source"]
        typ = col.get("type")
        val = None
        if src.startswith("$"):
            if src == "$request.url":
                val = meta.get("request", {}).get("url")
            elif src == "$request.method":
                val = meta.get("request", {}).get("method")
            elif src == "$response.status":
                val = meta.get("response", {}).get("status")
        else:
            raw = _dig(body, src)
            if typ in ("date", "time") and isinstance(raw, str):
                pkt_dt = _to_pkt_dt(raw)
                if pkt_dt:
                    if typ == "date":
                        val = pkt_dt.strftime("%-m/%-d/%Y")
                    else:
                        val = pkt_dt.strftime("%-I:%M%p PKT").lower()
            else:
                val = raw
        out.append("" if val is None else str(val))
    return out


def find_airtable_record(driver, endpoint_filter: str, return_meta: bool = False, debug: bool = False):
    events = collect_network_events(driver)

    matched = filter_requests(events, endpoint_filter, "PATCH")  # ✅ first
    matched.update(filter_requests(events, endpoint_filter, "POST"))
    if debug:
        print(f"🔍 Matched {len(matched)} requests for endpoint: {endpoint_filter}")

    for req_id, meta in matched.items():

        # ✅ Skip failed responses (4xx, 5xx)
        status = meta.get("response", {}).get("status", 200)
        if status and status >= 400:
            if debug:
                print(f"⏭️ Skipping request {req_id} — status {status}")
            continue

        # Try response body first
        body = get_response_body(driver, req_id)

        # ✅ Fallback to POST payload (Signize Us: direct Airtable call, CDP blocks response)
        if not body:
            body = _get_post_payload(driver, req_id, debug=debug)

        if debug:
            print(f"\n📦 Request ID: {req_id}")
            print("Meta:", meta)
            print("Body:", body)

        if not body:
            continue

        # Already wrapped by _get_post_payload
        if "airtable_data" in body and "fields" in body.get("airtable_data", {}):
            return (body, meta) if return_meta else body

        airtable = body.get("airtable_data") or body.get("airtableData")
        if airtable:
            if isinstance(airtable, dict) and "body" in airtable:
                # ✅ Keep full structure — report_writer handles body → records[0]
                records = airtable["body"].get("records")
                if isinstance(records, list) and records:
                    return (body, meta) if return_meta else body
            else:
                body["airtable_data"] = airtable
                return (body, meta) if return_meta else body

        records = body.get("records")
        if isinstance(records, list) and records:
            body["airtable_data"] = records[0]
            return (body, meta) if return_meta else body

        form_data = body.get("form_data")
        if isinstance(form_data, dict):
            body["airtable_data"] = form_data
            return (body, meta) if return_meta else body

        # ✅ Handle {"success": true, "data": {...}} or {"status": "success", "data": {...}} shape (SignsInc2, prospects, BoostUp)
        data_field = body.get("data")
        if isinstance(data_field, dict) and (body.get("success") or body.get("status") == "success" or "airtableRecordId" in body):
            body["airtable_data"] = {
                "id": body.get("airtableRecordId") or data_field.get("airtable_record_id") or str(data_field.get("id", "")),
                "createdTime": data_field.get("created_at") or data_field.get("updated_at") or "",
                "fields": {
                    "Name": data_field.get("name", "") or data_field.get("Name", ""),
                    "Email": data_field.get("email", "") or data_field.get("Email", ""),
                    "Phone": data_field.get("phone", "") or data_field.get("Phone", ""),
                }
            }
            return (body, meta) if return_meta else body

        # ✅ Handle {"database_record": {...}} shape (Signage Inc two-step)
        database_record = body.get("database_record")
        if isinstance(database_record, dict):
            body["airtable_data"] = database_record
            return (body, meta) if return_meta else body

    return (None, None) if return_meta else None