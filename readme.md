# Запуск:
* pip install -r requirements. txt
* python maage.py runserver
 
# Создание суперюзера(администратора):
* py manage.py createsuperuser

# Почему sqlite?
* Любая другоя бд для тестового - оверкилл

# Остальное:
* Тестовое отвечает всем запросам, указанным в тестовом задании
* В репозитории уже лежит промигрированая бд
* Практически все вью - функциональные, так как они небольшие
* В urls.py в папке самого приложения (tests_app/) на большую часть вью наложено ограничение login_required
* Я вообще не трогал визуальное оформление, т.к. об этом в задании ни слова

Спасибо за уделённое время!
