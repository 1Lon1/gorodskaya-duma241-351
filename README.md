# ИС «Городская Дума»

Информационная система управления деятельностью городской Думы.  
Автоматизация учёта депутатов, комиссий, заседаний и посещаемости заседаний.

---

## О проекте

**ИС «Городская Дума»** - учебный проект, выполненный в рамках дисциплины  
«Методология и практики DevOps» (Московский Политех, направление 10.03.01  
«Информационная безопасность»).

**Предметная область:** работа городской Думы - депутаты, комиссии,  
заседания и посещаемость заседаний.

**Назначение:** автоматизация учёта депутатов, комиссий, заседаний  
и посещаемости.

**Тип приложения:** Web-приложение с HTTP API и реляционной базой данных.

---

## Архитектура

```

Пользователь
|
Web-интерфейс (HTML + CSS + JavaScript)
| HTTP
FastAPI (Python 3.13)
|
SQLAlchemy ORM
|
SQLite (duma.db)

```

**Авторизация:**

```

POST /api/auth/login  ->  JWT-токен  ->  Authorization: Bearer <token>

```

---

## Технологический стек

### Backend
- **Python 3.13**
- **FastAPI** - HTTP API
- **SQLAlchemy** - ORM
- **SQLite** - реляционная БД
- **python-jose** - JWT
- **bcrypt** - хеширование паролей
- **python-dotenv** - конфигурация через `.env`

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla JS)

---

## Структура проекта

```

gorodskaya-duma241-351/
├── backend/
│   ├── main.py                  # Точка входа FastAPI, роутеры
│   ├── auth.py                  # JWT, логин, регистрация
│   ├── database.py              # Подключение к БД, Base, session
│   ├── models.py                # SQLAlchemy-модели
│   ├── schemas.py               # Pydantic-схемы
│   ├── requirements.txt         # Зависимости backend
│   ├── duma.db                  # SQLite-БД (в .gitignore)
│   └── **pycache**/             # (в .gitignore)
├── frontend/
│   ├── index.html               # SPA-интерфейс
│   ├── style.css                # Стили
│   └── app.js                   # Логика работы с API
├── .env.example                 # Пример переменных окружения
├── .gitignore
├── README.md
└── ТЗ.docx                      # Техническое задание

```

---

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/gorodskaya-duma241-351.git
cd gorodskaya-duma241-351
```

### 2. Настройка окружения backend

Создайте виртуальное окружение и установите зависимости:

```
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Конфигурация `.env`

Скопируйте `.env.example` в `.env` и заполните значения:

```
cp .env.example .env
```

Пример содержимого `.env`:

```
SECRET_KEY=your-super-secret-key-change-me
DATABASE_URL=sqlite:///./duma.db
```

> Файл `.env` **не должен** попадать в Git. Он уже добавлен в `.gitignore`.

### 4. Запуск backend

```
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

- **API:** [http://127.0.0.1:8001](http://127.0.0.1:8001/)
- **Swagger:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Health:** [http://127.0.0.1:8001/api/health](http://127.0.0.1:8001/api/health)

База данных и таблицы создаются автоматически при первом запуске.

### 5. Запуск frontend

В отдельном терминале:

```
cd frontend
python -m http.server 5500
```

Откройте браузер: **[http://127.0.0.1:5500](http://127.0.0.1:5500/)**

---

## API

Базовый адрес локального backend: `http://127.0.0.1:8001`

### Health

| Метод | Endpoint | Описание |
|---|---|---|
| GET | `/api/health` | Проверка доступности сервиса |

**Ответ:**

```
{ "status": "ok" }
```

### Авторизация

| Метод | Endpoint | Описание |
|---|---|---|
| −POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Вход, выдача JWT-токена |

**Пример ответа `/api/auth/login`:**

```
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

Защищённые операции требуют заголовка:

```
Authorization: Bearer <token>
```

### Депутаты

| Метод | Endpoint | Auth | Описание |
|---|---|---|---|
| POST | `/api/deputies` | Да | Создать депутата |
| GET | `/api/deputies` | Нет | Список депутатов |
| GET | `/api/deputies/{id}` | Нет | Получить депутата |
| DELETE | `/api/deputies/{id}` | Да | Удалить депутата |

### Комиссии

| Метод | Endpoint | Auth | Описание |
|---|---|---|---|
| POST | `/api/commissions` | Да | Создать комиссию |
| GET | `/api/commissions` | Нет | Список комиссий |
| GET | `/api/commissions/{id}` | Нет | Получить комиссию |

### Заседания

| Метод | Endpoint | Auth | Описание |
|---|---|---|---|
| POST | `/api/meetings` | Да | Создать заседание |
| GET | `/api/meetings` | Нет | Список заседаний |
| GET | `/api/meetings/{id}` | Нет | Получить заседание |

### Посещаемость

| Метод | Endpoint | Auth | Описание |
|---|---|---|---|
| POST | `/api/meetings/{id}/attendance` | Да | Добавить посещаемость |
| GET | `/api/meetings/{id}/attendance` | Нет | Посещаемость заседания |

---

## Модель данных

В системе **6 таблиц**:

| Сущность | Поля |
|---|---|
| `User` | `id`, `username`, `password_hash`, `role` |
| `Deputy` | `id`, `full_name`, `party`, `district` |
| `Commission` | `id`, `name`, `description`, `chairman_id` |
| `DeputyCommission` | `deputy_id`, `commission_id` |
| `Meeting` | `id`, `commission_id`, `title`, `date`, `location` |
| `Attendance` | `id`, `meeting_id`, `deputy_id`, `status` |

**Связи:**

- `Commission.chairman_id` -> `Deputy.id`
- `Meeting.commission_id` -> `Commission.id`
- `Attendance.meeting_id` -> `Meeting.id`
- `Attendance.deputy_id` -> `Deputy.id`
- `DeputyCommission` - связь многие-ко-многим между `Deputy` и `Commission`

---

## Бизнес-правило

> **Один депутат не может иметь две записи посещаемости одного и того же заседания.**

Реализовано двумя способами:

1. **На уровне API** - перед созданием записи выполняется проверка.
При повторном добавлении возвращается **HTTP 400**
с сообщением: `"Для этого депутата уже есть запись посещаемости"`.
2. **На уровне БД** - ограничение `UNIQUE(meeting_id, deputy_id)`.

---

## Обработка ошибок

| Код | Значение |
|---|---|
| −200 | Успешная операция |
| −400 | Некорректная операция / дубликат |
| 401 | Отсутствует или недействительна авторизация |
| 404 | Объект не найден |

**Примеры:**

- `DELETE` несуществующего депутата -> **404**
- Защищённый endpoint без токена -> **401**
- Повторная посещаемость -> **400**

---

## Web-интерфейс

**Frontend доступен локально:** [http://127.0.0.1:5500](http://127.0.0.1:5500/)

Реализованные возможности:

- **Авторизация** - ввод логина и пароля, вход в систему
- **Депутаты** - просмотр списка, добавление, удаление
- **Комиссии** - просмотр, добавление, выбор председателя
- **Заседания** - просмотр, добавление, выбор комиссии
- **Посещаемость** - выбор заседания, просмотр, добавление депутата со статусом
(«присутствовал» / «отсутствовал»)

---

## Конфигурация

Все секреты вынесены в `.env`:

```
SECRET_KEY=<ваш-секретный-ключ>
DATABASE_URL=sqlite:///./duma.db
```

Приложение использует `python-dotenv`.
В репозитории хранится только `.env.example` с примером переменных.

### `.gitignore`

```
.venv/
.idea/
__pycache__/
*.pyc

backend/__pycache__/
backend/duma.db

.env
```

---

## Git-flow

**Основная ветка:** `main`

**Feature-ветки:**

| Ветка | Назначение | Коммит |
|---|---|---|
| `feature/1-delete-deputy` | Удаление депутата (Issue #1) | `b87b6b4`, `adc9536` |
| `feature/2-env-config` | Вынос конфигурации в `.env` | `af8fc20` |
| `feature/3-update-dependencies` | Актуализация зависимостей | `38cc94f` |

**Merge-коммит разрешения конфликта:** `c80a0b5 merge: resolve application title conflict`

**Релиз:** `v0.1.0` (annotated tag)

```
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

---

## Требования к окружению

### Серверная часть

- Процессор x64, ≥ 1 ГГц
- ОЗУ ≥ 2 ГБ
- ≥ 500 МБ свободного места на диске
- Python 3.13 или выше

### Клиентская часть

- Современный браузер (Chrome, Firefox, Edge и др.)
- ОЗУ ≥ 2 ГБ

---

## Документация

- [`ТЗ.docx`](https://./%D0%A2%D0%97.docx) — Техническое задание (ГОСТ 19.201-78, ГОСТ 34.602-89)
- [Swagger UI](http://127.0.0.1:8001/docs) — интерактивная документация API
- [ReDoc](http://127.0.0.1:8001/redoc) — альтернативная документация API

---

## Команда разработчиков

| Роль | ФИО |
|---|---|
| Руководитель разработки | Смирнова Ю. В. |
| Разработчик | Чуфаров С. Б. |
| Разработчик | Коротаев А. Г. |
| Разработчик | Ионин М. П. |

---

## Сроки

- **Начало работ:** 10.09.2026
- **Окончание работ:** 25.12.2026

---

## Лицензия

Проект выполнен в рамках учебной деятельности Московского политехнического
университета. Отдельное финансирование не предусмотрено.
Коммерческое использование не предполагается.

---

## Ссылки

- **GitHub-репозиторий:** [gorodskaya-duma241-351]([https://github.com/gorodskaya-duma241-351](https://github.com/1Lon1/gorodskaya-duma241-351/new/main?filename=README.md))
- **Issue #1:** «Добавить удаление депутата»
- **Релиз:** `v0.1.0`
