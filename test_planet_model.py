"""py -m unittest test_planet_model.py -v"""

import os
import tempfile
import unittest

from planet_model import (
    PlanetModel,
    PlanetParseError,
    PlanetValidationError,
    parse_line,
)


class TestParseLine(unittest.TestCase):

    def test_correct_line_parsed(self):
        """Корректная строка разбирается правильно"""
        planet = parse_line('3389.5 planeta "Марс" 1877.08.12')
        self.assertEqual(planet.name, 'Марс')
        self.assertEqual(planet.planet_type, 'planeta')
        self.assertAlmostEqual(planet.radius, 3389.5)
        self.assertEqual(planet.date, '1877.08.12')

    def test_field_order_does_not_matter(self):
        """Порядок полей в строке не важен"""
        planet = parse_line('"Земля" 6371.0 1600.01.01 planeta')
        self.assertEqual(planet.name, 'Земля')
        self.assertAlmostEqual(planet.radius, 6371.0)

    def test_invalid_line_raises_error(self):
        """пустая строка PlanetParseError."""
        with self.assertRaises(PlanetParseError):
            parse_line('пустая строка')

    def test_negative_radius_raises_error(self):
        """Отрицательный радиус PlanetValidationError"""
        with self.assertRaises(PlanetValidationError):
            parse_line('-100.0 planeta "Земля" 1600.01.01')

    def test_bad_date_format_raises_error(self):
        """Дата в неверном формате не распознаётся PlanetParseError"""
        with self.assertRaises(PlanetParseError):
            parse_line('6371.0 planeta "Земля" 2000-01-01')


class TestPlanetModel(unittest.TestCase):

    def _make_model(self, content: str) -> PlanetModel:
        """Создаёт модель из временного файла с заданным содержимым"""
        self.tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', encoding='utf-8', delete=False
        )
        self.tmp.write(content)
        self.tmp.close()
        return PlanetModel(self.tmp.name)

    def tearDown(self):
        if hasattr(self, 'tmp') and os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_invalid_lines_are_skipped(self):
        """Некорректные строки пропускаются, корректные загружаются"""
        model = self._make_model(
            '3389.5 planeta "Марс" 1877.08.12\n'
            'не то\n'
            '6371.0 planeta "Земля" 1600.01.01\n'
        )
        self.assertEqual(len(model.planets), 2)

    def test_add_planet_saves_and_reloads(self):
        """После добавления планета сохраняется в файл и загружается"""
        model = self._make_model('')
        model.add_planet('Нептун', 'planeta', 24622.0, '1846.09.23')
        model2 = PlanetModel(model.filename)
        self.assertEqual(len(model2.planets), 1)
        self.assertEqual(model2.planets[0].name, 'Нептун')

    def test_add_planet_invalid_data_raises_error(self):
        """Добавление планеты с неверными данными PlanetValidationError"""
        model = self._make_model('')
        with self.assertRaises(PlanetValidationError):
            model.add_planet('', 'planeta', -1.0, '2000-01-01')

    def test_delete_planet_removes_correct_one(self):
        """Удаляется именно выбранная планета, остальные остаются."""
        model = self._make_model(
            '3389.5 planeta "Марс" 1877.08.12\n'
            '6371.0 planeta "Земля" 1600.01.01\n'
        )
        model.delete_planet(0)
        self.assertEqual(len(model.planets), 1)
        self.assertEqual(model.planets[0].name, 'Земля')

    def test_delete_invalid_index_raises_error(self):
        """Удаление по несуществующему индексу бросает IndexError."""
        model = self._make_model('')
        with self.assertRaises(IndexError):
            model.delete_planet(0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
