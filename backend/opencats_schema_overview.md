# 📊 OpenCats Database Schema Overview

This document provides a clean overview of the **opencats** database structure, including column definitions and truncated sample data for readability.

**Generated at:** 2026-03-23
**Total Tables:** 54

## 📑 Quick Navigation
- [access_level](#table-access-level)
- [activity](#table-activity)
- [activity_type](#table-activity-type)
- [attachment](#table-attachment)
- [calendar_event](#table-calendar-event)
- [calendar_event_type](#table-calendar-event-type)
- [candidate](#table-candidate)
- [candidate_joborder](#table-candidate-joborder)
- [candidate_joborder_status](#table-candidate-joborder-status)
- [candidate_joborder_status_history](#table-candidate-joborder-status-history)
- [candidate_jobordrer_status_type](#table-candidate-jobordrer-status-type)
- [candidate_source](#table-candidate-source)
- [candidate_tag](#table-candidate-tag)
- [career_portal_questionnaire](#table-career-portal-questionnaire)
- [career_portal_questionnaire_answer](#table-career-portal-questionnaire-answer)
- [career_portal_questionnaire_history](#table-career-portal-questionnaire-history)
- [career_portal_questionnaire_question](#table-career-portal-questionnaire-question)
- [career_portal_template](#table-career-portal-template)
- [career_portal_template_site](#table-career-portal-template-site)
- [company](#table-company)
- [company_department](#table-company-department)
- [contact](#table-contact)
- [data_item_type](#table-data-item-type)
- [eeo_ethnic_type](#table-eeo-ethnic-type)
- [eeo_veteran_type](#table-eeo-veteran-type)
- [email_history](#table-email-history)
- [email_template](#table-email-template)
- [extension_statistics](#table-extension-statistics)
- [extra_field](#table-extra-field)
- [extra_field_settings](#table-extra-field-settings)
- [feedback](#table-feedback)
- [history](#table-history)
- [http_log](#table-http-log)
- [http_log_types](#table-http-log-types)
- [import](#table-import)
- [installtest](#table-installtest)
- [joborder](#table-joborder)
- [module_schema](#table-module-schema)
- [mru](#table-mru)
- [queue](#table-queue)
- [saved_list](#table-saved-list)
- [saved_list_entry](#table-saved-list-entry)
- [saved_search](#table-saved-search)
- [settings](#table-settings)
- [site](#table-site)
- [sph_counter](#table-sph-counter)
- [system](#table-system)
- [tag](#table-tag)
- [user](#table-user)
- [user_login](#table-user-login)
- [word_verification](#table-word-verification)
- [xml_feed_submits](#table-xml-feed-submits)
- [xml_feeds](#table-xml-feeds)
- [zipcodes](#table-zipcodes)

---

## <a name="table-access-level"></a> 📁 Table: `access_level`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **access_level_id** | `int(11)` | NO | PRI | 0 |
| **short_description** | `varchar(32)` | NO | MUL |  |
| **long_description** | `text` | NO | - | NULL |

### 🔍 Sample Data (Top 3)
|   access_level_id | short_description   | long_description                                                                 |
|------------------:|:--------------------|:---------------------------------------------------------------------------------|
|                 0 | Account Disabled    | Disabled - The lowest access level. User cannot log in.                          |
|               100 | Read Only           | Read Only - A standard user that can view data on the system in a read-only m... |
|               200 | Add / Edit          | Edit - All lower access, plus the ability to edit information on the system.     |

---

## <a name="table-activity"></a> 📁 Table: `activity`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **activity_id** | `int(11)` | NO | PRI | NULL |
| **data_item_id** | `int(11)` | NO | - | 0 |
| **data_item_type** | `int(11)` | NO | MUL | 0 |
| **joborder_id** | `int(11)` | YES | MUL | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **entered_by** | `int(11)` | NO | MUL | 0 |
| **date_created** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **type** | `int(11)` | NO | MUL | 0 |
| **notes** | `text` | YES | - | NULL |
| **date_modified** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |

### 🔍 Sample Data (Top 3)
|   activity_id |   data_item_id |   data_item_type |   joborder_id |   site_id |   entered_by | date_created        |   type | notes                        | date_modified       |
|--------------:|---------------:|-----------------:|--------------:|----------:|-------------:|:--------------------|-------:|:-----------------------------|:--------------------|
|             1 |              5 |              100 |             1 |         1 |            1 | 2023-12-11 01:41:35 |    400 | Added candidate to pipeline. | 2023-12-11 01:41:35 |
|             2 |              7 |              100 |             2 |         1 |            1 | 2023-12-11 07:11:35 |    400 | Added candidate to pipeline. | 2023-12-11 07:11:35 |
|            11 |             13 |              100 |            13 |         1 |         1257 | 2023-12-18 09:45:17 |    400 | Added candidate to pipeline. | 2023-12-18 09:45:17 |

---

## <a name="table-activity-type"></a> 📁 Table: `activity_type`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **activity_type_id** | `int(11)` | NO | PRI | 0 |
| **short_description** | `varchar(32)` | NO | MUL |  |

### 🔍 Sample Data (Top 3)
|   activity_type_id | short_description   |
|-------------------:|:--------------------|
|                100 | Call                |
|                200 | Email               |
|                300 | Meeting             |

---

## <a name="table-attachment"></a> 📁 Table: `attachment`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **attachment_id** | `int(11)` | NO | PRI | NULL |
| **data_item_id** | `int(11)` | NO | MUL | 0 |
| **data_item_type** | `int(11)` | NO | MUL | 0 |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **title** | `varchar(128)` | YES | - | NULL |
| **original_filename** | `varchar(255)` | NO | - |  |
| **stored_filename** | `varchar(255)` | NO | - |  |
| **content_type** | `varchar(255)` | YES | - | NULL |
| **resume** | `int(1)` | NO | - | 0 |
| **text** | `text` | YES | - | NULL |
| **date_created** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **profile_image** | `int(1)` | YES | - | 0 |
| **directory_name** | `varchar(64)` | YES | - | NULL |
| **md5_sum** | `varchar(40)` | NO | MUL |  |
| **file_size_kb** | `int(11)` | YES | - | 0 |
| **md5_sum_text** | `varchar(40)` | NO | - |  |

### 🔍 Sample Data (Top 3)
|   attachment_id |   data_item_id |   data_item_type |   site_id | title                  | original_filename           | stored_filename             | content_type   |   resume | text                                                                             | date_created        | date_modified       |   profile_image | directory_name                                  | md5_sum                          |   file_size_kb | md5_sum_text                     |
|----------------:|---------------:|-----------------:|----------:|:-----------------------|:----------------------------|:----------------------------|:---------------|---------:|:---------------------------------------------------------------------------------|:--------------------|:--------------------|----------------:|:------------------------------------------------|:---------------------------------|---------------:|:---------------------------------|
|               1 |             -1 |              200 |       180 | catsbackup             | catsbackup.bak              | catsbackup.bak              | catsbackup     |        0 | nan                                                                              | 2023-12-06 23:59:27 | 2023-12-06 23:59:27 |               0 | site_180/0xxx/c89aca92227435e143e0e080beef0f34/ | 8253e61eba5e7854c7b23810679734e9 |             22 |                                  |
|              12 |             14 |              100 |         1 | Sindhu Resume          | Sindhu Resume.docx          | Sindhu Resume.docx          |                |        1 | Sindhusri A (434) 321-1206 asindhusri8_rATrgmail_rDOTrcom  Professional Summa... | 2023-12-14 09:30:45 | 2023-12-14 09:30:45 |               0 | site_1/0xxx/7fcb41612a613f631a14fb7e62d57331/   | b643671ca14cbcd0640e22963b11e635 |             27 | 44f91ce014ef1a9769b7da814eda9c2f |
|               4 |              6 |              100 |         1 | Valentina Peter Resume | Valentina Peter Resume.docx | Valentina Peter Resume.docx |                |        1 | VALENTINA PETER â tinapeter2020_rATrgmail_rDOTrcom  |       â _rPLUSr1 90... | 2023-12-11 06:32:27 | 2023-12-11 06:32:27 |               0 | site_1/0xxx/ffd3b477e40e2dc2b1bad36405582b33/   | 3ef2a7b93751219267c2ace51b629d15 |             35 | 82d596149b520f7b18c8188d9ef347a1 |

---

## <a name="table-calendar-event"></a> 📁 Table: `calendar_event`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **calendar_event_id** | `int(11)` | NO | PRI | NULL |
| **type** | `int(11)` | NO | - | 0 |
| **date** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **title** | `text` | NO | - | NULL |
| **all_day** | `int(1)` | NO | - | 0 |
| **data_item_id** | `int(11)` | NO | - | -1 |
| **data_item_type** | `int(11)` | NO | - | -1 |
| **entered_by** | `int(11)` | NO | - | 0 |
| **date_created** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **joborder_id** | `int(11)` | NO | - | -1 |
| **description** | `text` | YES | - | NULL |
| **duration** | `int(11)` | NO | - | 60 |
| **reminder_enabled** | `int(1)` | NO | - | 0 |
| **reminder_email** | `text` | YES | - | NULL |
| **reminder_time** | `int(11)` | YES | - | 0 |
| **public** | `int(1)` | NO | - | 1 |

### 🔍 Sample Data (Top 3)
|   calendar_event_id |   type | date                | title          |   all_day |   data_item_id |   data_item_type |   entered_by | date_created        | date_modified       |   site_id |   joborder_id | description                                                           |   duration |   reminder_enabled | reminder_email                |   reminder_time |   public |
|--------------------:|-------:|:--------------------|:---------------|----------:|---------------:|-----------------:|-------------:|:--------------------|:--------------------|----------:|--------------:|:----------------------------------------------------------------------|-----------:|-------------------:|:------------------------------|----------------:|---------:|
|                   1 |    400 | 2023-12-19 19:30:00 | Data Architect |         0 |             13 |              100 |         1254 | 2023-12-18 09:50:37 | 2023-12-18 09:50:37 |         1 |            13 | Client: ST of Hope  1st round of interview.                           |         45 |                  0 | nikhil.j@paradigminfotech.com |              15 |        0 |
|                   2 |    400 | 2023-12-19 19:30:00 | Data Architect |         0 |             13 |              100 |         1254 | 2023-12-18 09:50:37 | 2023-12-18 09:50:37 |         1 |            13 | Client: ST of Hope  1st round of interview.                           |         45 |                  0 | nikhil.j@paradigminfotech.com |              15 |        0 |
|                   3 |    400 | 2023-12-21 00:30:00 | Oracle DBA     |         0 |             52 |              100 |         1255 | 2023-12-20 07:52:39 | 2023-12-20 07:52:39 |         1 |            -1 | Having first round interview with Hexaware- 20.12.2023 at 2.30 PM EST |         45 |                  0 | sekhar.m@paradigminfotech.com |              15 |        0 |

---

## <a name="table-calendar-event-type"></a> 📁 Table: `calendar_event_type`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **calendar_event_type_id** | `int(11)` | NO | PRI | 0 |
| **short_description** | `varchar(32)` | NO | MUL |  |
| **icon_image** | `varchar(128)` | NO | - |  |

### 🔍 Sample Data (Top 3)
|   calendar_event_type_id | short_description   | icon_image         |
|-------------------------:|:--------------------|:-------------------|
|                      100 | Call                | images/phone.gif   |
|                      200 | Email               | images/email.gif   |
|                      300 | Meeting             | images/meeting.gif |

---

## <a name="table-candidate"></a> 📁 Table: `candidate`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **candidate_id** | `int(11)` | NO | PRI | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **last_name** | `varchar(64)` | NO | MUL |  |
| **first_name** | `varchar(64)` | NO | MUL |  |
| **middle_name** | `varchar(32)` | YES | - | NULL |
| **phone_home** | `varchar(40)` | YES | MUL | NULL |
| **phone_cell** | `varchar(40)` | YES | MUL | NULL |
| **phone_work** | `varchar(40)` | YES | MUL | NULL |
| **address** | `text` | YES | - | NULL |
| **city** | `varchar(64)` | YES | - | NULL |
| **state** | `varchar(64)` | YES | - | NULL |
| **zip** | `varchar(16)` | YES | - | NULL |
| **source** | `varchar(128)` | YES | - | NULL |
| **date_available** | `datetime` | YES | - | NULL |
| **can_relocate** | `int(1)` | NO | - | 0 |
| **notes** | `text` | YES | - | NULL |
| **key_skills** | `text` | YES | MUL | NULL |
| **current_employer** | `varchar(128)` | YES | - | NULL |
| **entered_by** | `int(11)` | NO | MUL | 0 |
| **owner** | `int(11)` | YES | MUL | NULL |
| **date_created** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **email1** | `varchar(128)` | YES | - | NULL |
| **email2** | `varchar(128)` | YES | - | NULL |
| **web_site** | `varchar(128)` | YES | - | NULL |
| **import_id** | `int(11)` | NO | - | 0 |
| **is_hot** | `int(1)` | NO | - | 0 |
| **eeo_ethnic_type_id** | `int(11)` | YES | - | 0 |
| **eeo_veteran_type_id** | `int(11)` | YES | - | 0 |
| **eeo_disability_status** | `varchar(5)` | YES | - |  |
| **eeo_gender** | `varchar(5)` | YES | - |  |
| **desired_pay** | `varchar(64)` | YES | - | NULL |
| **current_pay** | `varchar(64)` | YES | - | NULL |
| **is_active** | `int(1)` | YES | - | 1 |
| **is_admin_hidden** | `int(1)` | YES | - | 0 |
| **best_time_to_call** | `varchar(255)` | NO | - |  |

### 🔍 Sample Data (Top 3)
|   candidate_id |   site_id | last_name   | first_name   | middle_name   | phone_home   | phone_cell   | phone_work   | address        | city       | state      |   zip | source   | date_available   |   can_relocate | notes                                                                            | key_skills                                                     | current_employer   |   entered_by |   owner | date_created        | date_modified       | email1                   | email2   | web_site   |   import_id |   is_hot |   eeo_ethnic_type_id |   eeo_veteran_type_id | eeo_disability_status   | eeo_gender   | desired_pay   | current_pay   |   is_active |   is_admin_hidden | best_time_to_call   |
|---------------:|----------:|:------------|:-------------|:--------------|:-------------|:-------------|:-------------|:---------------|:-----------|:-----------|------:|:---------|:-----------------|---------------:|:---------------------------------------------------------------------------------|:---------------------------------------------------------------|:-------------------|-------------:|--------:|:--------------------|:--------------------|:-------------------------|:---------|:-----------|------------:|---------:|---------------------:|----------------------:|:------------------------|:-------------|:--------------|:--------------|------------:|------------------:|:--------------------|
|             15 |         1 | burri       | Rohith reddy |               |              | 251-616-2288 |              |                | Saint paul | MN         | 55101 | (none)   | NULL             |              0 | Candidate Legal Name: Rohith reddy burri  E-mail: rohithreddyb09@gmail.com  P... | .NET Core/(ASP.NET) , JavaScript API, Oracle , Azure, Agile    |                    |         1254 |    1254 | 2023-12-14 13:50:05 | 2023-12-14 14:07:09 | rohithreddyb09@gmail.com |          |            |           0 |        0 |                    0 |                     0 |                         |              |               |               |           1 |                 0 |                     |
|              6 |         1 | PETER       | VALENTINA    |               |              | 908-656-7866 |              |                |            | New Jersey |       | Hotlist  | NULL             |              1 | H1 Transfer  2-3 weeks notice  Relocation Ok Prefers around NJ area  Market a... | Product Owner                                                  |                    |            1 |       1 | 2023-12-11 06:32:27 | 2023-12-14 06:55:50 | tinapeter2020@gmail.com  |          |            |           0 |        1 |                    0 |                     0 |                         |              |               |               |           1 |                 0 |                     |
|             14 |         1 | Thadishetti | Sindhusri    |               |              | 434-321-1206 |              | Lewisville, TX | Lewisville | TX         | 75067 | Hotlist  | NULL             |              1 |                                                                                  | Java, J2EE, JSP, Servlets, Spring Boot, Hibernate, Nodejs, XML |                    |         1258 |    1258 | 2023-12-14 09:30:45 | 2023-12-14 09:31:04 | asindhusri8@gmail.com    |          |            |           0 |        1 |                    0 |                     0 |                         |              |               | $55           |           1 |                 0 | Any time            |

---

## <a name="table-candidate-joborder"></a> 📁 Table: `candidate_joborder`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **candidate_joborder_id** | `int(11)` | NO | PRI | NULL |
| **candidate_id** | `int(11)` | NO | MUL | 0 |
| **joborder_id** | `int(11)` | NO | MUL | 0 |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **status** | `int(11)` | NO | - | 0 |
| **date_submitted** | `datetime` | YES | MUL | NULL |
| **date_created** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **rating_value** | `int(5)` | YES | - | NULL |
| **added_by** | `int(11)` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   candidate_joborder_id |   candidate_id |   joborder_id |   site_id |   status | date_submitted   | date_created        | date_modified       |   rating_value |   added_by |
|------------------------:|---------------:|--------------:|----------:|---------:|:-----------------|:--------------------|:--------------------|---------------:|-----------:|
|                       5 |             13 |            13 |         1 |      500 | NULL             | 2023-12-18 09:45:17 | 2023-12-18 09:50:35 |              5 |       1257 |
|                       6 |            734 |            41 |         1 |      400 | NULL             | 2024-01-29 05:50:46 | 2024-01-29 05:51:23 |            nan |       1253 |
|                       3 |              6 |             2 |         1 |      650 | NULL             | 2023-12-11 07:13:21 | 2023-12-11 07:23:25 |            nan |          1 |

---

## <a name="table-candidate-joborder-status"></a> 📁 Table: `candidate_joborder_status`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **candidate_joborder_status_id** | `int(11)` | NO | PRI | 0 |
| **short_description** | `varchar(32)` | NO | MUL |  |
| **can_be_scheduled** | `int(1)` | NO | - | 0 |
| **triggers_email** | `int(1)` | NO | - | 1 |
| **is_enabled** | `int(1)` | NO | - | 1 |

### 🔍 Sample Data (Top 3)
|   candidate_joborder_status_id | short_description   |   can_be_scheduled |   triggers_email |   is_enabled |
|-------------------------------:|:--------------------|-------------------:|-----------------:|-------------:|
|                            100 | No Contact          |                  0 |                0 |            1 |
|                            200 | Contacted           |                  0 |                0 |            1 |
|                            300 | Qualifying          |                  0 |                1 |            1 |

---

## <a name="table-candidate-joborder-status-history"></a> 📁 Table: `candidate_joborder_status_history`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **candidate_joborder_status_history_id** | `int(11)` | NO | PRI | NULL |
| **candidate_id** | `int(11)` | NO | MUL | 0 |
| **joborder_id** | `int(11)` | NO | MUL | 0 |
| **date** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **status_from** | `int(11)` | NO | - | 0 |
| **status_to** | `int(11)` | NO | MUL | 0 |
| **site_id** | `int(11)` | NO | MUL | 0 |

### 🔍 Sample Data (Top 3)
|   candidate_joborder_status_history_id |   candidate_id |   joborder_id | date                |   status_from |   status_to |   site_id |
|---------------------------------------:|---------------:|--------------:|:--------------------|--------------:|------------:|----------:|
|                                      1 |              6 |             2 | 2023-12-11 07:18:46 |           100 |         250 |         1 |
|                                      2 |              6 |             2 | 2023-12-11 07:23:25 |           250 |         650 |         1 |
|                                      7 |            734 |            41 | 2024-01-29 05:51:23 |           100 |         400 |         1 |

---

## <a name="table-candidate-jobordrer-status-type"></a> 📁 Table: `candidate_jobordrer_status_type`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **candidate_status_type_id** | `int(11)` | NO | PRI | 0 |
| **short_description** | `varchar(32)` | NO | MUL |  |
| **can_be_scheduled** | `int(1)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-candidate-source"></a> 📁 Table: `candidate_source`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **source_id** | `int(11)` | NO | PRI | NULL |
| **name** | `varchar(255)` | YES | - | NULL |
| **site_id** | `int(11)` | YES | MUL | NULL |
| **date_created** | `datetime` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   source_id | name    |   site_id | date_created        |
|------------:|:--------|----------:|:--------------------|
|           1 | Hotlist |         1 | 2023-12-11 07:59:24 |
|           2 | Dice    |         1 | 2023-12-14 14:00:44 |

---

## <a name="table-candidate-tag"></a> 📁 Table: `candidate_tag`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `int(10) unsigned` | NO | PRI | NULL |
| **site_id** | `int(10) unsigned` | YES | - | NULL |
| **candidate_id** | `int(10) unsigned` | NO | - | NULL |
| **tag_id** | `int(10) unsigned` | NO | - | NULL |

### 🔍 Sample Data (Top 3)
|   id |   site_id |   candidate_id |   tag_id |
|-----:|----------:|---------------:|---------:|
|   55 |         1 |              1 |        5 |
|   56 |         1 |              1 |       78 |
|   57 |         1 |              1 |       80 |

---

## <a name="table-career-portal-questionnaire"></a> 📁 Table: `career_portal_questionnaire`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **career_portal_questionnaire_id** | `int(11)` | NO | PRI | NULL |
| **title** | `varchar(255)` | NO | - |  |
| **site_id** | `int(11)` | NO | - | 0 |
| **description** | `varchar(255)` | YES | - | NULL |
| **is_active** | `tinyint(1)` | NO | - | 1 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-career-portal-questionnaire-answer"></a> 📁 Table: `career_portal_questionnaire_answer`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **career_portal_questionnaire_answer_id** | `int(11)` | NO | PRI | NULL |
| **career_portal_questionnaire_question_id** | `int(11)` | NO | - | NULL |
| **career_portal_questionnaire_id** | `int(11)` | NO | - | NULL |
| **text** | `varchar(255)` | NO | - |  |
| **action_source** | `varchar(128)` | YES | - | NULL |
| **action_notes** | `text` | YES | - | NULL |
| **action_is_hot** | `tinyint(1)` | YES | - | 0 |
| **action_is_active** | `tinyint(1)` | YES | - | 0 |
| **action_can_relocate** | `tinyint(1)` | YES | - | 0 |
| **action_key_skills** | `varchar(255)` | YES | - | NULL |
| **position** | `int(4)` | NO | - | 0 |
| **site_id** | `int(11)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-career-portal-questionnaire-history"></a> 📁 Table: `career_portal_questionnaire_history`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **career_portal_questionnaire_history_id** | `int(11)` | NO | PRI | NULL |
| **site_id** | `int(11)` | NO | - | 0 |
| **candidate_id** | `int(11)` | NO | - | 0 |
| **question** | `varchar(255)` | NO | - |  |
| **answer** | `varchar(255)` | NO | - |  |
| **questionnaire_title** | `varchar(255)` | NO | - |  |
| **questionnaire_description** | `varchar(255)` | NO | - |  |
| **date** | `datetime` | NO | - | 1000-01-01 00:00:00 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-career-portal-questionnaire-question"></a> 📁 Table: `career_portal_questionnaire_question`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **career_portal_questionnaire_question_id** | `int(11)` | NO | PRI | NULL |
| **career_portal_questionnaire_id** | `int(11)` | NO | - | NULL |
| **text** | `varchar(255)` | NO | - |  |
| **minimum_length** | `int(11)` | YES | - | NULL |
| **maximum_length** | `int(11)` | YES | - | NULL |
| **required** | `tinyint(1)` | NO | - | 0 |
| **position** | `int(4)` | NO | - | 0 |
| **site_id** | `int(11)` | NO | - | 0 |
| **type** | `int(11)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-career-portal-template"></a> 📁 Table: `career_portal_template`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **career_portal_template_id** | `int(11)` | NO | PRI | NULL |
| **career_portal_name** | `varchar(255)` | YES | - | NULL |
| **setting** | `varchar(128)` | NO | - |  |
| **value** | `text` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   career_portal_template_id | career_portal_name   | setting   | value   |
|----------------------------:|:---------------------|:----------|:--------|
|                          56 | Blank Page           | Left      |         |
|                          57 | Blank Page           | Footer    |         |
|                          58 | Blank Page           | Header    |         |

---

## <a name="table-career-portal-template-site"></a> 📁 Table: `career_portal_template_site`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **career_portal_template_id** | `int(11)` | NO | PRI | NULL |
| **career_portal_name** | `varchar(255)` | YES | - | NULL |
| **site_id** | `int(11)` | NO | - | NULL |
| **setting** | `varchar(128)` | NO | - |  |
| **value** | `text` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-company"></a> 📁 Table: `company`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **company_id** | `int(11)` | NO | PRI | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **billing_contact** | `int(11)` | YES | - | NULL |
| **name** | `varchar(64)` | NO | MUL |  |
| **address** | `text` | YES | - | NULL |
| **city** | `varchar(64)` | YES | - | NULL |
| **state** | `varchar(64)` | YES | - | NULL |
| **zip** | `varchar(16)` | YES | - | NULL |
| **phone1** | `varchar(40)` | YES | - | NULL |
| **phone2** | `varchar(40)` | YES | - | NULL |
| **url** | `varchar(128)` | YES | - | NULL |
| **key_technologies** | `text` | YES | MUL | NULL |
| **notes** | `text` | YES | - | NULL |
| **entered_by** | `int(11)` | YES | MUL | NULL |
| **owner** | `int(11)` | YES | MUL | NULL |
| **date_created** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **is_hot** | `int(1)` | YES | MUL | NULL |
| **fax_number** | `varchar(40)` | YES | - | NULL |
| **import_id** | `int(11)` | YES | - | NULL |
| **default_company** | `int(1)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
|   company_id |   site_id | billing_contact   | name                 | address                                                                          | city           | state   |   zip | phone1       | phone2   | url                         | key_technologies                                        | notes                                                                            |   entered_by |   owner | date_created        | date_modified       |   is_hot | fax_number   | import_id   |   default_company |
|-------------:|----------:|:------------------|:---------------------|:---------------------------------------------------------------------------------|:---------------|:--------|------:|:-------------|:---------|:----------------------------|:--------------------------------------------------------|:---------------------------------------------------------------------------------|-------------:|--------:|:--------------------|:--------------------|---------:|:-------------|:------------|------------------:|
|            1 |         1 | NULL              | Internal Postings    |                                                                                  |                |         |       |              |          |                             |                                                         |                                                                                  |            0 |       0 | 2009-11-19 10:00:20 | 2009-11-19 10:00:20 |        0 |              | NULL        |                 1 |
|           12 |         1 | NULL              | Vaspire Technologies | 180 Tices Lane,  Suite 205, Building A,  East Brunswick, NJ 08816  Phone no 7... | East Brunswick | NJ      | 08816 | 732-746-5090 |          | http://www.vaspiretech.com/ | Data Architect                                          | Profile Sybmitte to the client Baskara Sethupathy Billing rate $80/hr  for th... |         1257 |    1257 | 2023-12-14 07:40:24 | 2023-12-14 07:40:24 |        1 |              | NULL        |                 0 |
|            5 |         1 | NULL              | Wabtec               |                                                                                  | Erie           | PA      |       |              |          | http://www.wabtec.com/      | PM, Data Analyst, IT analyst, Mulesoft, AWS, Sharepoint |                                                                                  |            1 |       1 | 2023-12-11 06:27:07 | 2023-12-11 06:27:07 |        1 |              | NULL        |                 0 |

---

## <a name="table-company-department"></a> 📁 Table: `company_department`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **company_department_id** | `int(11)` | NO | PRI | NULL |
| **name** | `varchar(128)` | YES | - | NULL |
| **company_id** | `int(11)` | NO | - | NULL |
| **site_id** | `int(11)` | NO | - | 0 |
| **date_created** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **created_by** | `int(11)` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   company_department_id | name            |   company_id |   site_id | date_created        | created_by   |
|------------------------:|:----------------|-------------:|----------:|:--------------------|:-------------|
|                       1 | Human Resources |            4 |         1 | 2023-12-11 01:40:23 | NULL         |

---

## <a name="table-contact"></a> 📁 Table: `contact`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **contact_id** | `int(11)` | NO | PRI | NULL |
| **company_id** | `int(11)` | NO | MUL | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **last_name** | `varchar(64)` | NO | MUL |  |
| **first_name** | `varchar(64)` | NO | MUL |  |
| **title** | `varchar(128)` | YES | MUL | NULL |
| **email1** | `varchar(128)` | YES | - | NULL |
| **email2** | `varchar(128)` | YES | - | NULL |
| **phone_work** | `varchar(40)` | YES | - | NULL |
| **phone_cell** | `varchar(40)` | YES | - | NULL |
| **phone_other** | `varchar(40)` | YES | - | NULL |
| **address** | `text` | YES | - | NULL |
| **city** | `varchar(64)` | YES | - | NULL |
| **state** | `varchar(64)` | YES | - | NULL |
| **zip** | `varchar(16)` | YES | - | NULL |
| **is_hot** | `int(1)` | YES | - | NULL |
| **notes** | `text` | YES | - | NULL |
| **entered_by** | `int(11)` | NO | - | 0 |
| **owner** | `int(11)` | YES | MUL | NULL |
| **date_created** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **left_company** | `int(1)` | NO | - | 0 |
| **import_id** | `int(11)` | NO | - | 0 |
| **company_department_id** | `int(11)` | NO | - | NULL |
| **reports_to** | `int(11)` | YES | - | -1 |

### 🔍 Sample Data (Top 3)
|   contact_id |   company_id |   site_id | last_name   | first_name   | title       | email1   | email2   | phone_work   | phone_cell   | phone_other   | address   | city   | state   | zip   |   is_hot | notes   |   entered_by |   owner | date_created        | date_modified       |   left_company |   import_id |   company_department_id |   reports_to |
|-------------:|-------------:|----------:|:------------|:-------------|:------------|:---------|:---------|:-------------|:-------------|:--------------|:----------|:-------|:--------|:------|---------:|:--------|-------------:|--------:|:--------------------|:--------------------|---------------:|------------:|------------------------:|-------------:|
|            1 |            1 |         1 | P           | Ramakanth    | Sr.Recruter |          |          |              |              |               |           |        |         |       |        0 |         |            1 |       1 | 2023-12-08 07:18:03 | 2023-12-08 07:18:03 |              0 |           0 |                       0 |           -1 |

---

## <a name="table-data-item-type"></a> 📁 Table: `data_item_type`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **data_item_type_id** | `int(11)` | NO | PRI | 0 |
| **short_description** | `varchar(32)` | NO | MUL |  |

### 🔍 Sample Data (Top 3)
|   data_item_type_id | short_description   |
|--------------------:|:--------------------|
|                 100 | Candidate           |
|                 200 | Company             |
|                 300 | Contact             |

---

## <a name="table-eeo-ethnic-type"></a> 📁 Table: `eeo_ethnic_type`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **eeo_ethnic_type_id** | `int(11)` | NO | PRI | NULL |
| **type** | `varchar(128)` | NO | - |  |

### 🔍 Sample Data (Top 3)
|   eeo_ethnic_type_id | type                      |
|---------------------:|:--------------------------|
|                    1 | American Indian           |
|                    2 | Asian or Pacific Islander |
|                    3 | Hispanic or Latino        |

---

## <a name="table-eeo-veteran-type"></a> 📁 Table: `eeo_veteran_type`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **eeo_veteran_type_id** | `int(11)` | NO | PRI | NULL |
| **type** | `varchar(128)` | NO | - |  |

### 🔍 Sample Data (Top 3)
|   eeo_veteran_type_id | type              |
|----------------------:|:------------------|
|                     1 | No Veteran Status |
|                     2 | Eligible Veteran  |
|                     3 | Disabled Veteran  |

---

## <a name="table-email-history"></a> 📁 Table: `email_history`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **email_history_id** | `int(11)` | NO | PRI | NULL |
| **from_address** | `varchar(128)` | NO | - |  |
| **recipients** | `text` | NO | - | NULL |
| **text** | `text` | YES | - | NULL |
| **user_id** | `int(11)` | YES | MUL | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **date** | `datetime` | YES | MUL | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-email-template"></a> 📁 Table: `email_template`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **email_template_id** | `int(11)` | NO | PRI | NULL |
| **text** | `text` | YES | - | NULL |
| **allow_substitution** | `int(1)` | NO | - | 0 |
| **site_id** | `int(11)` | NO | - | 0 |
| **tag** | `varchar(255)` | YES | - | NULL |
| **title** | `varchar(255)` | YES | - | NULL |
| **possible_variables** | `text` | YES | - | NULL |
| **disabled** | `int(1)` | YES | - | 0 |

### 🔍 Sample Data (Top 3)
|   email_template_id | text                                                                             |   allow_substitution |   site_id | tag                                     | title                                           | possible_variables                                                               |   disabled |
|--------------------:|:---------------------------------------------------------------------------------|---------------------:|----------:|:----------------------------------------|:------------------------------------------------|:---------------------------------------------------------------------------------|-----------:|
|                  20 | * Auto generated message. Please DO NOT reply *  %DATETIME%    Dear %CANDFULL... |                    1 |         1 | EMAIL_TEMPLATE_STATUSCHANGE             | Status Changed (Sent to Candidate)              | %CANDSTATUS%%CANDOWNER%%CANDFIRSTNAME%%CANDFULLNAME%%CANDPREVSTATUS%%JBODCLIE... |          0 |
|                  28 | %DATETIME%    Dear %CANDOWNER%,    This E-Mail is a notification that a Candi... |                    1 |         1 | EMAIL_TEMPLATE_OWNERSHIPASSIGNCANDIDATE | Candidate Assigned (Sent to Assigned Recruiter) | %CANDOWNER%%CANDFIRSTNAME%%CANDFULLNAME%%CANDCATSURL%                            |          0 |
|                  27 | %DATETIME%    Dear %JBODOWNER%,    This E-Mail is a notification that a Job O... |                    1 |         1 | EMAIL_TEMPLATE_OWNERSHIPASSIGNJOBORDER  | Job Order Assigned (Sent to Assigned Recruiter) | %JBODOWNER%%JBODTITLE%%JBODCLIENT%%JBODCATSURL%%JBODID%                          |          0 |

---

## <a name="table-extension-statistics"></a> 📁 Table: `extension_statistics`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **extension_statistics_id** | `int(11)` | NO | PRI | NULL |
| **extension** | `varchar(128)` | NO | - |  |
| **action** | `varchar(128)` | NO | - |  |
| **user** | `varchar(128)` | NO | - |  |
| **date** | `date` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-extra-field"></a> 📁 Table: `extra_field`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **extra_field_id** | `int(11)` | NO | PRI | NULL |
| **data_item_id** | `int(11)` | YES | MUL | 0 |
| **field_name** | `varchar(255)` | YES | - | NULL |
| **value** | `text` | YES | - | NULL |
| **import_id** | `int(11)` | YES | - | NULL |
| **site_id** | `int(11)` | YES | MUL | 0 |
| **data_item_type** | `int(11)` | YES | - | 0 |

### 🔍 Sample Data (Top 3)
|   extra_field_id |   data_item_id | field_name   | value         |   import_id |   site_id |   data_item_type |
|-----------------:|---------------:|:-------------|:--------------|------------:|----------:|-----------------:|
|                1 |              7 | Vendor       | Shiva         |           0 |         1 |              400 |
|                2 |              8 | Vendor       | Vishal        |           0 |         1 |              400 |
|                3 |             11 | Vendor       | Krishna Kumar |           0 |         1 |              400 |

---

## <a name="table-extra-field-settings"></a> 📁 Table: `extra_field_settings`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **extra_field_settings_id** | `int(11)` | NO | PRI | NULL |
| **field_name** | `varchar(255)` | YES | - | NULL |
| **import_id** | `int(11)` | YES | - | NULL |
| **site_id** | `int(11)` | NO | - | 0 |
| **date_created** | `datetime` | YES | - | NULL |
| **data_item_type** | `int(11)` | YES | - | 0 |
| **extra_field_type** | `int(11)` | NO | - | 1 |
| **extra_field_options** | `text` | YES | - | NULL |
| **position** | `int(4)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
|   extra_field_settings_id | field_name   | import_id   |   site_id | date_created        |   data_item_type |   extra_field_type | extra_field_options   |   position |
|--------------------------:|:-------------|:------------|----------:|:--------------------|-----------------:|-------------------:|:----------------------|-----------:|
|                         1 | AdminUser    | NULL        |       180 | 2005-06-01 00:00:00 |              200 |                  1 | NULL                  |          1 |
|                         2 | UnixName     | NULL        |       180 | 2005-06-01 00:00:00 |              200 |                  1 | NULL                  |          2 |
|                         3 | BillingNotes | NULL        |       180 | 2005-06-01 00:00:00 |              200 |                  1 | NULL                  |          3 |

---

## <a name="table-feedback"></a> 📁 Table: `feedback`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **feedback_id** | `int(11)` | NO | PRI | NULL |
| **user_id** | `int(11)` | YES | - | NULL |
| **site_id** | `int(11)` | NO | - | 0 |
| **date_created** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **subject** | `varchar(255)` | NO | - |  |
| **reply_to_address** | `varchar(255)` | NO | - |  |
| **reply_to_name** | `varchar(255)` | NO | - |  |
| **feedback** | `text` | NO | - | NULL |
| **archived** | `int(1)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-history"></a> 📁 Table: `history`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **history_id** | `int(11)` | NO | PRI | NULL |
| **data_item_type** | `int(11)` | YES | - | NULL |
| **data_item_id** | `int(11)` | YES | MUL | NULL |
| **the_field** | `varchar(64)` | YES | - | NULL |
| **previous_value** | `text` | YES | - | NULL |
| **new_value** | `text` | YES | - | NULL |
| **description** | `varchar(192)` | YES | - | NULL |
| **set_date** | `datetime` | YES | - | NULL |
| **entered_by** | `int(11)` | YES | MUL | NULL |
| **site_id** | `int(11)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
|   history_id |   data_item_type |   data_item_id | the_field      | previous_value   |   new_value | description                              | set_date            |   entered_by |   site_id |
|-------------:|-----------------:|---------------:|:---------------|:-----------------|------------:|:-----------------------------------------|:--------------------|-------------:|----------:|
|            1 |              200 |              1 | !newEntry!     | NULL             |         nan | (USER) created entry.                    | 2009-11-19 10:00:20 |            1 |         1 |
|            2 |              200 |              1 | defaultCompany | NULL             |           1 | (USER) changed field(s): defaultCompany. | 2009-11-19 10:00:20 |            1 |         1 |
|            3 |              100 |              1 | !newEntry!     | NULL             |         nan | (USER) created entry.                    | 2009-11-19 10:24:54 |            1 |         1 |

---

## <a name="table-http-log"></a> 📁 Table: `http_log`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **log_id** | `int(11)` | NO | PRI | NULL |
| **site_id** | `int(11)` | NO | - | NULL |
| **remote_addr** | `char(16)` | NO | - | NULL |
| **http_user_agent** | `varchar(255)` | YES | - | NULL |
| **script_filename** | `varchar(255)` | YES | - | NULL |
| **request_method** | `varchar(16)` | YES | - | NULL |
| **query_string** | `varchar(255)` | YES | - | NULL |
| **request_uri** | `varchar(255)` | YES | - | NULL |
| **script_name** | `varchar(255)` | YES | - | NULL |
| **log_type** | `int(11)` | NO | - | NULL |
| **date** | `datetime` | YES | - | 1000-01-01 00:00:00 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-http-log-types"></a> 📁 Table: `http_log_types`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **log_type_id** | `int(11)` | NO | PRI | NULL |
| **name** | `varchar(16)` | NO | - | NULL |
| **description** | `varchar(255)` | YES | - | NULL |
| **default_log_type** | `tinyint(1) unsigned zerofill` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
|   log_type_id | name   | description   |   default_log_type |
|--------------:|:-------|:--------------|-------------------:|
|             1 | XML    | XML Job Feed  |                  0 |

---

## <a name="table-import"></a> 📁 Table: `import`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **import_id** | `int(11)` | NO | PRI | NULL |
| **module_name** | `varchar(255)` | NO | - |  |
| **reverted** | `int(1)` | NO | - | 0 |
| **site_id** | `int(11)` | NO | - | 0 |
| **import_errors** | `text` | YES | - | NULL |
| **added_lines** | `int(11)` | YES | - | NULL |
| **date_created** | `datetime` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-installtest"></a> 📁 Table: `installtest`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **id** | `int(11)` | NO | PRI | 0 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-joborder"></a> 📁 Table: `joborder`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **joborder_id** | `int(11)` | NO | PRI | NULL |
| **recruiter** | `int(11)` | YES | MUL | NULL |
| **contact_id** | `int(11)` | YES | MUL | NULL |
| **company_id** | `int(11)` | YES | MUL | NULL |
| **entered_by** | `int(11)` | NO | MUL | 0 |
| **owner** | `int(11)` | YES | MUL | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **client_job_id** | `varchar(32)` | YES | - | NULL |
| **title** | `varchar(64)` | NO | MUL |  |
| **description** | `text` | YES | - | NULL |
| **notes** | `text` | YES | - | NULL |
| **type** | `varchar(64)` | NO | - | C |
| **duration** | `varchar(64)` | YES | - | NULL |
| **rate_max** | `varchar(255)` | YES | - | NULL |
| **salary** | `varchar(64)` | YES | - | NULL |
| **status** | `varchar(16)` | NO | - | Active |
| **is_hot** | `int(1)` | NO | MUL | 0 |
| **openings** | `int(11)` | YES | MUL | NULL |
| **city** | `varchar(64)` | NO | - |  |
| **state** | `varchar(64)` | NO | - |  |
| **start_date** | `datetime` | YES | MUL | NULL |
| **date_created** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **date_modified** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **public** | `int(1)` | NO | - | 0 |
| **company_department_id** | `int(11)` | YES | - | NULL |
| **is_admin_hidden** | `int(1)` | YES | - | 0 |
| **openings_available** | `int(11)` | YES | - | 0 |
| **questionnaire_id** | `int(11)` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   joborder_id |   recruiter |   contact_id |   company_id |   entered_by |   owner |   site_id | client_job_id   | title          | description                                                                      | notes                                                                            | type   | duration   | rate_max   | salary   | status   |   is_hot |   openings | city           | state   | start_date   | date_created        | date_modified       |   public |   company_department_id |   is_admin_hidden |   openings_available | questionnaire_id   |
|--------------:|------------:|-------------:|-------------:|-------------:|--------:|----------:|:----------------|:---------------|:---------------------------------------------------------------------------------|:---------------------------------------------------------------------------------|:-------|:-----------|:-----------|:---------|:---------|---------:|-----------:|:---------------|:--------|:-------------|:--------------------|:--------------------|---------:|------------------------:|------------------:|---------------------:|:-------------------|
|            11 |        1257 |           -1 |           12 |         1257 |    1257 |         1 |                 | Data Architect | <p>Profile Sybmitte to the client Baskara Sethupathy Billing rate $80/hr for ... | Profile Sybmitte to the client Baskara Sethupathy Billing rate $80/hr for the... | C      | Long Term  | $80/hr     |          | Active   |        1 |          1 | East Brunswick | NJ      | NULL         | 2023-12-14 07:47:05 | 2023-12-14 07:48:07 |        0 |                       0 |                 0 |                    1 | NULL               |
|             2 |        1258 |            3 |            6 |            1 |    1252 |         1 |                 | DBA Developer  | <p>Test Modis Job</p>                                                            |                                                                                  | C      |            |            |          | Active   |        0 |          1 | Dallas         | TX      | NULL         | 2023-12-11 07:09:44 | 2023-12-14 06:55:50 |        0 |                       0 |                 0 |                    1 | NULL               |
|             3 |           1 |           -1 |            5 |            1 |       1 |         1 |                 | Product Owner  | <p>Product Owner</p><p>Scrum master</p>                                          |                                                                                  | C      |            |            |          | Active   |        0 |          1 | Erie           | PA      | NULL         | 2023-12-11 07:15:28 | 2023-12-11 07:26:47 |        0 |                       0 |                 0 |                    1 | NULL               |

---

## <a name="table-module-schema"></a> 📁 Table: `module_schema`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **module_schema_id** | `int(11)` | NO | PRI | NULL |
| **name** | `varchar(64)` | YES | - | NULL |
| **version** | `int(11)` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   module_schema_id | name        |   version |
|-------------------:|:------------|----------:|
|                  1 | activity    |         0 |
|                  2 | attachments |         0 |
|                  3 | calendar    |         0 |

---

## <a name="table-mru"></a> 📁 Table: `mru`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **mru_id** | `int(11)` | NO | PRI | NULL |
| **user_id** | `int(11)` | YES | MUL | NULL |
| **site_id** | `int(11)` | NO | - | 0 |
| **data_item_type** | `int(11)` | NO | - | 0 |
| **data_item_text** | `varchar(64)` | NO | - |  |
| **url** | `varchar(255)` | NO | - |  |
| **date_created** | `datetime` | NO | - | 1000-01-01 00:00:00 |

### 🔍 Sample Data (Top 3)
|   mru_id |   user_id |   site_id |   data_item_type | data_item_text                   | url                                                | date_created        |
|---------:|----------:|----------:|-----------------:|:---------------------------------|:---------------------------------------------------|:--------------------|
|     1450 |      1252 |         1 |              400 | Infrastructure/Platform Engineer | index.php?m=joborders&amp;a=show&amp;jobOrderID=67 | 2024-03-18 11:10:52 |
|     1464 |      1253 |         1 |              400 | Helathcare Business Analyst      | index.php?m=joborders&amp;a=show&amp;jobOrderID=39 | 2024-03-19 07:01:44 |
|      195 |         1 |         1 |              400 | Product Owner                    | index.php?m=joborders&amp;a=show&amp;jobOrderID=3  | 2023-12-11 08:23:36 |

---

## <a name="table-queue"></a> 📁 Table: `queue`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **queue_id** | `int(11)` | NO | PRI | NULL |
| **site_id** | `int(11)` | NO | - | NULL |
| **task** | `varchar(125)` | NO | - | NULL |
| **args** | `text` | YES | - | NULL |
| **priority** | `tinyint(2)` | NO | - | 5 |
| **date_created** | `datetime` | NO | - | NULL |
| **date_timeout** | `datetime` | NO | - | NULL |
| **date_completed** | `datetime` | YES | - | NULL |
| **locked** | `tinyint(1) unsigned` | NO | - | 0 |
| **error** | `tinyint(1) unsigned` | YES | - | 0 |
| **response** | `varchar(255)` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-saved-list"></a> 📁 Table: `saved_list`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **saved_list_id** | `int(11)` | NO | PRI | NULL |
| **description** | `varchar(64)` | NO | MUL |  |
| **data_item_type** | `int(11)` | NO | MUL | 0 |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **is_dynamic** | `int(1)` | YES | - | 0 |
| **datagrid_instance** | `varchar(64)` | YES | - |  |
| **parameters** | `text` | YES | - | NULL |
| **created_by** | `int(11)` | YES | - | 0 |
| **number_entries** | `int(11)` | YES | - | 0 |
| **date_created** | `datetime` | YES | - | NULL |
| **date_modified** | `datetime` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-saved-list-entry"></a> 📁 Table: `saved_list_entry`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **saved_list_entry_id** | `int(11)` | NO | PRI | NULL |
| **saved_list_id** | `int(11)` | NO | MUL | NULL |
| **data_item_type** | `int(11)` | NO | MUL | 0 |
| **data_item_id** | `int(11)` | NO | MUL | 0 |
| **site_id** | `int(11)` | NO | - | 0 |
| **date_created** | `datetime` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-saved-search"></a> 📁 Table: `saved_search`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **search_id** | `int(11)` | NO | PRI | NULL |
| **data_item_text** | `text` | YES | - | NULL |
| **url** | `text` | YES | - | NULL |
| **is_custom** | `int(1)` | YES | - | NULL |
| **data_item_type** | `int(11)` | YES | - | NULL |
| **user_id** | `int(11)` | YES | - | NULL |
| **site_id** | `int(11)` | YES | - | NULL |
| **date_created** | `datetime` | YES | - | NULL |

### 🔍 Sample Data (Top 3)
|   search_id | data_item_text    | url                                                                              |   is_custom |   data_item_type |   user_id |   site_id | date_created        |
|------------:|:------------------|:---------------------------------------------------------------------------------|------------:|-----------------:|----------:|----------:|:--------------------|
|           7 | h4                | /paradigmitusa/index.php?m=candidates&a=search&getback=getback&mode=searchByR... |           0 |              100 |         1 |         1 | 2023-12-11 08:06:15 |
|           8 | KEYLENT           | /paradigmitusa/index.php?m=joborders&a=search&getback=getback&mode=searchByCo... |           0 |              400 |      1252 |         1 | 2023-12-12 10:48:10 |
|           3 | Scrum AND Tableau | /paradigmitusa/index.php?m=candidates&a=search&getback=getback&mode=searchByR... |           0 |              100 |         1 |         1 | 2023-12-11 07:39:01 |

---

## <a name="table-settings"></a> 📁 Table: `settings`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **settings_id** | `int(11)` | NO | PRI | NULL |
| **setting** | `varchar(255)` | NO | - |  |
| **value** | `varchar(255)` | YES | - | NULL |
| **site_id** | `int(11)` | NO | - | 0 |
| **settings_type** | `int(11)` | YES | - | 0 |

### 🔍 Sample Data (Top 3)
|   settings_id | setting     | value                |   site_id |   settings_type |
|--------------:|:------------|:---------------------|----------:|----------------:|
|             1 | fromAddress | admin@testdomain.com |         1 |               1 |
|             2 | fromAddress | admin@testdomain.com |       180 |               1 |
|             3 | configured  | 1                    |         1 |               1 |

---

## <a name="table-site"></a> 📁 Table: `site`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **site_id** | `int(11)` | NO | PRI | NULL |
| **name** | `varchar(255)` | NO | - |  |
| **is_demo** | `int(1)` | NO | - | 0 |
| **user_licenses** | `int(11)` | NO | - | 0 |
| **entered_by** | `int(11)` | NO | - | 0 |
| **date_created** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **unix_name** | `varchar(128)` | YES | - | NULL |
| **company_id** | `int(11)` | YES | - | NULL |
| **is_free** | `int(1)` | YES | - | NULL |
| **account_active** | `int(1)` | NO | - | 1 |
| **account_deleted** | `int(1)` | NO | MUL | 0 |
| **reason_disabled** | `text` | YES | - | NULL |
| **time_zone** | `int(5)` | YES | - | 0 |
| **time_format_24** | `int(1)` | YES | - | 0 |
| **date_format_ddmmyy** | `int(1)` | YES | - | 0 |
| **is_hr_mode** | `int(1)` | YES | - | 0 |
| **file_size_kb** | `int(11)` | YES | - | 0 |
| **page_views** | `bigint(20)` | YES | - | 0 |
| **page_view_days** | `int(11)` | YES | - | 0 |
| **last_viewed_day** | `date` | YES | - | NULL |
| **first_time_setup** | `tinyint(4)` | YES | - | 0 |
| **localization_configured** | `int(1)` | YES | - | 0 |
| **agreed_to_license** | `int(1)` | YES | - | 0 |
| **limit_warning** | `tinyint(1)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
           |   site_id | name           |   is_demo |   user_licenses |   entered_by | date_created        | unix_name   | company_id   |   is_free |   account_active |   account_deleted | reason_disabled   |   time_zone |   time_format_24 |   date_format_ddmmyy |   is_hr_mode |   file_size_kb |   page_views |   page_view_days | last_viewed_day   |   first_time_setup |   localization_configured |   agreed_to_license |   limit_warning |
|----------:|:---------------|----------:|----------------:|-------------:|:--------------------|:------------|:-------------|----------:|-----------------:|------------------:|:------------------|------------:|-----------------:|---------------------:|-------------:|---------------:|-------------:|-----------------:|:------------------|-------------------:|--------------------------:|--------------------:|----------------:|
|         1 | testdomain.com |         0 |               0 |            0 | 2005-06-01 00:00:00 | nan         | NULL         |         0 |                1 |                 0 | NULL              |          -5 |                0 |                    0 |            0 |         107550 |         7421 |               40 | 2024-08-08        |                  0 |                         0 |                   1 |               0 |
|       180 | CATS_ADMIN     |         0 |               0 |            0 | 2005-06-01 00:00:00 | catsadmin   | NULL         |         0 |                1 |                 0 | NULL              |           5 |                0 |                    1 |            0 |             22 |            0 |                0 | NULL              |                  0 |                         0 |                   0 |               0 |

---

## <a name="table-sph-counter"></a> 📁 Table: `sph_counter`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **counter_id** | `int(11)` | NO | PRI | NULL |
| **max_doc_id** | `int(11)` | NO | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-system"></a> 📁 Table: `system`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **system_id** | `int(20)` | NO | PRI | 0 |
| **uid** | `int(20)` | YES | - | NULL |
| **available_version** | `int(11)` | YES | - | 0 |
| **date_version_checked** | `datetime` | NO | - | 1000-01-01 00:00:00 |
| **available_version_description** | `text` | YES | - | NULL |
| **disable_version_check** | `int(1)` | YES | - | 0 |

### 🔍 Sample Data (Top 3)
|   system_id |     uid |   available_version | date_version_checked   | available_version_description   |   disable_version_check |
|------------:|--------:|--------------------:|:-----------------------|:--------------------------------|------------------------:|
|           0 | 2618174 |                 900 | 2009-11-19 00:00:00    |                                 |                       1 |

---

## <a name="table-tag"></a> 📁 Table: `tag`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **tag_id** | `int(10) unsigned` | NO | PRI | NULL |
| **tag_parent_id** | `int(10) unsigned` | YES | - | NULL |
| **title** | `varchar(255)` | YES | - | NULL |
| **description** | `varchar(500)` | YES | - | NULL |
| **site_id** | `int(11) unsigned` | YES | - | NULL |
| **date_created** | `timestamp` | YES | - | CURRENT_TIMESTAMP |

### 🔍 Sample Data (Top 3)
|   tag_id |   tag_parent_id | title    | description   |   site_id | date_created        |
|---------:|----------------:|:---------|:--------------|----------:|:--------------------|
|        1 |             nan | tag1     | -             |         1 | 2009-11-19 23:54:02 |
|        5 |               1 | tag13    | -             |         1 | 2009-11-20 01:36:08 |
|       77 |               1 | test tag | -             |         1 | 2009-11-21 02:43:35 |

---

## <a name="table-user"></a> 📁 Table: `user`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **user_id** | `int(11)` | NO | PRI | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **user_name** | `varchar(64)` | NO | - |  |
| **email** | `varchar(128)` | YES | - | NULL |
| **password** | `varchar(128)` | NO | - |  |
| **access_level** | `int(11)` | NO | MUL | 100 |
| **can_change_password** | `int(1)` | NO | - | 1 |
| **is_test_user** | `int(1)` | NO | - | 0 |
| **last_name** | `varchar(40)` | NO | MUL |  |
| **first_name** | `varchar(40)` | NO | MUL |  |
| **is_demo** | `int(1)` | YES | - | 0 |
| **categories** | `varchar(192)` | YES | - | NULL |
| **session_cookie** | `varchar(256)` | YES | - | NULL |
| **pipeline_entries_per_page** | `int(8)` | YES | - | 15 |
| **column_preferences** | `longtext` | YES | - | NULL |
| **force_logout** | `int(1)` | YES | - | 0 |
| **title** | `varchar(64)` | YES | - |  |
| **phone_work** | `varchar(64)` | YES | - |  |
| **phone_cell** | `varchar(64)` | YES | - |  |
| **phone_other** | `varchar(64)` | YES | - |  |
| **address** | `text` | YES | - | NULL |
| **notes** | `text` | YES | - | NULL |
| **company** | `varchar(255)` | YES | - | NULL |
| **city** | `varchar(64)` | YES | - | NULL |
| **state** | `varchar(64)` | YES | - | NULL |
| **zip_code** | `varchar(16)` | YES | - | NULL |
| **country** | `varchar(128)` | YES | - | NULL |
| **can_see_eeo_info** | `int(1)` | YES | - | 0 |

### 🔍 Sample Data (Top 3)
|   user_id |   site_id | user_name      | email                | password                         |   access_level |   can_change_password |   is_test_user | last_name     | first_name   |   is_demo | categories   | session_cookie                  |   pipeline_entries_per_page | column_preferences                                                               |   force_logout | title   | phone_work   | phone_cell   | phone_other   | address   | notes   | company   | city   | state   | zip_code   | country   |   can_see_eeo_info |
|----------:|----------:|:---------------|:---------------------|:---------------------------------|---------------:|----------------------:|---------------:|:--------------|:-------------|----------:|:-------------|:--------------------------------|----------------------------:|:---------------------------------------------------------------------------------|---------------:|:--------|:-------------|:-------------|:--------------|:----------|:--------|:----------|:-------|:--------|:-----------|:----------|-------------------:|
|         1 |         1 | admin          | admin@testdomain.com | df4c83ab9209e973c9c96e693810d350 |            500 |                     1 |              0 | Administrator | CATS         |         0 | NULL         | CATS=uen9ktk42d8gf7nudh4793t290 |                          15 | a:8:{s:31:"home:ImportantPipelineDashboard";a:6:{i:0;a:2:{s:4:"name";s:10:"Fi... |              0 |         |              |              |               | NULL      | NULL    | NULL      | NULL   | NULL    | NULL       | NULL      |                  0 |
|      1250 |       180 | cats@rootadmin | 0                    | cantlogin                        |              0 |                     0 |              0 | Automated     | CATS         |         0 | NULL         | nan                             |                          15 | nan                                                                              |              0 |         |              |              |               | NULL      | NULL    | NULL      | NULL   | NULL    | NULL       | NULL      |                  0 |
|      1251 |         1 | hradmin        | hr@paradigmit.com    | 058b12398009dbe4a7479dfbd66b33ad |            300 |                     1 |              0 | ParadimIT     | HR           |         0 | NULL         | CATS=kfu4b5f6bj4bkpkdutmc8f4sc3 |                          15 | a:8:{s:31:"home:ImportantPipelineDashboard";a:6:{i:0;a:2:{s:4:"name";s:10:"Fi... |              0 |         |              |              |               | NULL      | NULL    | NULL      | NULL   | NULL    | NULL       | NULL      |                  0 |

---

## <a name="table-user-login"></a> 📁 Table: `user_login`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **user_login_id** | `int(11)` | NO | PRI | NULL |
| **user_id** | `int(11)` | YES | MUL | NULL |
| **site_id** | `int(11)` | NO | MUL | 0 |
| **ip** | `varchar(128)` | NO | MUL |  |
| **user_agent** | `varchar(255)` | YES | - | NULL |
| **date** | `datetime` | NO | MUL | 1000-01-01 00:00:00 |
| **successful** | `int(1)` | NO | MUL | 0 |
| **host** | `varchar(255)` | YES | - | NULL |
| **date_refreshed** | `datetime` | YES | MUL | NULL |

### 🔍 Sample Data (Top 3)
|   user_login_id |   user_id |   site_id | ip        | user_agent                                                                       | date                |   successful | host      | date_refreshed      |
|----------------:|----------:|----------:|:----------|:---------------------------------------------------------------------------------|:--------------------|-------------:|:----------|:--------------------|
|               1 |         1 |         1 | 127.0.0.1 | Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.5) Gecko/20091102 Fi... | 2009-11-19 09:59:57 |            1 | 127.0.0.1 | 2009-11-20 14:29:36 |
|               2 |         1 |         1 | ::1       | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gec... | 2023-12-06 23:25:08 |            1 | ::1       | 2023-12-11 01:58:43 |
|               3 |         1 |         1 | ::1       | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gec... | 2023-12-06 23:54:37 |            1 | ::1       | 2023-12-07 00:04:30 |

---

## <a name="table-word-verification"></a> 📁 Table: `word_verification`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **word_verification_ID** | `int(11)` | NO | PRI | NULL |
| **word** | `varchar(28)` | NO | - |  |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-xml-feed-submits"></a> 📁 Table: `xml_feed_submits`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **feed_id** | `int(11)` | NO | PRI | NULL |
| **feed_site** | `varchar(75)` | NO | - | NULL |
| **feed_url** | `varchar(255)` | NO | - | NULL |
| **date_last_post** | `date` | NO | - | NULL |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

## <a name="table-xml-feeds"></a> 📁 Table: `xml_feeds`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **xml_feed_id** | `int(11)` | NO | PRI | NULL |
| **name** | `varchar(50)` | NO | - | NULL |
| **description** | `varchar(255)` | YES | - | NULL |
| **website** | `varchar(255)` | YES | - | NULL |
| **post_url** | `varchar(255)` | NO | - | NULL |
| **success_string** | `varchar(255)` | NO | - | NULL |
| **xml_template_name** | `varchar(255)` | NO | - | NULL |

### 🔍 Sample Data (Top 3)
|   xml_feed_id | name        | description                       | website                    | post_url                                    | success_string                             | xml_template_name   |
|--------------:|:------------|:----------------------------------|:---------------------------|:--------------------------------------------|:-------------------------------------------|:--------------------|
|             1 | Indeed      | Indeed.com job search engine.     | http://www.indeed.com      | http://www.indeed.com/jsp/includejobs.jsp   | Thank you for submitting your XML job feed | indeed              |
|             2 | SimplyHired | SimplyHired.com job search engine | http://www.simplyhired.com | http://www.simplyhired.com/confirmation.php | Thanks for Contacting Us                   | simplyhired         |

---

## <a name="table-zipcodes"></a> 📁 Table: `zipcodes`

### 🛠 Schema (Columns)
| Column | Type | Null | Key | Default |
| :--- | :--- | :--- | :--- | :--- |
| **zipcode** | `mediumint(9)` | NO | PRI | 0 |
| **city** | `tinytext` | NO | - | NULL |
| **state** | `varchar(2)` | NO | - |  |
| **areacode** | `smallint(6)` | NO | - | 0 |

### 🔍 Sample Data (Top 3)
> ℹ️ *This table is currently empty.*

---

/