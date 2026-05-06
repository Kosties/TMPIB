import logging

from planet_model import Planet, PlanetModel, PlanetValidationError, _validate_date

logger = logging.getLogger(__name__)
class CommandError(Exception):
    pass


def _parse_add(args: str) -> Planet:
    parts = [p.strip() for p in args.split(';')]

    if len(parts) != 4:
        raise CommandError(
            f'ADD ожидает 4 поля через ";", получено {len(parts)}: {args!r}'
        )

    name, planet_type, radius_str, date = parts

    if not name:
        raise CommandError('ADD: название не может быть пустым')
    if not planet_type:
        raise CommandError('ADD: тип не может быть пустым')

    try:
        radius = float(radius_str)
    except ValueError:
        raise CommandError(f'ADD: радиус должен быть числом, получено: {radius_str!r}')

    if radius <= 0:
        raise CommandError(f'ADD: радиус должен быть положительным, получено: {radius}')

    try:
        _validate_date(date)
    except PlanetValidationError as e:
        raise CommandError(f'ADD: {e}')

    return Planet(name=name, planet_type=planet_type, radius=radius, date=date)


def _parse_rem(args: str) -> tuple:
    operators = ['<=', '>=', '!=', '<', '>', '=']

    for op in operators:
        if op in args:
            left, right = args.split(op, maxsplit=1)
            field = left.strip().lower()
            value = right.strip()

            allowed_fields = {'name', 'type', 'radius', 'date'}
            if field not in allowed_fields:
                raise CommandError(
                    f'REM: неизвестное поле {field!r}. '
                    f'Допустимые: {", ".join(sorted(allowed_fields))}'
                )

            return field, op, value

    raise CommandError(f'REM: не найден оператор в условии: {args!r}')


def _matches(planet: Planet, field: str, op: str, value: str) -> bool:
    planet_value = {
        'name':   planet.name,
        'type':   planet.planet_type,
        'radius': planet.radius,
        'date':   planet.date,
    }[field]

    if field == 'radius':
        try:
            value_num = float(value)
        except ValueError:
            raise CommandError(
                f'REM: для поля radius ожидается число, получено: {value!r}'
            )
        ops = {
            '=':  lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<':  lambda a, b: a <  b,
            '>':  lambda a, b: a >  b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
        }
        return ops[op](planet_value, value_num)

    if op not in ('=', '!='):
        raise CommandError(
            f'REM: оператор {op!r} не поддерживается для поля {field!r}. '
            f'Используйте = или !='
        )
    return planet_value == value if op == '=' else planet_value != value

class CommandProcessor:
    def __init__(self, model: PlanetModel):
        self.model = model

    def run_file(self, filename: str) -> None:

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error('Файл команд не найден: %s', filename)
            return
        except OSError as e:
            logger.error('Не удалось прочитать файл команд %s: %s', filename, e)
            return

        logger.info('Начало выполнения файла команд: %s', filename)

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                self._execute(line)
            except CommandError as e:
                logger.warning(
                    'Строка %d пропущена — %s | Команда: %r', line_num, e, line
                )

        logger.info('Файл команд выполнен: %s', filename)

    def _execute(self, line: str) -> None:
        parts = line.split(maxsplit=1)
        command = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ''

        if command == 'ADD':
            self._cmd_add(args)
        elif command == 'REM':
            self._cmd_rem(args)
        elif command == 'SAVE':
            self._cmd_save(args)
        else:
            raise CommandError(f'Неизвестная команда: {command!r}')

    def _cmd_add(self, args: str) -> None:
        planet = _parse_add(args)
        self.model.planets.append(planet)
        logger.info('ADD: добавлена планета %r', planet)

    def _cmd_rem(self, args: str) -> None:
        field, op, value = _parse_rem(args)
        before = len(self.model.planets)
        self.model.planets = [
            p for p in self.model.planets
            if not _matches(p, field, op, value)
        ]
        removed = before - len(self.model.planets)
        logger.info('REM %s %s %s: удалено %d планет', field, op, value, removed)

    def _cmd_save(self, args: str) -> None:
        path = args.strip()
        if not path:
            raise CommandError('SAVE: не указан путь к файлу')

        original = self.model.filename
        self.model.filename = path
        try:
            self.model.save()
        finally:
            self.model.filename = original

        logger.info('SAVE: данные сохранены в %s', path)
