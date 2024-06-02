from core.settings import get_rabbit_settings

TITLE_PROMPT = """
Определи, содержатся ли в запросе слова, которые могут быть частью названия фильма.
Если такие есть, перечисли их через запятую на английском. Если нет или сомневаешься, ответь: none.
Нужны именно части названия фильма. Жанры, действия, рейтинги, режиссеры и другие несвязанные слова не учитываются.
Отвечай в формате: слова через запятую или none. Без окружающего текста и пояснений.

Примеры:

Запрос: фильмы про войну
Ответ: "none"

Запрос: фильмы ужасов
Ответ: "none"

Запрос: посмотреть Звездные войны или матрицу
Ответ: "Star Wars, Matrix"

Запрос: фильмы джоржа лукаса
Ответ: "none"

Запрос: новинки тарантино
Ответ: "none"

Запрос: фильмы с Брюсом Уиллисом
Ответ: "none"

Запрос: классика кино: Крестный отец и Матрица
Ответ: "Godfather, Matrix"

Запрос: {query}
"""  # noqa: E501

RATING_PROMPT = """
Ты компьютер, который анализирует запросы на наличие уточнений по упорядочиванию результатов по рейтингу.
Определи, содержится ли в данном запросе уточнение по упорядочиванию результатов по рейтингу/популярнности.
Запрос: {query}
Если ты сомневаешься, отвечай: none.
Ответ должен быть однословним: asc, desc или none.
Примеры:
Запрос: "покажи фильмы с самым высоким рейтингом"
Ответ: desc
Запрос: "самые плохие работы тарантино"
Ответ: asc
Запрос: "какие фильмы сейчас готовятся к выходу"
Ответ: none
"""  # noqa: E501

ACTOR_PROMPT = """
Ты компьютер, который выдаёт в командную строку список актёров через запятую из запроса.
Определи, содержится ли в данном запросе уточнение по имени актёра.
Запрос: {query}
Если ты сомневаешься, ответь: none.
Если есть имена актёров, перечисли их через запятую, переводя на английский язык.
Ответ должен содержать только имена актёров через запятую или none.
Примеры:
Запрос: "фильмы с Николаем Кейджем и Натали Портман"
Ответ: "Nikolas Cage, Natalie Portman"
"""  # noqa: E501

DATE_PROMPT = """
Определи содержится ли в данном запросе уточнение по дате выхода фильма
Запрос: {query}
Если ты сомневаешься — отвечай none.
Отвечай в формате: gte:2020-01-01, lte:2021-01-01, lte:now или none
Примеры:
Запрос: новинки кинопроката
Ответ: lte:now
Запрос: Фильмы Тарантино после 1990 года
Ответ: gte:1990-01-01
Запрос: Фильмы про войну
Ответ: none
"""  # noqa: E501

DESCRIPTION_PROMPT = """
Определи, содержатся ли в запросе слова, которые могут быть частью описания фильма.
Если такие есть, перечисли их через запятую на английском. Если нет или сомневаешься, ответь: none.
Нужны именно части названия фильма. Жанры, рейтинги, режиссеры и другие несвязанные слова не учитываются.
Отвечай в формате: слова через запятую или none. Без окружающего текста и пояснений.

Примеры:

Запрос: фильмы про войну
Ответ: "war"

Запрос: фильмы ужасов
Ответ: "none"

Запрос: посмотреть Звездные войны или матрицу
Ответ: "none"

Запрос: фильмы джоржа лукаса
Ответ: "none"

Запрос: новинки тарантино
Ответ: "none"

Запрос: фильмы про путешествия в париж
Ответ: "paris"

Запрос: фильмы с Брюсом Уиллисом
Ответ: "none"

Запрос: классика кино: Крестный отец и Матрица
Ответ: "none

Запрос: {query}
"""  # noqa: E501

DIRECTOR_PROMPT = """
Ты компьютер, который выдаёт в командную строку список режиссеров через запятую из запроса.
Определи, содержится ли в данном запросе уточнение по имени режиссера.
Запрос: {query}
Если ты сомневаешься, ответь: none.
Если есть имена режиссеров, перечисли их через запятую, переводя на английский язык.
Ответ должен содержать только имена режиссеров через запятую или none.
Примеры:
Запрос: "фильмы режиссера Квентина Тарантино и Джеймса Кэмерона"
Ответ: "Quentin Tarantino, James Cameron"
"""  # noqa: E501

GENRE_PROMPT = """
Ты компьютер, который выдаёт в командную строку список жанров через зяпятую которые могут соответствовать запросу.
Определи, содержится ли в данном запросе уточнение по жанру или жанрам фильма.
Запрос: {query}
Если ты сомневаешься, отвечай: none.
Допустимые значения жанров: Action, Adventure, Fantasy, Sci-Fi, Drama, Music, Romance, Thriller, Mystery, Comedy, Animation, Family, Biography, Musical, Crime, Short, Western, Documentary, History, War, Game-Show, Reality-TV, Horror, Sport, Talk-Show, News.
Отвечай в формате: значений через запятую или none. Без лишний слов.
Примеры:
Запрос: "покажи мне фильмы в жанре Action и Comedy"
Ответ: "Action, Comedy"
Запрос: "фильмы про любовь и музыку"
Ответ: "Romance, Music"
Запрос: "какие фильмы сейчас популярны"
Ответ: "none"
"""  # noqa: E501

INDICES_PROMPT = """
Определи с поиском чего связан следущий запрос: поиск фильмов, поиск жанров или поиск персон.
Запрос: {query}
Если ты сомневаешься — отвечай none.
У тебя есть 4 варианта ответа: movies, genres, persons, none. Ответь, пожалуйста, одним словом.
"""  # noqa: E501


class Prompts:
    _settings = get_rabbit_settings()

    def __init__(self):
        self._prompts = {}
        self._configure_prompts()

    def get_prompt(self, queue: str) -> str:
        return self._prompts[queue]

    def _configure_prompts(self):

        queues = [
            self._settings.actor_queue,
            self._settings.date_filter_queue,
            self._settings.description_text_queue,
            self._settings.director_queue,
            self._settings.genre_filter_queue,
            self._settings.subject_queue,
            self._settings.rating_order_queue,
            self._settings.title_text_queue
        ]

        for queue in queues:
            match queue:
                case self._settings.actor_queue:
                    self._prompts[queue] = ACTOR_PROMPT
                case self._settings.date_filter_queue:
                    self._prompts[queue] = DATE_PROMPT
                case self._settings.description_text_queue:
                    self._prompts[queue] = DESCRIPTION_PROMPT
                case self._settings.director_queue:
                    self._prompts[queue] = DIRECTOR_PROMPT
                case self._settings.genre_filter_queue:
                    self._prompts[queue] = GENRE_PROMPT
                case self._settings.subject_queue:
                    self._prompts[queue] = INDICES_PROMPT
                case self._settings.rating_order_queue:
                    self._prompts[queue] = RATING_PROMPT
                case self._settings.title_text_queue:
                    self._prompts[queue] = TITLE_PROMPT
