import flask
import g4f
import threading
import markdown as md
app = flask.Flask(__name__)

TOPICS = [
    "Что такое Python и установка",
    "Первая программа print()",
    "Переменные и типы данных (int, float, str, bool)",
    "Операторы и приоритет операций",
    "Ввод данных input() и конвертация типов",
    "Условные конструкции: if / elif / else",
    "Циклы: for и while, структура цикла",
    "Операторы break, continue, pass",
    "Функции: def, параметры, return",
    "Аргументы функций: позиционные, именованные, *args, **kwargs",
    "Списки (list): создание, методы, срезы",
    "Кортежи (tuple): неизменяемые последовательности",
    "Множества (set): свойства и операции",
    "Словари (dict): ключи, значения, итерация",
    "Строки: методы строк, форматирование, f-строки",
    "Работа с файлами: open, read, write, with",
    "Исключения и обработка ошибок: try/except/finally",
    "Модули и пакеты: импорт, структура проекта",
    "__name__ == '__main__': зачем и как",
    "Лямбда-функции и генераторы списков",
    "Итераторы и генераторы (yield)",
    "Декораторы: зачем и как писать",
    "ООП: классы, объекты, self",
    "Атрибуты и методы экземпляра",
    "Конструкторы: __init__",
    "Наследование и полиморфизм",
    "Инкапсуляция и приватные атрибуты",
    "Магические методы: __str__, __repr__, __len__, __iter__",
    "Работа с датами и временем (datetime)",
    "Модуль random: генерация случайных чисел",
    "Регулярные выражения (re)",
    "Работа с JSON и сериализация",
    "CSV: чтение/запись табличных данных",
    "argparse: аргументы командной строки",
    "Логирование с logging",
    "Unit-тесты с unittest",
    "doctest и Pytest",
    "Профилирование и оптимизация кода",
    "Алгоритмы: сортировки, поиск",
    "Структуры данных: стек, очередь, список, дерево",
    "Рекурсия: примеры и обработка глубины",
    "Асинхронность: async/await",
    "Многопоточность: threading (ограничения GIL)",
    "Многопроцессорность: multiprocessing",
    "subprocess: запуск внешних процессов",
    "Работа с системными путями: os и pathlib",
    "Безопасность ввода: валидация и защита",
    "Оптимизация памяти: профайлинг и советы",
    "Создание консольных утилит (на примере TODO-менеджера)",
    "Серийные форматы: pickle, yaml",
    "Практики чистого кода (PEP8, PEP20)",
    "Докстринги и аннотации типов",
    "CI/CD: автоматизированные тесты и проверки",
    "Подготовка production-скриптов и дистрибуция",
    "pip и управление зависимостями",
    "venv и виртуальные окружения",
    "Работа с Git и GitHub",
    "Создание своих модулей и пакетов",
    "Загрузка данных из интернета (requests)",
    "Парсинг HTML (BeautifulSoup, lxml)",
    "Введение в SQLite и SQLAlchemy",
    "Flask: первые шаги",
    "FastAPI: современный подход",
    "Итоговый проект: консольный менеджер задач (TODO App)",
]

PROMPT_TEMPLATE = (
    "Ты — преподаватель Python. Объясни тему '{topic}' так, "
    "чтобы даже полный новичок понял. Ответь строго в формате:\n\n"
    "📖 Объяснение:\n...\n\n"
    "💻 Пример кода:\n```python\n...\n```\n\n"
    "🏋️‍♂️ Упражнения:\n1. ...\n2. ...\n3. ...\n\n"
    "🏡 Домашка:\n1. ...\n2. ...\n3. ...\n\n"
    "Пиши на русском языке. Код только для консоли."
)


def fetch_lesson_sync(topic: str) -> str:
    prompt = PROMPT_TEMPLATE.format(topic=topic)
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        collected = []
        for chunk in response:
            if isinstance(chunk, str):
                collected.append(chunk)
        return "".join(collected)
    except Exception as e:
        return f"[Ошибка при запросе]: {e}"


def fetch_lesson(topic: str) -> str:
    result = {}

    def task():
        result["content"] = fetch_lesson_sync(topic)

    thread = threading.Thread(target=task)
    thread.start()
    thread.join()  # ждём результат (иначе вернётся пусто)
    return result.get("content", "[Ошибка: результата нет]")


@app.route("/python")
def index():
    return flask.render_template("index.html", topics=TOPICS, show_loading="none")
@app.route("/python/howtouploadhw")
def howtouploadhw():
    return flask.render_template("howtouploadhw.html")

@app.route("/python/lesson/<int:lesson_id>")
def lessons(lesson_id):
    return flask.render_template("loading.html", id_lesson=lesson_id)


@app.route("/python/lesson_not_load/<int:lesson_id>")
def lesson(lesson_id):
    if lesson_id < 0 or lesson_id >= len(TOPICS):
        return "Тема не найдена", 404

    topic = TOPICS[lesson_id]
    content = fetch_lesson(topic)
    return flask.render_template(
        "index.html", topics=TOPICS, active=lesson_id, lesson=content, markdown=lambda text: md.markdown(
        text,
        extensions=["fenced_code", "codehilite"]
    )
    )


if __name__ == "__main__":
    app.run(debug=True)
