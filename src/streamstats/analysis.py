import logging

logger = logging.getLogger(__name__) # свой логгер
from dataclasses import dataclass, field
from datetime import datetime

from .errors import InvalidEventError
from .models import Event, validate_event
from .parsers import get_parsers


@dataclass
class Stats:
    """
    Класс для хранения и агрегации статистики по событиям.
    """
    total: int = 0
    by_level: dict = field(default_factory=dict) # default_factory (новый файл, новый словарь)
    by_source: dict = field(default_factory=dict)
    errors_by_source: dict = field(default_factory=dict)
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    skipped: int = 0

    # МЕТОД add (Добавление в статистику)
    def add(self, event: Event):
        """
        Добавляет одно событие в статистику (обновляет счетчики и время).
        """
        self.total += 1 # Плюс 1 отчёт

        # Здесь присваиваем вид события как ключ в левой части и заносим в словарь
        # В правой части если нет такого ключа то возвращаем 0 и добавляем +1, и потом просто +1
        self.by_level[event.level] = self.by_level.get(event.level, 0) + 1 
        self.by_source[event.source] = self.by_source.get(event.source, 0) + 1

        # Если событие вызвало ошибку:
        if event.is_error():
            self.errors_by_source[event.source] = self.errors_by_source.get(event.source, 0) + 1
        # Если событий (и времени) ещё не было или новое время меньше самого малого текущего:    
        if self.first_ts is None or event.timestamp < self.first_ts:
            self.first_ts = event.timestamp
        # Аналогично, если не было событий и текущее время больше времени самого позднего события    
        if self.last_ts is None or event.timestamp > self.last_ts:
            self.last_ts = event.timestamp

    # МЕТОД merge (сливание другого объекта Stats в текущий)
    def merge(self, other):
        """
        Объединяет статистику из другого объекта Stats в текущий.
        """
        self.total += other.total
        self.skipped += other.skipped

        for level, count in other.by_level.items():
            self.by_level[level] = self.by_level.get(level, 0) + count

        for source, count in other.by_source.items():
            self.by_source[source] = self.by_source.get(source, 0) + count

        for source, count in other.errors_by_source.items():
            self.errors_by_source[source] = self.errors_by_source.get(source, 0) + count
        
        if other.first_ts is not None and (self.first_ts is None or other.first_ts < self.first_ts):
            self.first_ts = other.first_ts

        if other.last_ts is not None and (self.last_ts is None or other.last_ts > self.last_ts):
            self.last_ts = other.last_ts

    def top_errors(self):
        """
        Возвращает топ-5 источников с наибольшим количеством ошибок.
        """
        # Превращаем словарь в список кортежей
        items = list(self.errors_by_source.items())
        
        # 2. Сортируем по значению (count) по убыванию
        # x[1] — это второе значение в паре (сам count)
        # reverse=True — от большего к меньшему
        # key=lambda x: (x[1]) — сортируем по убыванию количества ошибок
        items.sort(key=lambda x: x[1], reverse=True)
        
        # 3. Возвращаем первые 5
        return items[:5]

def analyze_files(paths, format, skip_invalid):
    """
    Читает файлы, валидирует события и возвращает общую статистику.
    """
    parser = get_parsers(format)
    total_stats = Stats()

    for path in paths:
        file_stats = Stats()

        for raw_row in parser(path):
            line_num = raw_row["_line_num"]  
            try:
                event = validate_event(raw_row)
            except InvalidEventError as e:
                if skip_invalid:
                    logger.warning(f"Skipped invalid row in {path} at line {line_num}")
                    file_stats.skipped += 1
                    continue
                else:
                    raise InvalidEventError(f"{path}, line {line_num}: {e}") from e

            file_stats.add(event)

        total_stats.merge(file_stats)
        
    return total_stats