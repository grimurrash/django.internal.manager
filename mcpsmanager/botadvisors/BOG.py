import telebot
from telebot import types
from datetime import datetime

# '5734753752:AAFX3rxV6jkNyYz6qAs41pU1YYc4ED7T8ZM')
bot = telebot.TeleBot('5758448500:AAGVgOV4N7iBHIVVXgfHXMdg3MifKNLIkGc')


@bot.message_handler(commands=['start'])
def welcome(message):
    text = f"Здравствуйте, уважаемый кандидат на должность советника директора по воспитанию и взаимодействию с детскими общественными объединениями!\n\n" \
           f"Для участия в конкурсе Вам необходимо внести Ваши данные в этом чат-боте\n\n" \
           f"Для начала, пожалуйста,\n\n" \
           f"- ознакомьтесь с <a href='https://patriotsport.moscow/'>Положением о конкурсе</a>\n\n" \
           f"- дайте свое согласие на <a href='https://patriotsport.moscow/wp-content/uploads/2022/03/pril-3.pdf'>обработку и использование персональных данных</a>👇\n\n"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('С положением ознакомлен')
    markup.add(item1)
    bot.register_next_step_handler(message, get_patronymic)  # следующий шаг – функция get_surname

    with open('Patri.jpeg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=text, reply_markup=markup, parse_mode="HTML")


name = ''  # имя
surname = ''  # Фамилия
patronymic = ''  # Отчество
age = 0  # Возраст
day = 0
mon = 0
god = 0
gender = ''  # пол
user_photo = ''  # Фото человека
tel_number = ''  # телефон
social_networks = ''  # соц сети
education = ''  # образование
place_education = ''  # название вуз
place_education2 = ''  # направление подготовки
place_education_stop = ''  # окончание обучения
doc_education = ''  # документы образования
work_experience = ''  # опыт работы
work_experience_name = ''  # название организации где работает
job_title = ''  # должность
prof_skills = ''  # проф навыки
pers_qualities = ''  # лич качества
achievements = ''  # достижения
exp_children = ''  # опыт работы с детьми
ed_oo_work = ''  # образовательную организацию, в которой Вы планируете работать
adm_okr = ''  # адм округ
add_education = ''  # добавить обучение
add_work = ''  # добавить работу
email = ''
napr_education = ''  # направление образования


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == 'С положением ознакомлен':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item2 = types.KeyboardButton('Даю согласие на обработку и использование персональных данных')
        markup.add(item2)
        bot.send_message(message.from_user.id, "Дайте согласие на обработку и использование персональных данных👇",
                         reply_markup=markup)
    elif message.text == 'Даю согласие на обработку и использование персональных данных':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item3 = types.KeyboardButton('Правила заполнения')
        markup.add(item3)
        bot.send_message(
            message.from_user.id,
            "Спасибо!\n\n "
            "Прежде чем приступить к заполнению анкеты, подготовьте, пожалуйста, «сканы» или фото следующих документов в разборчивом виде:\n\n "
            "- документы об образовании (диплом (главный разворот), свидетельство о профессиональной переподготовке (при наличии))\n\n "
            "- вашу фотографию для анкеты\n\n"
            "Все документы необходимо будет загрузить в соответствующие поля чат-бота.\n\n"
            "Заполнение анкеты займет у Вас около 30 минут\n\n"
            "Нажмите кнопку «Правила заполнения», чтобы ознакомиться с правилами.\n\n",
            reply_markup=markup
        )

    elif message.text == 'Правила заполнения':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item4 = types.KeyboardButton('Все понятно')
        markup.add(item4)
        bot.send_message(message.from_user.id,
                         "Для заполнения анкеты Вам необходимо последовательно отвечать на вопросы и вводить Ваши данные в поле ответа на поступающие Вам сообщения в этот чат.\n\n"
                         "Обратите внимание, что ответы на некоторые вопросы ограничены по количеству знаков (это будет указано в самом вопросе).\n\n"
                         "При загрузке материалов и изображений обращайте внимание на необходимый формат файла.\n\n"
                         "Если при заполнении, вы обнаружите, что допустили ошибку или хотите изменить внесенную информацию, вы можете вернуться в какой-либо раздел, нажав на кнопку «меню» и выбрав соответствующий пункт. После внесения изменений необходимо нажать «Назад» для возврата.",
                         reply_markup=markup)



    elif message.text == 'Все понятно':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item5 = types.KeyboardButton('Старт')
        markup.add(item5)
        bot.send_message(message.from_user.id, 'Для начала нажмите "Старт"👇', reply_markup=markup)

    elif message.text == 'Старт':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Введите Вашу ФАМИЛИЮ", reply_markup=a)
        bot.register_next_step_handler(message, get_surname)  # следующий шаг – функция get_surname
    else:
        bot.send_message(message.from_user.id, "Произошла ошибка... \nНеобходимо начать опрос заново. \n Для этого введите /start", parse_mode="html")


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Введите Ваше ИМЯ')
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    global name
    global surname
    name = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item6 = types.KeyboardButton('Пропустить')
    markup.add(item6)
    bot.send_message(message.from_user.id, 'Введите Ваше ОТЧЕСТВО', reply_markup=markup)
    bot.register_next_step_handler(message, get_patronymic)


def get_patronymic(message):
    global patronymic
    patronymic = message.text
    a = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id,
                     "Укажите дату рождения (в формате 20.12.2000 (День.Месяц.Год))",
                     parse_mode="html", reply_markup=a)
    bot.register_next_step_handler(message, get_date_of_birth)


def get_date_of_birth(message):
    global age
    try:
        age = datetime.fromisoformat(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item7 = types.KeyboardButton('Мужской')
        item8 = types.KeyboardButton('Женский')
        markup.add(item7, item8)
        bot.send_message(message.from_user.id, 'Укажите Ваш пол', reply_markup=markup)
        bot.register_next_step_handler(message, get_gender)
    except Exception:
        bot.send_message(message.from_user.id, 'Неверный формат \nПример для заполнения: <b>20.12.2000 (День.Месяц.Год)</b>',
                         parse_mode="html")
        bot.register_next_step_handler(message, get_date_of_birth)


def get_day(message):
    global day
    try:
        day = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item7 = types.KeyboardButton('Мужской')
        item8 = types.KeyboardButton('Женский')
        markup.add(item7, item8)
        bot.send_message(message.from_user.id, 'Укажите Ваш пол', reply_markup=markup)
        bot.register_next_step_handler(message, get_gender)
    except Exception:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста \nПример для заполнения: <b>30122022</b>',
                         parse_mode="html")
        bot.register_next_step_handler(message, get_date_of_birth)


def get_gender(message):
    global gender
    gender = message.text
    if message.text == 'Женский':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Загрузите Вашу фотографию для анкеты", reply_markup=a)
        bot.register_next_step_handler(message, get_user_photo)
    elif message.text == 'Мужской':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Загрузите Вашу фотографию для анкеты", reply_markup=a)
        bot.register_next_step_handler(message, get_user_photo)
    else:
        bot.send_message(message.from_user.id, "Воспользуйтесь кнопками ⬇️")
        bot.register_next_step_handler(message, get_gender)
    # global gender;
    # gender = message.text;


@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    global user_photo
    user_photo = message.photo
    # bot.send_message(message.chat.id, 'Укажите Ваш номер телефона (без знаков и пробелов)', reply_markup=markup)
    # bot.register_next_step_handler(message, get_tel_number)
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)  # Подключаем клавиатуру
    button_phone = types.KeyboardButton(text="Отправить телефон",
                                        request_contact=True)  # Указываем название кнопки, которая появится у пользователя
    markup.add(button_phone)  # Добавляем эту кнопку
    bot.send_message(message.chat.id,
                     'Укажите Ваш номер телефона (без знаков и пробелов)\n\nИли нажмите кнопку <b>"Отправить телефон"</b>',
                     parse_mode="html", reply_markup=markup)
    bot.register_next_step_handler(message, get_tel_number)


@bot.message_handler(commands=['number'])  # Объявили ветку для работы по команде <strong>number</strong>
def get_tel_number(message):
    global tel_number
    tel_number = message.text
    a = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Укажите Ваш Email адрес', reply_markup=a)  # reply_markup=markup)
    bot.register_next_step_handler(message, get_email)


@bot.message_handler(content_types=['text'])
def get_email(message):
    global email
    email = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item9 = types.KeyboardButton('Пропустить')
    markup.add(item9)
    bot.send_message(message.chat.id,
                     'Укажите ссылку на ОСНОВНУЮ личную страницу в социальной сети (VK, Одноклассники и др). При отсутствии, нажмите кнопку «Пропустить»',
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_social_networks)


@bot.message_handler(content_types=['text'])
def get_social_networks(message):
    global social_networks
    social_networks = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item10 = types.KeyboardButton('Высшее (бакалавриат)')
    item11 = types.KeyboardButton('Высшее (специалитет)')
    item12 = types.KeyboardButton('Высшее (магистратура)')
    item13 = types.KeyboardButton('Аспирантура')
    item14 = types.KeyboardButton('Неоконченное высшее (выпускной курс)')
    markup.add(item10, item11, item12, item13, item14)
    bot.send_message(message.chat.id, 'Укажите уровень Вашего образования', reply_markup=markup)
    bot.register_next_step_handler(message, get_education)


@bot.message_handler(content_types=['text'])
def get_education(message):
    global education
    education = message.text
    if message.text == 'Высшее (бакалавриат)':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item10 = types.KeyboardButton('Высшее (бакалавриат)')
        item11 = types.KeyboardButton('Высшее (специалитет)')
        item12 = types.KeyboardButton('Высшее (магистратура)')
        item13 = types.KeyboardButton('Аспирантура')
        item14 = types.KeyboardButton('Неоконченное высшее (выпускной курс по педагогическому направлению)')
        item15 = types.KeyboardButton('Курсы профессиональной переподготовки/ повышения квалификации')
        item16 = types.KeyboardButton('Среднее профессиональное образование')
        markup.add(item10, item11, item12, item13, item14, item15, item16)
        bot.send_message(message.chat.id,
                         'Выберите последнюю полученную Вами форму образования, по педагогическому профилю',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_place_education)
    elif message.text == 'Высшее (специалитет)':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item10 = types.KeyboardButton('Высшее (бакалавриат)')
        item11 = types.KeyboardButton('Высшее (специалитет)')
        item12 = types.KeyboardButton('Высшее (магистратура)')
        item13 = types.KeyboardButton('Аспирантура')
        item14 = types.KeyboardButton('Неоконченное высшее (выпускной курс по педагогическому направлению)')
        item15 = types.KeyboardButton('Курсы профессиональной переподготовки/ повышения квалификации')
        item16 = types.KeyboardButton('Среднее профессиональное образование')
        markup.add(item10, item11, item12, item13, item14, item15, item16)
        bot.send_message(message.chat.id,
                         'Выберите последнюю полученную Вами форму образования, по педагогическому профилю',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_place_education)
    elif message.text == 'Высшее (магистратура)':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item10 = types.KeyboardButton('Высшее (бакалавриат)')
        item11 = types.KeyboardButton('Высшее (специалитет)')
        item12 = types.KeyboardButton('Высшее (магистратура)')
        item13 = types.KeyboardButton('Аспирантура')
        item14 = types.KeyboardButton('Неоконченное высшее (выпускной курс по педагогическому направлению)')
        item15 = types.KeyboardButton('Курсы профессиональной переподготовки/ повышения квалификации')
        item16 = types.KeyboardButton('Среднее профессиональное образование')
        markup.add(item10, item11, item12, item13, item14, item15, item16)
        bot.send_message(message.chat.id,
                         'Выберите последнюю полученную Вами форму образования, по педагогическому профилю',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_place_education)
    elif message.text == 'Аспирантура':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item10 = types.KeyboardButton('Высшее (бакалавриат)')
        item11 = types.KeyboardButton('Высшее (специалитет)')
        item12 = types.KeyboardButton('Высшее (магистратура)')
        item13 = types.KeyboardButton('Аспирантура')
        item14 = types.KeyboardButton('Неоконченное высшее (выпускной курс по педагогическому направлению)')
        item15 = types.KeyboardButton('Курсы профессиональной переподготовки/ повышения квалификации')
        item16 = types.KeyboardButton('Среднее профессиональное образование')
        markup.add(item10, item11, item12, item13, item14, item15, item16)
        bot.send_message(message.chat.id,
                         'Выберите последнюю полученную Вами форму образования, по педагогическому профилю',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_place_education)
    elif message.text == 'Неоконченное высшее (выпускной курс)':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item10 = types.KeyboardButton('Высшее (бакалавриат)')
        item11 = types.KeyboardButton('Высшее (специалитет)')
        item12 = types.KeyboardButton('Высшее (магистратура)')
        item13 = types.KeyboardButton('Аспирантура')
        item14 = types.KeyboardButton('Неоконченное высшее (выпускной курс по педагогическому направлению)')
        item15 = types.KeyboardButton('Курсы профессиональной переподготовки/ повышения квалификации')
        item16 = types.KeyboardButton('Среднее профессиональное образование')
        markup.add(item10, item11, item12, item13, item14, item15, item16)
        bot.send_message(message.chat.id,
                         'Выберите последнюю полученную Вами форму образования, по педагогическому профилю',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_place_education)
    else:
        bot.send_message(message.from_user.id, "Воспользуйтесь кнопками ⬇️")


@bot.message_handler(content_types=['text'])
def get_place_education(message):
    global education
    education = message.text
    if message.text == 'Высшее (бакалавриат)':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Высшее (специалитет)':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Высшее (магистратура)':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Аспирантура':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Неоконченное высшее (выпускной курс по педагогическому направлению)':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Среднее профессиональное образование':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Курсы профессиональной переподготовки/ повышения квалификации':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)


@bot.message_handler(content_types=['text'])
def get_place_education2(message):
    global place_education2
    place_education2 = message.text
    bot.send_message(message.from_user.id, "Введите направление подготовки/специальности")
    bot.register_next_step_handler(message, get_napr_education)


def get_napr_education(message):
    global napr_education
    napr_education = message.text
    bot.send_message(message.from_user.id, "Укажите год окончания")
    bot.register_next_step_handler(message, get_place_education_stop)


def get_place_education_stop(message):
    global place_education_stop
    place_education_stop = message.text
    bot.send_message(message.from_user.id,
                     "Загрузите документы об образовании (без приложения) и повышении квалификации (формат PDF)")
    bot.register_next_step_handler(message, get_doc_education)


@bot.message_handler(content_types=['photo'])
def get_doc_education(message):
    global doc_education
    doc_education = message.photo
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item7 = types.KeyboardButton('Добавить место обучения')
    item8 = types.KeyboardButton('Продолжить')
    markup.add(item7, item8)
    bot.send_message(message.from_user.id, "Добавить еще место обучения?", reply_markup=markup)
    bot.register_next_step_handler(message, get_add_education)


@bot.message_handler(content_types=['text'])
def get_add_education(message):
    global add_education
    add_education = message.text
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # item7 = types.KeyboardButton('Добавить место обучения')
    # item8 = types.KeyboardButton('Продолжить')
    # markup.add(item7, item8)
    if message.text == 'Добавить место обучения':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Укажите информацию обо всех учебных соведениях (СПО, ВО), где Вы обучались, начиная с последнего \n\n В данной графе 👇 введите название последнего учебного заведения',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_place_education2)
    elif message.text == 'Продолжить':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Укажите опыт Вашей трудовой деятельности за последние 5 лет. В данной графе👇 укажите название организации, являющейся вашим последним или текущим местом работы',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_work_experience)
    else:
        bot.send_message(message.from_user.id, "Воспользуйтесь кнопками ⬇️")


@bot.message_handler(content_types=['text'])
def get_work_experience(message):
    global work_experience
    work_experience = message.text
    bot.send_message(message.from_user.id, 'Укажите вашу должность')
    bot.register_next_step_handler(message, get_job_title)


def get_job_title(message):
    global job_title
    job_title = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item7 = types.KeyboardButton('Добавить место работы')
    item8 = types.KeyboardButton('Продолжить')
    markup.add(item7, item8)
    bot.send_message(message.from_user.id, 'Хотите добавить место работы?', parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, get_add_work)


def get_add_work(message):
    global add_work
    add_work = message.text
    if message.text == 'Добавить место работы':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Укажите опыт Вашей трудовой деятельности за последние 5 лет. В данной графе👇 укажите название организации, являющейся вашим последним или текущим местом работы',
                         reply_markup=a)
        bot.register_next_step_handler(message, get_work_experience)
    elif message.text == 'Продолжить':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Перечислите Ваши профессиональные навыки (пример: организация мероприятий, проведение уроков, написание текстов и тд) (до 500 знаков)',
                         parse_mode='html', reply_markup=a)
        bot.register_next_step_handler(message, get_prof_skills)
    else:
        bot.send_message(message.from_user.id, "Воспользуйтесь кнопками ⬇️")


def get_prof_skills(message):
    global prof_skills
    prof_skills = message.text
    bot.send_message(message.from_user.id,
                     'Перечислите Ваши личностные качества <i>(пример: коммуникабельность, стрессоустойчивость и тд) (до 500 знаков)</i>',
                     parse_mode='html')
    bot.register_next_step_handler(message, get_pers_qualities)


def get_pers_qualities(message):
    global pers_qualities
    pers_qualities = message.text
    bot.send_message(message.from_user.id,
                     'Укажите информацию о ваших достижениях (перечень опубликованных статей, реализованных проектов, победы в конкурсах, полученных грантов). Прикрепите ссылки на описания проектов/публикаций (при наличии) До 1500 знаков')
    bot.register_next_step_handler(message, get_achievements)


def get_achievements(message):
    global achievements
    achievements = message.text
    bot.send_message(message.from_user.id,
                     'Опишите опыт работы с детским коллективом (вожатская, волонтерская, преподавательская и иная деятельность) До 1500 знаков')
    bot.register_next_step_handler(message, get_exp_children)


def get_exp_children(message):
    global exp_children
    exp_children = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item20 = types.KeyboardButton('Пропустить')
    markup.add(item20)
    bot.send_message(message.from_user.id,
                     'Пожалуйста, укажите образовательную организацию, в которой Вы планируете работать Советником (одна ОО) или нажмите «Пропустить»',
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_ed_oo_work)


def get_ed_oo_work(message):
    global ed_oo_work
    ed_oo_work = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item21 = types.KeyboardButton('ЦАО')
    item22 = types.KeyboardButton('СВАО')
    item23 = types.KeyboardButton('ВАО')
    item24 = types.KeyboardButton('ЮВАО')
    item25 = types.KeyboardButton('ЗАО')
    item26 = types.KeyboardButton('СЗАО')
    item27 = types.KeyboardButton('ЮЗАО')
    item28 = types.KeyboardButton('ЮАО')
    item29 = types.KeyboardButton('САО')
    item30 = types.KeyboardButton('ЗелАО')
    item31 = types.KeyboardButton('ТиНАО')
    markup.add(item21, item23, item24, item25, item26, item27, item28, item29, item30, item31, item22)
    bot.send_message(message.from_user.id,
                     "Пожалуйста, выберите административный(е) округ(а), в котором(ых) Вы хотели бы работать Советником",
                     reply_markup=markup)
    bot.register_next_step_handler(message, get_adm_okr)


def get_adm_okr(message):
    global adm_okr
    adm_okr = message.text
    if message.text == 'ЦАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'СВАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ВАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ЮВАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'СЗАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ЮЗАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ЗАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ЮАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'САО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ЗелАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    elif message.text == 'ТиНАО':
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).',
                         reply_markup=a)
    else:
        bot.send_message(message.from_user.id, "Воспользуйтесь кнопками ⬇️")


#    bot.register_next_step_handler(message, get_stop_reg)

# def get_stop_reg(message):
#     global stop_reg
#     stop_reg = message.text
#     if message.text == ('ЦАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('СВАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ВАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ЮВАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('СЗАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ЮЗАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ЗАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ЮАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('САО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ЗелАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     elif message.text == ('ТиНАО'):
#       bot.send_message(message.from_user.id, 'Спасибо! Ваши данные отправлены на модерацию. Теперь Вам доступно прохождение теста. Обратите внимание, тест необходимо пройти до (дата окончания прохождения теста).')
#     else:
#         bot.send_message(message.from_user.id, "Воспользуйтесь кнопками ⬇️")
#     # if message.text == ('ЗАО' or 'САО' or 'ЮЗАО' or 'ЦАО')
#    # bot.register_next_step_handler(message, get_ed_oo_work)


bot.polling(non_stop=True)
