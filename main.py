linux_or_windows = "Windows"

import os
import logging
logging.basicConfig(level=logging.INFO)

from aiogram import Bot, Dispatcher, executor
from aiogram.types import ContentType, Message, CallbackQuery

from db import db
import pandas as pd
from time import time
from markups import *

bot = Bot(token="1331857087:AAHzqh5R_9IBnOhVePQuyNENBbwoCSvEkr0", parse_mode='HTML')
dp = Dispatcher(bot)

admins = []
users_who_want_to_see_student_results = []
users_who_want_to_enroll_in_a_course = []
courses = {
	"EHT_course": {
		"answers": ["Оқушының толық аты жөнін еңгізіңіз", "Оқитын мектебінін атын еңгізіңіз", "Бір ата-анасының телефон нөмерін еңгізіңіз", "Оқушының телефон нөмерін еңгізіңіз", "Таңдап жатқан 1-інші бейімдік пәнін еңгізіңіз", "Таңдап жатқан 2-інші бейімдік пәнін еңгізіңіз"],
		"columns": ["fullname", "school", "parents_phone_number", "phone_number", "ss1", "ss2"],
		"names": ['ФИО', "Оқитын мектебі", "Бір ата-анасының телефон нөмері", "Оқушының телефон нөмері", "1-інші бейімдік пәні", "2-інші бейімдік пәні"]
	},
	"kids": {
		"answers": ["Оқушының толық аты жөнін еңгізіңіз", "Бір ата-анасының телефон нөмерін еңгізіңіз", "Оқушының телефон нөмерін еңгізіңіз"],
		"columns": ["fullname", "parents_phone_number", "phone_number"],
		"names": ['ФИО', "Бір ата-анасының телефон нөмері", "Оқушының телефон нөмері"]
	},
	"classes_5_6_7": {
		"answers": ["Оқушының толық аты жөнін еңгізіңіз", "Бір ата-анасының телефон нөмерін еңгізіңіз", "Оқушының телефон нөмерін еңгізіңіз", "Оқитын мектебінін атын еңгізіңіз", "Нешінші сыныпта оқиды?"],
		"columns": ["fullname", "parents_phone_number", "phone_number", "school", "class"],
		"names": ['ФИО', "Бір ата-анасының телефон нөмері", "Оқушының телефон нөмері", "Оқитын мектебі", "Оқитын сыныбы"]
	}
}
about_us = '“КурсAnt” Білім беру орталығы 1️⃣1️⃣сынып оқушыларын Ұлттық Біріңғай Тестілеуіне дайындаймыз. Алматы, Шымкент қалаларында және Ордабасы ауданында филиалдарымыз бар.\n\nШымкент қаласында 5️⃣жыл қызмет етудеміз. Осы 5жыл ішінде 2500-дей түлекпен жұмыс жасадық. 2000-ға жуық оқушы ГРАНТ иегерлері шығып,қуаныштарына куә болдық.'

@dp.message_handler(commands=['start'])
async def welcome(msg: Message):
	await msg.answer(
		text = "Қош келдіңіз",
		reply_markup = starting_markup
	)

def list_of_courses_markup(Type):
	if Type == "result" or Type == "admin":
		inline_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ҰБТ-ға дайындық курсы", callback_data=f"{Type}1")]])
		return inline_markup
	else:
		list_of_courses = db.get_list_of_courses()
		inline_markup = InlineKeyboardMarkup(resize_keyboard=True)
		for course in list_of_courses:
			inline_markup.add(InlineKeyboardButton(text=course[1], callback_data=f"{Type}{course[0]}"))
		return inline_markup

async def cancel_cmd(msg):
	for i, user in enumerate(users_who_want_to_see_student_results):
		if user[0] == msg.from_user.id:
			del users_who_want_to_see_student_results[i]
			break
	else:
		for i, user in enumerate(users_who_want_to_enroll_in_a_course):
			if user[0] == msg.from_user.id:
				del users_who_want_to_enroll_in_a_course[i]
				db.delete(user[2], ["iin", user[1]])
				break

	await msg.answer("Басты бет", reply_markup=starting_markup)

@dp.message_handler(content_types=ContentType.TEXT)
async def msg_handler(msg: Message):
	global users_who_want_to_enroll_in_a_course, users_who_want_to_see_student_results
	print(users_who_want_to_see_student_results, users_who_want_to_enroll_in_a_course)
	if msg.text == "212234":
		await msg.answer("Сіз админ режимге өтудесіз, бірақ алдымен сіз қалап тұрған оқушының оқитын курсын таңдаңыз", reply_markup=list_of_courses_markup("admin"))
		#
	else:
		for i, admin in enumerate(admins):
			if admin[0] == msg.from_user.id:
				if msg.text == "Бас тарту" or msg.text == "Админ режимнен шығу":
					if admin[3] == None:
						del admins[i]
						await msg.answer("Сіз админ режимнен шықтыңыз", reply_markup=starting_markup)
					else:
						if admin[3].startswith("tests:"):
							db.delete("tests", [admin[1], admin[3].split(":")[1]])
						admin[3] = None
						await msg.answer("Бас тартылды, басты бет", reply_markup=admin_markup)
				elif admin[1] == None:
					try:
						data = db.get(admin[2], "fullname", ["iin", msg.text])[0]
					except:
						await msg.answer("Мұндай ЖСН(ИИН) бар оқушы тіркелмеген")
					else:							
						admins[i][1] = msg.text
						await msg.answer("Сіз админ режимге толық өттіңіз\n\nСіз таңдаған оқушының толық аты жөні: "+data[0], reply_markup=admin_markup)
				elif msg.text == '"Активность" статусын өзгерту':
					admins[i][3] = "activity"
					res = db.get(admin[2], 'activity', ['iin', admin[1]])[0][0]
					if res == None:
						await msg.answer(f"Қазіргі 'Активность' статусы: Статус әзірше орнатылмаған\n\nСтатусты өзгерту үшін текст жазып жіберіңіз. Статус сол текстке өзгертіледі.", reply_markup=cancel_markup)
					else:
						await msg.answer(f"Қазіргі 'Активность' статусы: {res}\n\nСтатусты өзгерту үшін текст жазып жіберіңіз. Статус сол текстке өзгертіледі.", reply_markup=cancel_markup)
				elif msg.text == "Шағым қалдыру":
					admins[i][3] = "complaint"
					res = db.get(admin[2], 'complaint', ['iin', admin[1]])[0][0]
					if res == None:
						await msg.answer(f"Ең соңғы шағым: Шағым жоқ\n\nШағым қалдыру үшін текст жазып жіберіңіз. Шағым текстті сол сіз жіберген текстке өзгертіледі", reply_markup=cancel_markup)
					else:
						await msg.answer(f"Ең соңғы шағым: {res}\n\nШағым қалдыру үшін текст жазып жіберіңіз. Шағым текстті сол сіз жіберген текстке өзгертіледі", reply_markup=cancel_markup)
				elif msg.text == "Соңғы рет жасалған төлем":
					admins[i][3] = "last_payment_date"
					res = db.get(admin[2], 'last_payment_date', ['iin', admin[1]])[0][0]
					if res == None:
						await msg.answer(f"Соңғы рет төлеген күн: Күні орнатылмаған\n\nСоңғы рет төлеген күнді жазыңыз.", reply_markup=cancel_markup)
					else:
						await msg.answer(f"Соңғы рет төлеген күн: {res}\n\nСоңғы рет төлеген күнді жазыңыз.", reply_markup=cancel_markup)
				elif msg.text == "Тест жауаптарын енгізу":
					admins[i][3] = "tests::passing_date"
					await msg.answer("\n\nТест өтілген күнді еңгізіңіз:", reply_markup=cancel_markup)
				elif msg.text == "Посещаемость":
					months = db.get("attendance", "month", ["iin", admin[1]])
					markup = InlineKeyboardMarkup()
					for month in months:
						markup.add(InlineKeyboardButton(text=month[0], callback_data=f"month:{month[0]}"))
					markup.add(InlineKeyboardButton(text="Ай қосу", callback_data="add_month"))
					await msg.answer("Батырмаларды басып өзгертсеңіз болады!", reply_markup=markup)
				elif msg.text == "Басқа оқушы таңдау":
					await msg.answer("Оқушы оқитын курсты таңдаңыз", reply_markup=list_of_courses_markup("admin"))
					#
				elif msg.text == "Excel-ге шығару":
					await msg.answer("Күтіңіз...")
					EHT_students = {
						'ИИН': [],
						'ФИО': [],
						'Мектеп': [],
						'Ата-анасының тел. нөмері': [],
						'Оқушының тел. нөмері': [],
						'Бейімдік пән 1': [],
						'Бейімдік пән 2': [],
						'Активность': [],
						'Шағым': [],
						'Соңғы рет жасалған төлем': []
					}
					kids = {
						'ИИН': [],
						'ФИО': [],
						'Ата-анасының тел. нөмері': [],
						'Оқушының тел. нөмері': []
					}
					classes_5_6_7 = {
						'ИИН': [],
						'ФИО': [],
						'Ата-анасының тел. нөмері': [],
						'Оқушының тел. нөмері': [],
						'Мектеп': [],
						'Сынып': []
					}
					tests = {
						'ИИН': [],
						'Тест өтілген күн': [],
						'Оқу сау.': [],
						'Мат. сау.': [],
						'Қ. тарих': [],
						'Бейімдік пән 1': [],
						'Бейімдік пән 2': []
					}
					attendance = {
						'ИИН': [],
						'Ай': [],
						'Общ. сабақ саны (Оқу сау.)': [],
						'Сабаққа келді (Оқу сау.)': [],
						'Общ. сабақ саны (Мат. сау.)': [],
						'Сабаққа келді (Мат. сау.)': [],
						'Общ. сабақ саны (Қ. тарих)': [],
						'Сабаққа келді (Қ. тарих)': [],
						'Общ. сабақ саны (Бейімдік пән 1)': [],
						'Сабаққа келді (Бейімдік пән 1)': [],
						'Общ. сабақ саны (Бейімдік пән 2)': [],
						'Сабаққа келді (Бейімдік пән 2)': [],
					}
					for data in db.get_all_data("EHT_course"):
						for i, key in enumerate(EHT_students.keys()):
							EHT_students[key].append(data[i])
					for data in db.get_all_data("tests"):
						for i, key in enumerate(tests.keys()):
							tests[key].append(data[i])
					for data in db.get_all_data("attendance"):
						for i, key in enumerate(attendance.keys()):
							attendance[key].append(data[i])
					for data in db.get_all_data("kids"):
						for i, key in enumerate(kids.keys()):
							kids[key].append(data[i])
					for data in db.get_all_data("classes_5_6_7"):
						for i, key in enumerate(classes_5_6_7.keys()):
							classes_5_6_7[key].append(data[i])

					tests = pd.DataFrame(tests)
					EHT_students = pd.DataFrame(EHT_students)
					attendance = pd.DataFrame(attendance)
					kids = pd.DataFrame(kids)
					classes_5_6_7 = pd.DataFrame(classes_5_6_7)
					
					Time = int(time())
					file = f'Document-{Time}.xlsx'

					sheets = {"ҰБТ-ға дайындық курсы": EHT_students, "Курс Kids": kids, "5, 6, 7 сынып курсы": classes_5_6_7, "ҰБТ тесттері": tests, "ҰБТ посещаемость": attendance}
					writer = pd.ExcelWriter(file, engine='xlsxwriter')

					for sheet in sheets.keys():
					    sheets[sheet].to_excel(writer, sheet_name=sheet, index=False)

					writer.save()
					writer.close()

					with open(file, "rb") as filee:
						await msg.answer_document(filee)

					if linux_or_windows == "Windows":
						os.system(f"del {file}")
					else:
						os.system(f"rm {file}")
				else:
					if str(admin[3]).startswith("tests:"):
						splitted_data = admin[3].split(":")
						date = splitted_data[1]
						column = splitted_data[2]
						if column == "passing_date":
							db.add("tests", [admin[1], msg.text])
							admin[3] = f"tests:{msg.text}:oc"
							await msg.answer("Оқу сауаттылығынан неше балл жинады?")
						else:
							if column != "confirmation": db.update("tests", column, msg.text, [admin[1], date])
							text = ""
							markup = cancel_markup
							if column == "oc":
								text = "Математикалық сауаттылығынан неше балл жинады?"
								admin[3] = f"tests:{date}:mc"
							elif column == "mc":
								text = "Қазақстан тарихынан неше балл жинады?"
								admin[3] = f"tests:{date}:history"
							elif column == "history":
								text = f"{db.get(admin[2], 'ss1', ['iin', admin[1]])[0][0]} бойынша неше балл жинады?"
								admin[3] = f"tests:{date}:ss1"
							elif column == "ss1":
								text = f"{db.get(admin[2], 'ss2', ['iin', admin[1]])[0][0]} бойынша неше балл жинады?"
								admin[3] = f"tests:{date}:ss2"
							elif column == "ss2":
								text = "Аяқталуға сәл қалды, тек растау берсеңіз болды"
								admin[3] = f"tests:{date}:confirmation"
								markup = ReplyKeyboardMarkup(resize_keyboard=True)
								markup.add("Растау")
								markup.add("Бас тарту")
							else: # Confirmation
								if msg.text == "Растау":
									text = "Тест жауаптары базаға енгізілді"
									markup = admin_markup
									admin[3] = None
								else:
									await msg.answer("Өтініш кнопкалардың біреуін басыңыз")
									break
							await msg.answer(text, reply_markup=markup)

					elif admin[3] in ["activity", "complaint", "last_payment_date"]:
						db.update(admin[2], admin[3], msg.text, ["iin", admin[1]])
						await msg.answer("Орындалды", reply_markup=admin_markup)
						admin[3] = None
					else:
						await msg.answer("Мен бұл сообщениеге қалай жауап беретінімді білмеймін")
						#
				break
		else:
			if msg.text == "Біз туралы":
				with open("src/default.png", "rb") as photo:
					await bot.send_photo(msg.from_user.id, photo.read(), caption=about_us)
				
				# with open("video.mp4", "rb") as video:
				# 	await bot.send_video(msg.chat.id, video, caption=about_us)
			elif msg.text == "Курсқа тіркелу":
				markup = list_of_courses_markup("lesson")
				await msg.answer("Курстар тізімі:", reply_markup=markup)
			elif msg.text == "Оқушының оқу үлгерімін көру":
				await msg.answer("Қалап тұрған оқушыңыз қай курста оқиды?", reply_markup=list_of_courses_markup("result"))
				#
			elif msg.text == "Біздің әлеуметтік желілеріміз":
				text = "Біздің әлеуметтік парақшаларымыз:\n"
				text += "1. <a href='https://vk.com/edu.kursant.shym'>Вконтакте</a>\n"
				text += "2. <a href='https://instagram.com/edu.kursant.ubt?utm_medium=copy_link'>Инстаграм</a>\n"
				text += "3. <a href='https://t.me/easyhistory2021'>Телеграм</a>"
				await msg.answer(text, disable_web_page_preview=True)
			elif msg.text == "Акциялар, жеңілдіктер":
				# discounts = db.get_all_data("discounts")
				# for discount in discounts:
				# 	with open(discount[1], "rb") as photo:
				# 		await bot.send_photo(msg.from_user.id, photo.read(), caption=discount[0])
				await msg.answer("1. Алтын белгі үміткерлеріне ҰБТ-ға дайындық курсына: 26.000 тг\n2. Көпбалалы, жартылай жетім оқушыларға ҰБТ-ға дайындық курсына: 26.000 тг")
			elif msg.text == "Менеджермен хабарласу":
				await msg.answer("Менеджеріміз: Аружан Апай\nНөмері: +7 707 153 0210")
				#
			elif msg.text == "Алдыңғы жылғы результаттар":
				await msg.answer("<a href='https://www.instagram.com/s/aGlnaGxpZ2h0OjE3OTE0MTg3NDc2NzQ0NzQ1?story_media_id=2567653469922508716_20311619532&utm_medium=copy_link'>ҰБТ 2021 нәтижелері</a>", disable_web_page_preview=True)
				#
			elif msg.text == "ҰБТ нұсқаларын тегін алу":
				await msg.answer("Барлық ҰБТ нұсқаларын жауаптарымен <a href='https://vk.com/edu.kursant.shym'>тегін алу</a>", disable_web_page_preview=True)
				#
			elif msg.text == "Бас тарту" or msg.text == "Басты бетке оралу":
				await cancel_cmd(msg)
				#
			elif msg.text == "Тесттер":
				for i, user in enumerate(users_who_want_to_see_student_results):
					if user[0] == msg.from_user.id:
						tests = db.get("tests", "*", ["iin", user[1]])

						if len(tests) == 0:
							text = "Әзірше ешқандайда тест тапсырмаған"
							inline_markup = None
						else:
							text = "Тесттер:"
							inline_markup = InlineKeyboardMarkup()

							for i, test in enumerate(tests):
								inline_markup.add(InlineKeyboardButton(text = test[1]+f"; Жалпы балл: {test[2]+test[3]+test[4]+test[5]+test[6]}", callback_data = f"history_of_tests;{test[1]}"))
								if i == 9:
									break

							inline_markup.add(
								InlineKeyboardButton(text = "◀️", callback_data = "nothing"),
								InlineKeyboardButton(text = "▶️", callback_data = "page_of_history_of_tests:10:0")
							)

						await msg.answer(text, reply_markup=inline_markup)
			elif msg.text == "Посещаемость":
				for i, user in enumerate(users_who_want_to_see_student_results):
					if user[0] == msg.from_user.id:
						attendance = db.get("attendance", "*", ["iin", user[1]])
						if len(attendance) == 0:
							await msg.answer("Сабаққа 1 рет болсын келмеген")
						else:
							for i in attendance:
								i = list(i)
								for j in range(2, 12):
									if i[j] == None:
										i[j] = 0
								text = ""
								text += "\n- " + i[1] + ":\n"
								text += "1. Оқу сауаттылығы:\n"
								text += f"- Жалпы өтілген сабақ саны: {i[2]};\n- Келді: {i[3]} сабаққа\n"
								text += "2. Математика сауаттылығы:\n"
								text += f"- Жалпы өтілген сабақ саны: {i[4]};\n- Келді: {i[5]} сабаққа\n"
								text += "3. Тарих:\n"
								text += f"- Жалпы өтілген сабақ саны: {i[6]};\n- Келді: {i[7]} сабаққа\n"
								text += f"4. {db.get(user[2], 'ss1', ['iin', user[1]])[0][0]}:\n"
								text += f"- Жалпы өтілген сабақ саны: {i[8]};\n- Келді: {i[9]} сабаққа\n"
								text += f"5. {db.get(user[2], 'ss2', ['iin', user[1]])[0][0]}:\n"
								text += f"- Жалпы өтілген сабақ саны: {i[10]};\n- Келді: {i[11]} сабаққа\n"
								await msg.answer(text)
			elif msg.text == "Мұғалімдердің шағымдары":
				for i, user in enumerate(users_who_want_to_see_student_results):
					if user[0] == msg.from_user.id:
						res = db.get(user[2], "complaint", ["iin", user[1]])[0][0]
						if res == None:
							await msg.answer("Шағым жоқ")
						else:
							await msg.answer(res)
						break
			else:
				for i, user in enumerate(users_who_want_to_see_student_results):
					if user[0] == msg.from_user.id:
						if user[1] == None:
							try:
								data = db.get(user[2], "iin, fullname, activity, last_payment_date", ["iin", msg.text])[0]
							except:
								await msg.answer("Мұндай ЖСН(ИИН) бар оқушы тіркелмеген", reply_markup=starting_markup)
								await cancel_cmd(msg)
							else:							
								if data[0]:
									users_who_want_to_see_student_results[i][1] = msg.text
									text = data[3]
									if text == None:
										text = "Күні орнатылмаған"
									if data[2] == None:
										await msg.answer("Оқушының толық аты жөні: "+data[1]+"\n"+"Активность: Статус әзірше орнатылмаған\nБатырмаларды басып оқушының оқу үлгерімін көрсеңіз болады.\nСоңғы рет төлеген күн: " + text, reply_markup=results_markup)
									else:
										await msg.answer("Оқушының толық аты жөні: "+data[1]+"\n"+"Активность: "+str(data[2])+"\nБатырмаларды басып оқушының оқу үлгерімін көрсеңіз болады.\nСоңғы рет төлеген күн: " + text, reply_markup=results_markup)
						break
				else:
					for i, user in enumerate(users_who_want_to_enroll_in_a_course):
						if user[0] == msg.from_user.id:
							if user[1] == None:
								data = db.get(user[2], "iin", ["iin", msg.text])
								print(data)
								if not data:
									users_who_want_to_enroll_in_a_course[i][1] = msg.text
									db.add(user[2], msg.text)
									await msg.answer(list(courses[user[2]]["answers"])[0])
								else:
									await msg.answer("Мұндай ЖСН(ИИН) бар оқушы бізде бар, басқа ЖСН(ИИН) жазыңыз.")
							else:
								for j, k in enumerate(courses[user[2]]["columns"]):
									data = db.get(user[2], k, ["iin", user[1]])[0][0]
									if not data:
										db.update(user[2], k, msg.text, ["iin", user[1]])
										try:
											await msg.answer(courses[user[2]]["answers"][j+1])
										except:
											if user[2] == "EHT_course":
												course = "ҰБТ-ға дайындық курсына"
											elif user[2] == "kids":
												course = "Kids курсына"
											else:
												course = "5, 6, 7 сынып оқушыларының курсына"

											text = course + f" жаңа оқушы тіркелді:\nИИН: {user[1]}\n"

											for n, m in enumerate(courses[user[2]]['columns']):
												data = db.get(user[2], m, ['iin', user[1]])[0][0]
												text += courses[user[2]]['names'][n] + ": " + data + "\n"

											await bot.send_message("838318362", text)
											await msg.answer("Сіз сәтті курсқа тіркелдіңіз.\nМенеджерден жауапты күтіңіз. Ертен сізге расписание жібереді")
											users_who_want_to_enroll_in_a_course[i][1] = "NONE"
											await cancel_cmd(msg)
										finally:
											break
							break
					else:
						await msg.answer("Мен бұл сообщениеге қалай жауап беретінімді білмеймін")

def Set(users, user_id):
	counter = 0
	for i, user in enumerate(users):
		if user[0] == user_id:
			counter += 1
	if counter > 1:
		for i, user in enumerate(users):
			if user[0] == user_id:
				counter -= 1
				del users[i]
				if counter == 1:
					break

def attendance_markup(admin, month):
	markup = InlineKeyboardMarkup()
	months = db.get("attendance", "*", ["iin", admin[1]])
	for i in months:
		i = list(i)
		if i[1] == month:
			for j in range(2, 12):
				if i[j] == None:
					i[j] = 0
			markup.add(InlineKeyboardButton(text=f"Общ. сабақ саны (Оқу сау.): {i[2]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:oc:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:oc:-1"))
			markup.add(InlineKeyboardButton(text=f"Сабаққа келді (Оқу сау.): {i[3]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:ocX:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:ocX:-1"))
			markup.add(InlineKeyboardButton(text=f"Общ. сабақ саны (Мат. сау.): {i[4]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:mc:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:mc:-1"))
			markup.add(InlineKeyboardButton(text=f"Сабаққа келді (Мат. сау.): {i[5]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:mcX:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:mcX:-1"))
			markup.add(InlineKeyboardButton(text=f"Общ. сабақ саны (Қ. тарих): {i[6]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:history:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:history:-1"))
			markup.add(InlineKeyboardButton(text=f"Сабаққа келді (Қ. тарих): {i[7]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:historyX:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:historyX:-1"))
			markup.add(InlineKeyboardButton(text=f"Общ. сабақ саны ({db.get(admin[2], 'ss1', ['iin', admin[1]])[0][0]}): {i[8]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:ss1:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:ss1:-1"))
			markup.add(InlineKeyboardButton(text=f"Сабаққа келді ({db.get(admin[2], 'ss1', ['iin', admin[1]])[0][0]}): {i[9]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:ss1X:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:ss1X:-1"))
			markup.add(InlineKeyboardButton(text=f"Общ. сабақ саны ({db.get(admin[2], 'ss2', ['iin', admin[1]])[0][0]}): {i[10]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:ss2:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:ss2:-1"))
			markup.add(InlineKeyboardButton(text=f"Сабаққа келді ({db.get(admin[2], 'ss2', ['iin', admin[1]])[0][0]}): {i[11]}", callback_data="nothing"))
			markup.add(InlineKeyboardButton(text=f"+1", callback_data=f"attendance:{month}:ss2X:+1"), InlineKeyboardButton(text=f"-1", callback_data=f"attendance:{month}:ss2X:-1"))
			return markup
	
@dp.callback_query_handler()
async def inline_echo(call: CallbackQuery):
	global users_who_want_to_enroll_in_a_course, users_who_want_to_see_student_results, admins

	if "lesson" in call.data:
		ID = int(str(call.data)[6:])
		course = db.get("courses", "*", ["id", ID])[0]
		with open(course[3], "rb") as src:
			if (course[3].lower().endswith(".mp4")):
				await bot.send_video(call.message.chat.id, src, caption=f'Курс: {course[2]}\n\nКурс туралы: {course[4]}', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Тіркелу", callback_data=f"enroll{ID}")]]))
			else:
				await bot.send_photo(call.message.chat.id, src.read(), caption = f'Курс: {course[2]}\n\nКурс туралы: {course[4]}', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Тіркелу", callback_data=f"enroll{ID}")]]))
		await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Курс туралы ақпарат:", reply_markup=None)
	elif "enroll" in call.data or "result" in call.data:
		ID = int(str(call.data)[6:])
		course = db.get("courses", "course_table_name", ["id", ID])[0][0]
		if "enroll" in call.data:
			users_who_want_to_enroll_in_a_course.append([call.message.chat.id, None, course])
			Set(users_who_want_to_enroll_in_a_course, call.message.chat.id)
		else:
			users_who_want_to_see_student_results.append([call.message.chat.id, None, course])
			Set(users_who_want_to_see_student_results, call.message.chat.id)
		await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
		await call.message.answer("Оқушының ЖСН(ИИН)-ін жазыңыз:", reply_markup=cancel_markup)
	elif call.data.startswith("history_of_tests;"):
		date = call.data.split(";")[1]
		for i, user in enumerate(users_who_want_to_see_student_results):
			if user[0] == call.message.chat.id:
				tests = db.get("tests", "*", ["iin", user[1]])

				for test in tests:
					if test[1] == date:
						# iin, passing date, mc, oc, history, ss1, ss2
						text = f"Тапсырды: {date}\n\nOқу сау.: {test[3]}/20\nМат. сау.: {test[2]}/15\nҚ. тарих: {test[4]}/15\n"
						text += f'{db.get(user[2], "ss1", ["iin", user[1]])[0][0]}: {test[5]}/45\n'
						text += f'{db.get(user[2], "ss2", ["iin", user[1]])[0][0]}: {test[6]}/45\n\n'
						text += f"Жалпы: {test[2]+test[3]+test[4]+test[5]+test[6]}/140"
						await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=None)
						break
	elif call.data.startswith("page_of_history_of_tests:"):
		start = int(call.data.split(":")[1])
		current = int(call.data.split(":")[2])
		
		if start == current:
			pass
		else:
			for i, user in enumerate(users_who_want_to_see_student_results):
				if user[0] == call.message.chat.id:
					tests = db.get("tests", "*", ["iin", user[1]])
					inline_markup = InlineKeyboardMarkup()

					for i in range(start, len(tests)):
						inline_markup.add(InlineKeyboardButton(text = tests[i][1]+f"; Жалпы балл: {tests[i][2]+tests[i][3]+tests[i][4]+tests[i][5]+tests[i][6]}", callback_data = f"history_of_tests;{tests[i][1]}"))

						if i == start + 9:
							break

					start_10 = start - 10
					if start_10 < 0:
						start_10 = 0

					inline_markup.add(
						InlineKeyboardButton(text = "◀️", callback_data = f"page_of_history_of_tests:{start_10}:{start}"),
						InlineKeyboardButton(text = "▶️", callback_data = f"page_of_history_of_tests:{start + 10}:{start}")
					)

					await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Тесты:", reply_markup=inline_markup)
	elif call.data.startswith("admin"):
		ID = int(str(call.data)[5:])
		course = db.get("courses", "course_table_name, course", ["id", ID])[0]
		admins.append([call.message.chat.id, None, course[0], None])
		Set(admins, call.message.chat.id)
		await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=course[1], reply_markup=None)
		await call.message.answer("Оқушының ЖСН(ИИН)-ін жазыңыз:", reply_markup=cancel_markup)
	elif call.data == "add_month":
		markup = InlineKeyboardMarkup()
		markup.add(InlineKeyboardButton(text="Қаңтар", callback_data="selected_month:Қаңтар"))
		markup.add(InlineKeyboardButton(text="Ақпан", callback_data="selected_month:Ақпан"))
		markup.add(InlineKeyboardButton(text="Наурыз", callback_data="selected_month:Наурыз"))
		markup.add(InlineKeyboardButton(text="Сәуір", callback_data="selected_month:Сәуір"))
		markup.add(InlineKeyboardButton(text="Мамыр", callback_data="selected_month:Мамыр"))
		markup.add(InlineKeyboardButton(text="Маусым", callback_data="selected_month:Маусым"))
		markup.add(InlineKeyboardButton(text="Шілде", callback_data="selected_month:Шілде"))
		markup.add(InlineKeyboardButton(text="Тамыз", callback_data="selected_month:Тамыз"))
		markup.add(InlineKeyboardButton(text="Қыркүйек", callback_data="selected_month:Қыркүйек"))
		markup.add(InlineKeyboardButton(text="Қазан", callback_data="selected_month:Қазан"))
		markup.add(InlineKeyboardButton(text="Қараша", callback_data="selected_month:Қараша"))
		markup.add(InlineKeyboardButton(text="Желтоқсан", callback_data="selected_month:Желтоқсан"))
		markup.add(InlineKeyboardButton(text="Бас тарту", callback_data="selected_month:Бас тарту"))
		await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Айды таңдаңыз", reply_markup=markup)
	elif call.data.startswith("selected_month"):
		for i, admin in enumerate(admins):
			if admin[0] == call.message.chat.id:
				month = str(call.data).split(":")[1]
				months = db.get("attendance", "month", ["iin", admin[1]])
				text = ""
				if month == "Бас тарту":
					text = "Бас тартылды"
				else:
					for i in months:
						if i[0] == month:
							text = "Мұндай ай уже бар"
							break
					else:
						db.add("attendance", [admin[1], month])
						text = "Орындалды"
				markup = InlineKeyboardMarkup()
				months = db.get("attendance", "month", ["iin", admin[1]])
				for month in months:
					markup.add(InlineKeyboardButton(text=month[0], callback_data=f"month:{month[0]}"))
				markup.add(InlineKeyboardButton(text="Ай қосу", callback_data="add_month"))
				await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)
				break
	elif call.data.startswith("month:"):
		for i, admin in enumerate(admins):
			if admin[0] == call.message.chat.id:
				await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=str(call.data)[6:], reply_markup=attendance_markup(admin, str(call.data)[6:]))
				break
	elif call.data.startswith("attendance:"):
		splitted_data = str(call.data).split(":")
		month = splitted_data[1]
		column = splitted_data[2]
		cmd = splitted_data[3]
		for i, admin in enumerate(admins):
			if admin[0] == call.message.chat.id:
				months = db.get("attendance", "*", ["iin", admin[1]])
				for i in months:
					if i[1] == month:
						items = ["oc", "ocX", "mc", "mcX", "history", "historyX", "ss1", "ss1X", "ss2", "ss2X"]
						current_count = i[items.index(column) + 2]
						if current_count == None:
							current_count = 0
						if cmd == "+1":
							db.update("attendance", column, current_count+1, [admin[1], month])
						else:
							if current_count-1 < 0:
								current_count = 0
							else:
								current_count -= 1
							db.update("attendance", column, current_count, [admin[1], month])
						break
				await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=attendance_markup(admin, month))
				break


if __name__ == "__main__": executor.start_polling(dp, skip_updates=True)