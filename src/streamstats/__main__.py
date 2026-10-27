import argparse
import sys

from .analysis import analyze_files
from .errors import InvalidEventError, StreamStatsError
from .report import build_report, write_report


def create_parser():
    """
    Создает и настраивает парсер аргументов командной строки.
    """
    parser = argparse.ArgumentParser(description="StreamStats log analyzer")
    subparsers = parser.add_subparsers(dest="command")
    
    # Тут создаем команду analyze
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("inputs", nargs="+", help="Files to analyze") # 1 и больше файлов можно указать
    analyze_parser.add_argument("--format", choices=["csv", "jsonl"], required=True) # обязательные флаги для выбора формата
    analyze_parser.add_argument("--output", required=True, help="Output JSON report path") # в какой json передать репорт
    analyze_parser.add_argument("--skip-invalid", action="store_true") # пропускать невалиды (да или нет)

    return parser

def main(argv=None):
    """
    Главная точка входа CLI: разбирает аргументы и управляет процессом анализа.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command != "analyze":
        parser.print_help()
        return 0

    try:
        stats = analyze_files(args.inputs, args.format, args.skip_invalid)
        
        # Собираем и пишем отчёт
        report = build_report(stats)
        write_report(report, args.output)
        return 0

    except InvalidEventError as i:
        print(f"{i}", file=sys.stderr)
        return 2

    except StreamStatsError as s:
        print(f"{s}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) # sys.exit для того чтобы ос поняла коды возврата