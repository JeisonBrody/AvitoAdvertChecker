import sqlite3


class BD:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `clients` WHERE `id_client` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status = True):
        """Добавляем нового подписчика и ставим активную подписку"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `clients` (`id_client`, `status_client`) VALUES(?,?)", (user_id, status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `clients` SET `status_client` = ? WHERE `id_client` = ?", (status, user_id))

    def update_city(self, user_id, city):
        """Обновляем выбранный город"""
        with self.connection:
            return self.cursor.execute("""UPDATE clients SET city = ? WHERE id_client = ?""", (city, user_id))

    def update_brand(self, user_id, brand):
        """Обновляем выбранную марку авто"""
        with self.connection:
            return self.cursor.execute("""UPDATE clients SET brand = ? WHERE id_client = ?""", (brand, user_id))

    def update_id_advert(self, user_id, id_advert):
        """Обновляем id объявления"""
        with self.connection:
            return self.cursor.execute("""UPDATE clients SET id_advert = ? WHERE id_client = ?""", (id_advert, user_id))

    def get_info(self, user_id):
        """Информация клиента"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM clients WHERE id_client = ?", (user_id,)).fetchone()

    def check_status(self, user_id):
        """Проверка статуса пользователю на подписку"""
        with self.connection:
            result = self.cursor.execute("SELECT status_client FROM clients WHERE id_client = ?", (user_id,)).fetchone()
            return bool(result[0])

    def is_pars(self, user_id):
        """Проверяем в каком состоянии парсер у юзера"""
        with self.connection:
            return self.cursor.execute("SELECT is_pars FROM clients where id_client = ?", (user_id,)).fetchone()

    def stop_pars(self, user_id):
        """Остановка парсера"""
        with self.connection:
            return self.cursor.execute("UPDATE clients SET is_pars = FALSE where id_client = ?", (user_id,))

    def start_pars(self, user_id):
        """Включение парсера"""
        with self.connection:
            return self.cursor.execute("UPDATE clients SET is_pars = TRUE where id_client = ?", (user_id,))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()