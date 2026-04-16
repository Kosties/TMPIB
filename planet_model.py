import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('planets.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlanetParseError(Exception):
    """Ошибка разбора строки с данными планеты."""
    pass


class PlanetValidationError(Exception):
    """Ошибка валидность полей планеты."""
    pass

class Planet:
    def __init__(self, name: str, planet_type: str, radius: float, date: str):
        self.name = name
        self.planet_type = planet_type
        self.radius = radius
        self.date = date

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'type': self.planet_type,
            'radius': self.radius,
            'date': self.date
        }

    def __repr__(self):
        return f'Planet(name={self.name!r}, type={self.planet_type!r}, radius={self.radius}, date={self.date!r})'



def _split_line(line: str) -> list[str]:
    """Разбивает строку"""
    parts = []
    current = ''
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
            current += char
        elif char == ' ' and not in_quotes:
            if current:
                parts.append(current)
                current = ''
        else:
            current += char

    if current:
        parts.append(current)

    return parts


def _validate_date(date: str) -> None:
    """Проверка даты"""
    parts = date.split('.')
    if len(parts) != 3:
        raise PlanetValidationError(f'Дата должна быть в формате ГГГГ.ММ.ДД, получено: {date!r}')
    year_str, month_str, day_str = parts
    if not (year_str.isdigit() and month_str.isdigit() and day_str.isdigit()):
        raise PlanetValidationError(f'Дата содержит нечисловые части: {date!r}')
    month = int(month_str)
    day = int(day_str)
    if not (1 <= month <= 12):
        raise PlanetValidationError(f'Некорректный месяц в дате: {date!r}')
    if not (1 <= day <= 31):
        raise PlanetValidationError(f'Некорректный день в дате: {date!r}')


def parse_line(line: str) -> Planet:

    parts = _split_line(line)

    name = None
    planet_type = None
    radius = None
    date = None

    for part in parts:
        if part.startswith('"') and part.endswith('"') and len(part) >= 2:
            name = part.strip('"')

        elif part.isalpha():
            planet_type = part
        elif '.' in part:
            dots = part.count('.')
            if dots == 2:
                date = part
            elif dots == 1:
                try:
                    radius = float(part)
                except ValueError:
                    raise PlanetParseError(f'Не удалось прочитать радиус из {part!r}')

        elif part.lstrip('-').isdigit():
            radius = float(part)


    if name is None:
        raise PlanetParseError('Отсутствует название планеты')
    if planet_type is None:
        raise PlanetParseError(f'Отсутствует тип планеты (строка: {line!r})')
    if radius is None:
        raise PlanetParseError(f'Отсутствует радиус планеты (строка: {line!r})')
    if date is None:
        raise PlanetParseError(f'Отсутствует дата открытия (строка: {line!r})')
    if radius <= 0:
        raise PlanetValidationError(f'Радиус должен быть положительным числом, получено: {radius}')

    _validate_date(date)

    return Planet(name=name, planet_type=planet_type, radius=radius, date=date)

DEFAULT_CONTENT = (
    '3389.5 planeta "Марс" 1877.08.12\n'
    '69911.0 planeta "Юпитер" 1610.01.07\n'
    '6051.8 planeta "Венера" 1620.01.01\n'
    '6371.0 planeta "Земля" 1600.01.01\n'
)


class PlanetModel:
    def __init__(self, filename: str = 'planets.txt'):
        self.filename = filename
        self.planets: list[Planet] = []
        self.load()



    def load(self) -> None:
        """Читает файл и загружает планеты"""
        try:
            lines = self._read_file_lines()
        except OSError as e:
            logger.error('Не удалось прочитать файл %s: %s', self.filename, e)
            return

        self.planets = []
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                planet = parse_line(line)
                self.planets.append(planet)
                logger.info('Строка %d: загружена планета %r', line_num, planet.name)
            except (PlanetParseError, PlanetValidationError) as e:
                logger.warning('Строка %d пропущена — %s | Содержимое: %r', line_num, e, line)

    def _read_file_lines(self) -> list[str]:
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            logger.info('Файл %s не найден — создаётся с данными по умолчанию', self.filename)
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write(DEFAULT_CONTENT)
            with open(self.filename, 'r', encoding='utf-8') as f:
                return f.readlines()


    def save(self) -> None:
        """Сохраняет список планет в файл."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                for p in self.planets:
                    f.write(f'{p.radius} {p.planet_type} "{p.name}" {p.date}\n')
            logger.info('Файл %s сохранён (%d планет)', self.filename, len(self.planets))
        except OSError as e:
            logger.error('Не удалось сохранить файл %s: %s', self.filename, e)
            raise


    def add_planet(self, name: str, planet_type: str, radius: float, date: str) -> Planet:
        if not name or not name.strip():
            raise PlanetValidationError('Название не может быть пустым')
        if not planet_type or not planet_type.strip():
            raise PlanetValidationError('Тип не может быть пустым')
        if radius <= 0:
            raise PlanetValidationError(f'Радиус должен быть положительным числом, получено: {radius}')
        _validate_date(date)

        planet = Planet(name=name.strip(), planet_type=planet_type.strip(), radius=radius, date=date)
        self.planets.append(planet)
        logger.info('Добавлена планета: %r', planet)
        self.save()
        return planet

    def delete_planet(self, index: int) -> None:
        if index < 0 or index >= len(self.planets):
            raise IndexError(f'Нет планеты с индексом {index}')
        removed = self.planets.pop(index)
        logger.info('Удалена планета: %r', removed)
        self.save()

    def get_all(self) -> list[Planet]:
        return list(self.planets)
