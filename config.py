
import os
import configparser
from pathlib import Path

_PROXY_INI_PATH = Path(__file__).resolve().parent / "config.ini"


def _load_proxy_ini():
    parser = configparser.ConfigParser()
    if _PROXY_INI_PATH.exists():
        parser.read(_PROXY_INI_PATH)
    return parser


_proxy_ini = _load_proxy_ini()


def _get_proxy_setting(section, key, env_var, default=None):
    """Env var > config.ini > default."""
    if env_var in os.environ and os.environ[env_var] != "":
        return os.environ[env_var]
    if _proxy_ini.has_option(section, key):
        return _proxy_ini.get(section, key)
    return default


class ProxyConfig:
    """US proxy settings for Selenium's ChromeOptions."""

    enabled = _get_proxy_setting("proxy", "enabled", "PROXY_ENABLED", "true").lower() == "true"
    host = _get_proxy_setting("proxy", "host", "PROXY_HOST", "")
    port = _get_proxy_setting("proxy", "port", "PROXY_PORT", "")
    username = _get_proxy_setting("proxy", "username", "PROXY_USERNAME", "")
    password = _get_proxy_setting("proxy", "password", "PROXY_PASSWORD", "")
    scheme = _get_proxy_setting("proxy", "scheme", "PROXY_SCHEME", "http")

    @classmethod
    def is_authenticated(cls):
        return bool(cls.username and cls.password)

    @classmethod
    def server_address(cls):
        return f"{cls.host}:{cls.port}"

    @classmethod
    def as_chrome_arg(cls):
        return f"{cls.scheme}://{cls.host}:{cls.port}"

    @classmethod
    def validate(cls):
        if not cls.enabled:
            return
        if not cls.host or not cls.port:
            raise ValueError(
                "Proxy is enabled but PROXY_HOST/PROXY_PORT (or config.ini "
                "[proxy] host/port) are not set."
            )


class SchedulerConfig:
    """How often the bot runs and how much jitter to add."""

    interval_minutes = int(_get_proxy_setting("scheduler", "interval_minutes", "SCHEDULER_INTERVAL_MINUTES", "60"))
    max_jitter_minutes = int(_get_proxy_setting("scheduler", "max_jitter_minutes", "SCHEDULER_MAX_JITTER_MINUTES", "60"))
    run_once = _get_proxy_setting("scheduler", "run_once", "SCHEDULER_RUN_ONCE", "false").lower() == "true"


class ReportConfig:
    """Configuration for status reports."""
    output_dir = _get_proxy_setting("reporting", "output_dir", "REPORT_OUTPUT_DIR", "reports")



    from pathlib import Path
SITES = [ 
        {"name": "Signage Inc"},
        {"name": "Signize Us"}, 
        {"name": "QuickSignage Landing page 1"},
        {"name": "QuickSignage Landing page 2"},
        {"name": "Signmakerz.com"},
        {"name": "Signs Inc Landing page 1"},
        {"name": "Signs.inc Landing page 2"}, ]
TARGET_SITES = [
    {
        "name": "Signs Inc - Primary",
        "visit_url": "https://signsync.marke-ter.online/demo",  
        "endpoint_filter": "https://signsync.marke-ter.online/api/submit/signsinc",
        "method": "POST",
        "expected_fields": [
            "airtable_data.id",
            "airtable_data.createdTime",
            "airtable_data.fields.Name",
            "airtable_data.fields.Email",
            "airtable_data.fields.Phone",
            "airtable_data.fields.Image",
            "airtable_data.fields.Details",
            "airtable_data.fields.Acrylic Storefront",
            "airtable_data.fields.Usage Input",
            "airtable_data.fields.Created_At",
            "airtable_data.fields.status",
            "airtable_data.fields.Created_at_Alt",
            "airtable_data.fields.Time_(Creation to Mockup)",
            "airtable_data.fields.Last Modified",
            "airtable_data.fields.Lead Source",
        ],
        "report_row": [
  
            {"label": "QA Test-", "source": "airtable_data.fields.Name"},
            {"label": "Email", "source": "airtable_data.fields.Email"},
            {"label": "Record ID", "source": "airtable_data.id"},
            {"label": "Date (PKT)", "source": "airtable_data.createdTime", "type": "date"},
            {"label": "Time (PKT)", "source": "airtable_data.createdTime", "type": "time"},
            {"label": "Request URL", "source": "$request.url"},
            {"label": "Method", "source": "$request.method"},
            {"label": "Status", "source": "$response.status"},
        ],
    },
]



OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LEAD_MD_PATH = OUTPUT_DIR / "leadpage_status.md"
LEAD_HTML_PATH = OUTPUT_DIR / "leadpage_status.html"
LEAD_PDF_PATH = OUTPUT_DIR / "leadpage_status.pdf"

WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
CAPTURE_HEADERS = True
