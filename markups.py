from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_keyboard_markup(buttons):
	markup = ReplyKeyboardMarkup(resize_keyboard=True)
	for i in range(len(buttons) // 2):
		markup.add(KeyboardButton(buttons[i + i]), KeyboardButton(buttons[i + i + 1]))
	for i in range(len(buttons) % 2):
		markup.add(KeyboardButton(buttons[len(buttons) - 1]))
	return markup

starting_markup = get_keyboard_markup(["Біз туралы", "Курсқа тіркелу", "Оқушының оқу үлгерімін көру", "Акциялар, жеңілдіктер", "ҰБТ нұсқаларын тегін алу", "Алдыңғы жылғы результаттар", "Біздің әлеуметтік желілеріміз", "Менеджермен хабарласу"])
cancel_markup = get_keyboard_markup(["Бас тарту"])
results_markup = get_keyboard_markup(["Тесттер", "Посещаемость", "Мұғалімдердің шағымдары"])
results_markup.add(KeyboardButton("Басты бетке оралу"))
admin_markup = get_keyboard_markup(['"Активность" статусын өзгерту', "Шағым қалдыру", "Соңғы рет жасалған төлем", "Тест жауаптарын енгізу", "Посещаемость", "Excel-ге шығару", "Басқа оқушы таңдау", "Админ режимнен шығу"])