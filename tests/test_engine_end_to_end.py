import json

from autoanalyst import profile_dataset
from autoanalyst.engine import AutoAnalystEngine


def test_profile_dataset_end_to_end(sample_csv_path):
    result = profile_dataset(sample_csv_path)

    d = result.to_dict()
    assert d["profile"]["data_understanding"]["n_rows"] > 0
    assert 0 <= d["profile"]["data_quality"]["overall_quality_score"] <= 100

    # JSON must round-trip cleanly (no NaN/inf/numpy types).
    json_str = result.to_json()
    parsed = json.loads(json_str)
    assert parsed["profile"]["data_quality"]["quality_grade"] in ("A+", "A", "B", "C", "D", "F")

    html = result.to_html()
    assert "<html" in html.lower()
    assert "AutoAnalyst" in html

    md = result.to_markdown()
    assert md.startswith("# AutoAnalyst")

    summary = result.console_summary()
    assert "QUALITY SCORE" in summary.upper() or "Quality Score" in summary


def test_engine_reusable_across_calls(sample_csv_path):
    engine = AutoAnalystEngine()
    r1 = engine.profile_dataset(sample_csv_path)
    r2 = engine.profile_dataset(sample_csv_path)
    assert r1.full_profile.understanding.n_rows == r2.full_profile.understanding.n_rows
