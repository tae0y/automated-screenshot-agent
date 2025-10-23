CREATE TABLE IF NOT EXISTS web_audit (
  id BIGSERIAL PRIMARY KEY,
  site_url TEXT NOT NULL,
  crawl_ts TIMESTAMPTZ NOT NULL,
  model TEXT NOT NULL,
  latency_ms INT NOT NULL,
  ui_components JSONB NOT NULL,
  layout_state JSONB NOT NULL,
  data_content JSONB NOT NULL,
  browser_console_errors JSONB NOT NULL,
  error_count INT NOT NULL,
  art_html_path TEXT NOT NULL,
  art_screenshot_path TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_web_audit_site_ts ON web_audit(site_url, crawl_ts DESC);
