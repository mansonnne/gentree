# Database Physical Structure

Этот документ фиксирует реальную физическую структуру базы данных `gentree`, по которой должны проектироваться SQLAlchemy-модели, Alembic-миграции и backend-репозитории.

Документ отличается от текста ВКР:

- во ВКР перечисляются информационные объекты предметной области;
- здесь описывается фактическая реляционная схема PostgreSQL, включая таблицы связей `M:N`, историю статусов и служебные сущности, необходимые для корректной реализации.

## Принципы проектирования

- СУБД: `PostgreSQL 15`
- стиль ключей: UUID как первичные ключи для доменных таблиц
- нормализация: минимум 3НФ
- все связи `многие ко многим` реализуются через отдельные таблицы связей
- исторические данные выносятся в отдельные таблицы, а не хранятся в JSON внутри основной записи
- производные представления, такие как генеалогическое древо, не хранятся отдельной таблицей, если могут быть построены из базовых сущностей

## Логические группы таблиц

### 1. Идентификация и доступ

- `users`

### 2. Исследование и генеалогический профиль

- `profiles`
- `persons`
- `person_names`
- `relationships`
- `facts`

### 3. Архивная работа

- `archive_request_templates`
- `archive_requests`
- `archive_request_status_history`

### 4. Документы и привязки

- `documents`
- `person_documents`
- `fact_documents`
- `archive_request_documents`

### 5. Коммуникации и результаты

- `notification_templates`
- `notifications`
- `generated_books`

### 6. Аудит

- `audit_log`

## Полный перечень таблиц

### `users`

Основная таблица учётных записей субъектов системы.

Ключевые поля:

- `id`
- `email`
- `hashed_password`
- `role`
- `status`
- `first_name`
- `last_name`
- `middle_name`
- `last_login_at`
- `email_verified_at`
- `created_at`
- `updated_at`

Назначение:

- хранение пользователей всех ролей;
- аутентификация и авторизация;
- связь с профилями, запросами, фактами, документами, уведомлениями и аудитом.

### `profiles`

Основная таблица генеалогических профилей.

Ключевые поля:

- `id`
- `owner_user_id`
- `title`
- `description`
- `status`
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

Назначение:

- контейнер одного генеалогического исследования;
- точка агрегации персон, связей, фактов и архивных запросов.

### `persons`

Основная таблица персон внутри профиля.

Ключевые поля:

- `id`
- `profile_id`
- `sex`
- `birth_date`
- `death_date`
- `birth_place`
- `death_place`
- `notes`
- `is_living`
- `created_at`
- `updated_at`

Назначение:

- хранение родственников и иных персон исследования;
- участие в связях, фактах и привязках документов.

### `person_names`

Таблица вариантов имени персоны.

Ключевые поля:

- `id`
- `person_id`
- `family_name`
- `given_name`
- `patronymic`
- `name_type`
- `is_primary`
- `created_at`

Назначение:

- хранение основного имени;
- хранение имени при рождении;
- хранение альтернативных форм имени;
- устранение повторяющихся групп полей в `persons`.

### `relationships`

Таблица родственных связей между персонами.

Ключевые поля:

- `id`
- `profile_id`
- `source_person_id`
- `target_person_id`
- `relationship_type`
- `start_date`
- `end_date`
- `notes`
- `created_at`
- `updated_at`

Назначение:

- хранение структуры родства;
- построение генеалогического древа на уровне приложения.

Ограничения:

- запрет связи персоны самой с собой;
- обе персоны связи должны принадлежать одному профилю;
- защита от дублирующих связей одного типа.

### `facts`

Таблица генеалогических фактов.

Ключевые поля:

- `id`
- `person_id`
- `fact_type`
- `fact_date`
- `place`
- `value_text`
- `notes`
- `confidence`
- `verified_by_user_id`
- `verified_at`
- `created_at`
- `updated_at`

Назначение:

- хранение событий и характеристик, относящихся к персоне;
- хранение уровня достоверности факта;
- фиксация подтверждения со стороны генеалога или администратора.

### `archive_request_templates`

Таблица шаблонов архивных запросов.

Ключевые поля:

- `id`
- `name`
- `description`
- `version`
- `storage_path`
- `is_active`
- `created_by_user_id`
- `created_at`

Назначение:

- версионируемое хранение шаблонов запросов;
- централизованное управление актуальными шаблонами.

### `archive_requests`

Основная таблица архивных запросов.

Ключевые поля:

- `id`
- `profile_id`
- `created_by_user_id`
- `assigned_genealogist_user_id`
- `template_id`
- `title`
- `request_goal`
- `current_status`
- `requested_archive_name`
- `outgoing_number`
- `sent_at`
- `due_at`
- `completed_at`
- `created_at`
- `updated_at`

Назначение:

- хранение запроса как самостоятельной бизнес-сущности;
- привязка запроса к профилю, пользователю и генеалогу;
- хранение только текущего статуса, без истории.

### `archive_request_status_history`

Таблица истории смены статусов архивного запроса.

Ключевые поля:

- `id`
- `archive_request_id`
- `from_status`
- `to_status`
- `changed_by_user_id`
- `comment`
- `created_at`

Назначение:

- аудит жизненного цикла запроса;
- восстановление последовательности изменения статусов;
- поддержка пользовательского просмотра истории обработки.

### `documents`

Универсальная таблица документов.

Ключевые поля:

- `id`
- `uploaded_by_user_id`
- `document_kind`
- `source_type`
- `file_name`
- `mime_type`
- `file_size_bytes`
- `storage_path`
- `checksum_sha256`
- `original_created_at`
- `created_at`

Назначение:

- единая карточка файла вне зависимости от его бизнес-назначения;
- хранение только метаданных и ссылки на физическое хранилище.

Почему это отдельная сущность:

- один и тот же документ может участвовать в разных сценариях;
- документы не должны дублироваться по нескольким бизнес-таблицам.

### `person_documents`

Таблица связи `M:N` между персонами и документами.

Ключевые поля:

- `id`
- `person_id`
- `document_id`
- `relation_type`
- `created_at`

Назначение:

- связывать архивные документы и другие файлы с конкретными персонами;
- поддерживать случаи, когда один документ относится к нескольким персонам.

### `fact_documents`

Таблица связи `M:N` между фактами и документами.

Ключевые поля:

- `id`
- `fact_id`
- `document_id`
- `relation_type`
- `created_at`

Назначение:

- связывать подтверждающие документы с фактами;
- поддерживать случаи, когда один документ подтверждает несколько фактов.

### `archive_request_documents`

Таблица связи `M:N` между архивными запросами и документами.

Ключевые поля:

- `id`
- `archive_request_id`
- `document_id`
- `relation_type`
- `created_at`

Назначение:

- хранить все файлы, относящиеся к запросу;
- различать типы привязки: черновик, итоговый запрос, ответ архива, вложение, результат.

### `notification_templates`

Таблица шаблонов уведомлений.

Ключевые поля:

- `id`
- `notification_type`
- `channel`
- `subject_template`
- `body_template`
- `is_active`
- `created_by_user_id`
- `created_at`
- `updated_at`

Назначение:

- централизованное управление текстами уведомлений;
- поддержка редактирования уведомлений администратором.

### `notifications`

Таблица пользовательских уведомлений.

Ключевые поля:

- `id`
- `recipient_user_id`
- `template_id`
- `notification_type`
- `title`
- `body`
- `related_archive_request_id`
- `related_document_id`
- `read_at`
- `created_at`

Назначение:

- доставка и хранение системных сообщений;
- привязка уведомлений к запросам и документам.

### `generated_books`

Таблица операций формирования генеалогической книги.

Ключевые поля:

- `id`
- `profile_id`
- `requested_by_user_id`
- `document_id`
- `status`
- `started_at`
- `finished_at`
- `error_message`
- `created_at`

Назначение:

- хранение процесса генерации итогового документа;
- отделение процесса генерации от универсальной сущности `documents`.

### `audit_log`

Таблица журнала действий.

Ключевые поля:

- `id`
- `actor_type`
- `actor_user_id`
- `action_type`
- `entity_type`
- `entity_id`
- `payload_json`
- `created_at`

Назначение:

- аудит пользовательских и системных действий;
- восстановление истории операций;
- поддержка административного контроля.

## Что не является отдельной таблицей

### `genealogical_tree`

Генеалогическое древо не хранится отдельной таблицей.

Оно вычисляется из:

- `persons`
- `relationships`

Причина:

- древо является производным представлением, а не самостоятельной первичной сущностью хранения;
- отдельная таблица древа привела бы к дублированию данных и риску рассогласования.

## Основные связи между таблицами

### Один-ко-многим

- `users -> profiles`
- `profiles -> persons`
- `profiles -> relationships`
- `persons -> person_names`
- `persons -> facts`
- `profiles -> archive_requests`
- `archive_requests -> archive_request_status_history`
- `users -> notifications`
- `profiles -> generated_books`
- `users -> audit_log`

### Многие-ко-многим

- `persons <-> documents` через `person_documents`
- `facts <-> documents` через `fact_documents`
- `archive_requests <-> documents` через `archive_request_documents`

### Ссылки на управляющие сущности

- `archive_requests -> archive_request_templates`
- `notifications -> notification_templates`
- `facts -> users` как подтверждающий пользователь
- `generated_books -> documents` как итоговый файл

## Реальный MVP-срез БД

Для первой рабочей backend-версии достаточно следующих таблиц:

- `users`
- `profiles`
- `persons`
- `person_names`
- `relationships`
- `facts`
- `archive_request_templates`
- `archive_requests`
- `archive_request_status_history`
- `documents`
- `archive_request_documents`
- `notification_templates`
- `notifications`
- `audit_log`

Можно отложить на следующий этап:

- `person_documents`
- `fact_documents`
- `generated_books`

## Почему реальная схема больше, чем список сущностей в ВКР

Потому что информационные объекты предметной области и физические таблицы базы данных не обязаны совпадать один к одному.

Дополнительные таблицы нужны для:

- реализации связей `многие ко многим`;
- хранения истории изменений;
- поддержки шаблонов;
- отделения процессов от результатов;
- соблюдения требований нормализации.

Именно поэтому в реальной реализации количество таблиц будет больше, чем число информационных объектов из главы 2.2.

## Рекомендуемый следующий шаг

Эта структура должна стать основанием для:

1. SQLAlchemy 2.0 моделей.
2. Enum-ов PostgreSQL.
3. Первой полноценной Alembic-миграции.
4. Дальнейшей реализации модулей `auth`, `profiles`, `persons`, `archive_requests`.

