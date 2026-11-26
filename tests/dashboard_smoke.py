"""Execute the Streamlit app and check key widgets on a synthetic database."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "dashboard_app.py"), default_timeout=60).run()
assert not app.exception, [str(e) for e in app.exception]
assert not app.error, [str(e) for e in app.error]
metrics = {m.label: m.value for m in app.metric}
assert metrics["Delivered orders"] == "1", metrics
assert metrics["Customer payments (BRL)"] == "12.00", metrics
assert metrics["Late delivery rate"] == "0.0%", metrics
print("Streamlit runtime smoke test passed:", metrics)
