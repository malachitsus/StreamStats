import json

from streamstats.__main__ import main


def test_cli_success(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2024-01-15T10:00:00,ERROR,db,timeout\n"
        "2024-01-15T10:00:05,INFO,auth,login\n",
        encoding="utf-8"
    )
    out_file = tmp_path / "report.json"

    args = ["analyze", str(csv_file), "--format", "csv", "--output", str(out_file)]
    exit_code = main(args)

    assert exit_code == 0 # ожидается успех (код 0)
    assert out_file.exists() # файл с репортом создался

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["total"] == 2 # ожидается 2 строки
        assert data["by_level"]["ERROR"] == 1 # ошибка одна


def test_cli_bad_line_strict(tmp_path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2024-01-15T10:00:00,blablablableblebleblublublu,db,timeout\n",
        encoding="utf-8"
    )
    out_file = tmp_path / "report.json"

    args = ["analyze", str(csv_file), "--format", "csv", "--output", str(out_file)]
    exit_code = main(args)

    assert exit_code == 2 # ожидается невалидная стрчока
    assert not out_file.exists() # ошибка стопнула создания файла репорта


def test_cli_skip_invalid(tmp_path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2024-01-15T10:00:00,POTUZHNOST,db,timeout\n"
        "2024-01-15T10:00:05,INFO,auth,login\n",
        encoding="utf-8"
    )
    out_file = tmp_path / "report.json"

    args = ["analyze", str(csv_file), "--format", "csv", "--output", str(out_file), "--skip-invalid"]
    exit_code = main(args)

    assert exit_code == 0 # ошибки скипаются, программа завершается успешно
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["total"] == 1 # тут только правильные строки
        assert data["skipped"] == 1 # забраковать одну ошибку