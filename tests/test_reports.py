from streamstats.report import build_report, write_report
from streamstats.analysis import Stats
import json

def test_build_and_write_report(tmp_path):
    # Пустая статистика
    stats = Stats()
    stats.total = 5
    stats.by_level = {"ERROR": 5}
    
    # Проверка build_report
    report_dict = build_report(stats)
    assert report_dict["total"] == 5 
    assert report_dict["by_level"] == {"ERROR": 5}
    assert report_dict["first_timestamp"] is None
    
    # Проверка write_report (запись в файл)
    out_file = tmp_path / "report.json"
    write_report(report_dict, out_file)
    
    # Проверка на то что json нормально конвертится
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["total"] == 5