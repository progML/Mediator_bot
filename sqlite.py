import sqlite3


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_user(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()

    def add_user(self, user_id, username):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id, username, balance, role) VALUES(?,?,?,?)",
                                       (user_id, username, 0, "USER"))

    def get_money(self, user_id, phone, code):
        with self.connection:
            return self.cursor.execute("INSERT into wallet(user_id, phone, code) VALUES(?,?,?)",
                                       (user_id, phone, code))

    def check(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM wallet WHERE user_id = ?", (user_id,)).fetchone()

    def delete_money(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM wallet WHERE user_id = ?", (user_id,))

    def check_balance(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

    def update_balance(self, amount, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET balance = ? WHERE `user_id` = ?", (amount, user_id))

    def selectPlace(self):
        with self.connection:
            return self.cursor.execute("Select DISTINCT place from domains").fetchall()

    def selectDomains(self, place):
        with self.connection:
            return self.cursor.execute("SELECT domain FROM domains WHERE place = ?", (place,)).fetchall()

    def selectAllDomains(self):
        with self.connection:
            return self.cursor.execute("SELECT domain FROM domains").fetchall()

    def addTask(self, user_id, domain, technical_task, file_id, deadline, amount, status):
        with self.connection:
            return self.cursor.execute(
                "INSERT into tasks(user_id, domain, technical_task, file_id, deadline, amount, status, executor) VALUES(?,?,?,?,?,?,?, -1)",
                (user_id, domain, technical_task, file_id, deadline, amount, status))

    def selectAllTask(self, place):
        with self.connection:
            return self.cursor.execute(
                "SELECT task_id, tasks.domain, technical_task, file_id, deadline, amount FROM tasks INNER JOIN domains ON tasks.domain = domains.domain where place=? and status = 'waiting'",
                (place,)).fetchall()

    def countAllTask(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT count(user_id) FROM tasks where status = 'waiting'").fetchone()

    def countPlace(self, place):
        with self.connection:
            return self.cursor.execute(
                "SELECT count(user_id) FROM tasks INNER JOIN domains ON tasks.domain = domains.domain where place=? and status = 'waiting'",
                (place,)).fetchone()

    def checkUserTask(self, userId):
        with self.connection:
            return self.cursor.execute(
                "SELECT count(task_id) FROM tasks where user_id=? and status = 'waiting'",
                (userId,)).fetchone()

    def get_admin(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT count(username) FROM users WHERE user_id = ? and role = 'ADMIN'",
                                       (user_id,)).fetchone()

    def delete_task(self, taskId):
        with self.connection:
            return self.cursor.execute("DELETE from tasks where task_id = ?",
                                       taskId).fetchone()

    def find_userId_taskId(self, taskId):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM tasks where task_id = ?",
                                       taskId).fetchone()

    def update_users(self, userId):
        with self.connection:
            return self.cursor.execute("UPDATE users SET role = 'BAN' where user_id = ?",
                                       userId).fetchone()

    def block_check(self, userId):
        with self.connection:
            return self.cursor.execute("SELECT role from users where user_id = ?",
                                       (userId,)).fetchone()

    def command_unblock(self, userName):
        with self.connection:
            return self.cursor.execute("UPDATE users SET role = 'USER' where username = ?",
                                       (userName,)).fetchone()

    def select_task(self, userId):
        with self.connection:
            return self.cursor.execute(
                "SELECT task_id, deadline, amount, executor, file_id FROM tasks where user_id=? and status = 'waiting'",
                (userId,)).fetchall()

    def count_task(self, userId):
        with self.connection:
            return self.cursor.execute(
                "SELECT count(task_id) FROM tasks WHERE user_id=? ",
                (userId,)).fetchone()

    def find_username(self, userId):
        with self.connection:
            return self.cursor.execute(
                "SELECT username FROM users where user_id=? ",
                (userId,)).fetchone()

    def get_username(self, taskId):
        with self.connection:
            return self.cursor.execute(
                "SELECT username FROM tasks where task_id=? ",
                (taskId,)).fetchone()
