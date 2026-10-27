from streamstats.analysis import analyze_files


def test_analyze_files_csv(tmp_path):
    # Создаем временный CSV файл
    file = tmp_path / "data.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2024-01-15T10:00:00,ERROR,db,timeout\n"
        "2024-01-15T10:00:05,INFO,auth,login\n"
        "2024-01-15T10:00:10,ERROR,db,disk full\n",
        encoding="utf-8"
    )
    
    # Запускаем функцию
    stats = analyze_files([file], "csv", False)
    
    # Проверяем результаты
    assert stats.total == 3
    assert stats.by_level == {"ERROR": 2, "INFO": 1}
    assert stats.by_source == {"db": 2, "auth": 1}
    assert stats.errors_by_source == {"db": 2}