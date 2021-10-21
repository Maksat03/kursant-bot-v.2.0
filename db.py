import sqlite3

class DB:
	def __init__(self):
		self.conn = sqlite3.connect("db.db")
		self.cursor = self.conn.cursor()
		tables = {
			"EHT_course":
				"""
				iin 				TEXT,
				fullname			TEXT,
				school				TEXT,
				parents_phone_number 	TEXT,
				phone_number		TEXT,
				ss1 				TEXT,
				ss2 				TEXT,
				activity			TEXT,
				complaint 			TEXT,
				last_payment_date	date
				""",
			"tests":
				"""
				iin 				TEXT,
				passing_date		date,
				oc					INTEGER,
				mc					INTEGER,
				history				INTEGER,
				ss1 				INTEGER,
				ss2 				INTEGER
				""",
			"attendance":
				"""
				iin 				TEXT,
				month				TEXT,
				oc					INTEGER,
				ocX					INTEGER,
				mc					INTEGER,
				mcX					INTEGER,
				history				INTEGER,
				historyX			INTEGER,
				ss1					INTEGER,
				ss1X				INTEGER,
				ss2 				INTEGER,
				ss2X				INTEGER
				""",
			"courses":
				"""
				id 					INTEGER PRIMARY KEY,
				course_table_name	TEXT,
				course 				TEXT,
				src					TEXT,
				description			TEXT
				""",
			"kids":
				"""
				iin 					TEXT,
				fullname				TEXT,
				parents_phone_number	TEXT,
				phone_number			TEXT
				""",
			"classes_5_6_7":
				"""
				iin 					TEXT,
				fullname				TEXT,
				parents_phone_number	TEXT,
				phone_number 			TEXT,
				school					TEXT,
				class 					INTEGER
				"""
		}
		for table in tables.keys():
			self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({tables[table]})")

	def get_all_data(self, table):
		self.cursor.execute(f"SELECT * FROM {table}")
		return self.cursor.fetchall()

	def add(self, table, data):
		if table == "courses":
			self.cursor.execute(f"INSERT INTO courses (course_table_name, course, img, description, price) VALUES ({data})")
		elif table in ["EHT_course", "kids", "classes_5_6_7"]:
			self.cursor.execute(f"INSERT INTO {table} (iin) VALUES (?)", (data, ))
		elif table == "attendance":
			self.cursor.execute(f"INSERT INTO attendance (iin, month) VALUES (?, ?)", (data[0], data[1]))
		elif table == "tests":
			self.cursor.execute(f"INSERT INTO tests (iin, passing_date) VALUES (?, ?)", (data[0], data[1]))
		else:
			self.cursor.execute(f"INSERT INTO {table} VALUES ({data})")
		self.conn.commit()

	def get_list_of_courses(self):
		self.cursor.execute("SELECT id, course FROM courses")
		return self.cursor.fetchall()

	def get(self, table, item, where):
		self.cursor.execute(f"SELECT {item} FROM {table} WHERE {where[0]} = '{where[1]}'")
		return self.cursor.fetchall()

	def update(self, table, item, value, where):
		if table == "attendance":
			self.cursor.execute(f"UPDATE {table} SET {item} = '{value}' WHERE (iin, month) = (?, ?)", (where[0], where[1]))
		elif table == "tests":
			self.cursor.execute(f"UPDATE {table} SET {item} = '{value}' WHERE (iin, passing_date) = (?, ?)", (where[0], where[1]))
		else:
			self.cursor.execute(f"UPDATE {table} SET {item} = '{value}' WHERE {where[0]} = '{where[1]}'")
		self.conn.commit()

	def delete(self, table, where):
		if table == "tests":
			self.cursor.execute(f'DELETE FROM {table} WHERE (iin, passing_date) = (?, ?)', (where[0], where[1]))
		else:
			self.cursor.execute(f'DELETE FROM {table} WHERE {where[0]} = "{where[1]}"')
		self.conn.commit()

db = DB()		