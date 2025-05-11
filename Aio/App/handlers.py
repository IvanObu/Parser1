from gc import callbacks
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, FSInputFile
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from Db.main_db import find_products_by_params, add_to_my_list, is_in_my_list, get_my_list
from Graphics.main_graphic import generate_price_graph

import sqlite3

import Aio.App.keyboards as kb

route = Router()

class Reg(StatesGroup):
    name = State()
    number = State()

class FilterFSM(StatesGroup):
    choosing_series = State()
    choosing_model = State()
    choosing_memory = State()
    choosing_color = State()
    waiting_for_search_text = State()

class FilterMFSM(StatesGroup):
    choosing_series = State()
    choosing_model = State()
    choosing_cpu = State()
    choosing_ram = State()
    choosing_storage = State()
    choosing_color = State()
    waiting_for_search_text = State()

class ProfileStates(StatesGroup):
    changing_name = State()

async def is_user_registered(user_id: int, conn: sqlite3.Connection) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM User WHERE rowid = ?", (user_id,))
    return cursor.fetchone() is not None

async def update_user_name(user_id: int, name: str, conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO User (rowid, Name) VALUES (?, ?)", (user_id, name))
    conn.commit()

@route.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    with sqlite3.connect("Db/products.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Name FROM User WHERE Us_Id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.execute("INSERT INTO User (Us_Id, Name) VALUES (?, ?)", (user_id, user_name))
            conn.commit()
            name = user_name
        else:
            name = user[0]
        if name:
            await message.answer(
                f"🖐 Welcome back, {name}!",
                reply_markup=kb.main_kb
            )
        else:
            await message.answer(
                "👋 Welcome! Use /reg command to register.",
                reply_markup=kb.main_kb
            )

@route.message(Command("reg"))
async def cmd_reg(message: Message, state: FSMContext):
    with sqlite3.connect("Db/products.db") as conn:
        if await is_user_registered(message.from_user.id, conn):
            cursor = conn.cursor()
            cursor.execute("SELECT Name FROM User WHERE rowid = ?", (message.from_user.id,))
            name = cursor.fetchone()[0]
            await message.answer(
                f"You're already registered as {name}.\n"
                "You can change your name in settings.",
                reply_markup=kb.main_kb
            )
        else:
            await message.answer(
                "📝 Please enter your name:",
                reply_markup=kb.cancel_kb
            )
            await state.set_state(ProfileStates.changing_name)

@route.message(F.text == "⚙️ Settings")
async def settings_menu(message: Message):
    await message.answer(
        "⚙️ Settings menu:",
        reply_markup=kb.settings_kb
    )

@route.message(F.text == "✏️ Смена имени")
async def start_change_name(message: Message, state: FSMContext):
    await message.answer(
        "📝 Enter new name:",
        reply_markup=kb.cancel_kb
    )
    await state.set_state(ProfileStates.changing_name)

@route.message(ProfileStates.changing_name, F.text)
async def process_name(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Action canceled", reply_markup=kb.main_kb)
        return

    if len(message.text) > 100:
        await message.answer("Name too long (max 100 chars)")
        return

    with sqlite3.connect("Db/products.db") as conn:
        await update_user_name(message.from_user.id, message.text, conn)
        await message.answer(
            f"✅ Имя изменено на: {message.text}",
            reply_markup=kb.main_kb
        )
    await state.clear()

@route.message(F.text == "️↩️ Назад")
async def back_to_main(message: Message):
    await message.answer(
        "Main menu:",
        reply_markup=kb.main_kb
    )

@route.message(F.text == "🔎 Search")
async def start_search(message: Message):
    await message.answer("Search 🔎", reply_markup=kb.ReplyKeyboardRemove())
    await message.answer("choose category:", reply_markup=kb.search_kb)

@route.message(F.text == "📘 Instruction")
async def instruction_handler(message: Message):
    await message.answer(
        text="📖 Инструкция по использованию бота...\n[Описание]:",
        reply_markup=kb.back
    )

@route.callback_query(F.data == "back_main")
async def back_main_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main_kb)
    await callback.answer()

@route.message(F.text == "📦 About shops")
async def about_stores_handler(message: Message):
    await message.answer("🏬 Описание магазинов:\n[Здесь информация]", reply_markup=kb.back)

@route.message(F.text == "📁 Make exel file")
async def send_excel_file(message: Message):
    try:

        file_path = "Db/apple_products.xlsx"
        file = FSInputFile(file_path, filename="Отчет.xlsx")
        await message.answer_document(
            document=file,
            caption="Ваш Excel-файл с данными 📊"
        )
    except FileNotFoundError:
        await message.answer("Файл не найден 😢")
    except Exception as e:
        await message.answer(f"Произошла ошибка")

@route.message(F.text == "⚙️ Settings")
async def start_search(message: Message):
    await message.answer("Search 🔎", reply_markup=kb.ReplyKeyboardRemove())
    await message.answer("choose category:", reply_markup=kb.search_kb)

@route.message(Command("help"))
async def cmd_start(message: Message):
    await message.answer(
        text="📖 Инструкция по использованию бота...\n[Описание]:",
        reply_markup=kb.back
    )



@route.callback_query( F.data== "back_main")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main_kb)
    await callback.answer()

@route.callback_query( F.data== "end_search")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main_kb)
    await callback.answer()

@route.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer("Enter your number:")

@route.callback_query(F.data == "device_iphone")
async def handle_device_iphone(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Выберите серию iPhone:", reply_markup=kb.get_series_kb())
    await state.set_state(FilterFSM.choosing_series)

@route.callback_query(F.data.startswith("series_"))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    series = callback.data.split("_", 1)[1]
    await state.update_data(series=series)
    await callback.message.edit_text("Выберите модель:", reply_markup=kb.get_model_kb(series))
    await state.set_state(FilterFSM.choosing_model)

@route.callback_query(F.data.startswith("model_"))
async def choose_memory(callback: CallbackQuery, state: FSMContext):
    model = callback.data.split("_", 1)[1]
    data = await state.get_data()
    series = data["series"]
    await state.update_data(model=model)
    await callback.message.edit_text("Выберите объем памяти:", reply_markup=kb.get_memory_kb(series, model))
    await state.set_state(FilterFSM.choosing_memory)

@route.callback_query(F.data.startswith("memory_"))
async def choose_color(callback: CallbackQuery, state: FSMContext):
    memory = callback.data.split("_", 1)[1]
    data = await state.get_data()
    series = data["series"]
    model = data["model"]
    await state.update_data(memory=memory)
    await callback.message.edit_text("Выберите цвет:", reply_markup=kb.get_color_kb(series, model))
    await state.set_state(FilterFSM.choosing_color)

@route.callback_query(F.data.startswith("color_"))
async def confirm_selection(callback: CallbackQuery, state: FSMContext):
    color = callback.data.split("_", 1)[1]
    await state.update_data(color=color)
    await callback.message.edit_text("Подтвердите выбор:", reply_markup=kb.confirm_selection_kb)

@route.callback_query(F.data == "c_finish")
async def finish_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    model = data["model"]
    memory = data["memory"]
    color = data["color"]

    await callback.message.edit_reply_markup()
    await callback.message.answer(
        f"✅ Вы выбрали:\n📱 iPhone {model}\n💾 Память: {memory}\n🎨 Цвет: {color}"
    )

    filters = {
        "model": model,
        "memory": memory,
        "color": color
    }
    conn = sqlite3.connect("Db/products.db")
    products = find_products_by_params(category="iPhone", filters=filters, conn=conn)

    if not products:
        await callback.message.answer("❌ Товары по заданным параметрам не найдены.", reply_markup=kb.search_kb)
    else:
        for product in products:
            await show_product(callback, product)
        await callback.message.answer("🔍 Завершить поиск", reply_markup=kb.end_search_kb)
    conn.close()
    await state.clear()


@route.callback_query(F.data == "device_mac")
async def handle_device_mac(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Выберите серию MacBook:", reply_markup=kb.get_mac_series_kb())
    await state.set_state(FilterMFSM.choosing_series)


@route.callback_query(F.data.startswith("mac_series_"))
async def choose_mac_model(callback: CallbackQuery, state: FSMContext):
    series = callback.data.split("_", 2)[2]
    await state.update_data(series=series)
    await callback.message.edit_text("Выберите модель:", reply_markup=kb.get_mac_model_kb(series))
    await state.set_state(FilterMFSM.choosing_model)


@route.callback_query(F.data.startswith("mac_model_"))
async def choose_mac_cpu(callback: CallbackQuery, state: FSMContext):
    model = callback.data.split("_", 2)[2]
    data = await state.get_data()
    series = data["series"]
    await state.update_data(model=model)
    await callback.message.edit_text("Выберите процессор:", reply_markup=kb.get_mac_cpu_kb(series, model))
    await state.set_state(FilterMFSM.choosing_cpu)


@route.callback_query(F.data.startswith("mac_cpu_"))
async def choose_mac_ram(callback: CallbackQuery, state: FSMContext):
    cpu = callback.data.split("_", 2)[2]
    data = await state.get_data()
    series = data["series"]
    model = data["model"]
    await state.update_data(cpu=cpu)
    await callback.message.edit_text("Выберите объем ОЗУ:", reply_markup=kb.get_mac_ram_kb(series, model))
    await state.set_state(FilterMFSM.choosing_ram)


@route.callback_query(F.data.startswith("mac_ram_"))
async def choose_mac_storage(callback: CallbackQuery, state: FSMContext):
    ram = callback.data.split("_", 2)[2]
    data = await state.get_data()
    series = data["series"]
    model = data["model"]
    await state.update_data(ram=ram)
    await callback.message.edit_text("Выберите объем памяти:", reply_markup=kb.get_mac_storage_kb(series, model))
    await state.set_state(FilterMFSM.choosing_storage)


@route.callback_query(F.data.startswith("mac_storage_"))
async def choose_mac_color(callback: CallbackQuery, state: FSMContext):
    storage = callback.data.split("_", 2)[2]
    data = await state.get_data()
    series = data["series"]
    model = data["model"]
    await state.update_data(storage=storage)
    await callback.message.edit_text("Выберите цвет:", reply_markup=kb.get_mac_color_kb(series, model))
    await state.set_state(FilterMFSM.choosing_color)


@route.callback_query(F.data.startswith("mac_color_"))
async def confirm_mac_selection(callback: CallbackQuery, state: FSMContext):
    color = callback.data.split("_", 2)[2]
    await state.update_data(color=color)
    data = await state.get_data()

    await callback.message.edit_text(
        f"✅ Проверьте выбранный MacBook:\n\n"
        f"Серия: {data['series']}\n"
        f"Модель: {data['model']}\n"
        f"Процессор: {data['cpu']}\n"
        f"ОЗУ: {data['ram']}\n"
        f"Память: {data['storage']}\n"
        f"Цвет: {color}\n\n"
        "Подтвердите выбор:",
        reply_markup=kb.confirm_mac_selection_kb()
    )


@route.callback_query(F.data == "c_finish_mac")
async def finish_mac_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.message.edit_reply_markup()
    await callback.message.answer(
        f"✅ Вы выбрали MacBook:\n"
        f"💻 {data['series']} {data['model']}\n"
        f"⚡ Процессор: {data['cpu']}\n"
        f"🧠 ОЗУ: {data['ram']}\n"
        f"💾 Память: {data['storage']}\n"
        f"🎨 Цвет: {data['color']}",
    )

    filters = {
        "series": data["series"],
        "model": data["model"],
        "cpu": data["cpu"],
        "ram": data["ram"],
        "storage": data["storage"],
        "color": data["color"]
    }
    conn = sqlite3.connect("Db/products.db")
    products = find_products_by_params(category="Mac", filters=filters, conn=conn)

    if not products:
        await callback.message.answer("❌ Товары по заданным параметрам не найдены.", reply_markup=kb.search_kb)
    else:
        for product in products:
            await show_product(callback, product)
        await callback.message.answer("🔍 Завершить поиск", reply_markup=kb.end_search_kb)
    conn.close()
    await state.clear()


async def show_product(callback, product):
    text = (
        f"🏬 Магазин: {product['store']}\n"
        f"💰 Цена: {product['price']} ₽"
    )
    conn = sqlite3.connect("Db/products.db")
    in_list = is_in_my_list(product["product_id"], conn)

    if in_list:
        button = InlineKeyboardButton(text="✅ В списке", callback_data="none")
    else:
        button = InlineKeyboardButton(text="➕ В мой список", callback_data=f"add_{product['product_id']}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

    await callback.message.answer(text, reply_markup=keyboard)


@route.callback_query(F.data.startswith("add_"))
async def handle_add_to_my_list(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    conn = sqlite3.connect("Db/products.db")
    add_to_my_list(product_id, conn)
    await callback.answer(text="✅ Добавлено в мой список", show_alert=False)

    new_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ В списке", callback_data="none")]
        ]
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    except:
        pass


# Глобальный словарь для временного хранения удаляемых товаров
pending_changes = {}

@route.callback_query(F.data == "my_list")
async def show_my_list_handler(callback: CallbackQuery):
    conn = sqlite3.connect("Db/products.db")
    try:
        products = await get_my_list(conn)

        if not products:
            await callback.message.answer("Ваш список пуст", reply_markup=kb.main_kb)
            return

        pending_changes.pop(callback.from_user.id, None)

        await callback.message.answer("\n📋 Ваш список товаров:", reply_markup=kb.main_kb)

        for product in products:
            message_text = (
                f"📌 {product['model']}\n"
                f"🏷 Цена: {product['price']} ₽\n"
                f"🛒 Магазин: {product['store']}\n"
                f"📅 Обновлено: {product['price_date']}"
            )

            # Определяем иконку в зависимости от статуса уведомлений
            notice_icon = "🔔" if product['notice_status'] == 1 else "🔕"

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌ Удалить",
                            callback_data=f"mark_remove_{product['id']}"
                        ),
                        InlineKeyboardButton(
                            text=f"{notice_icon} Уведомления",
                            callback_data=f"notify_{product['id']}"
                        ),
                        InlineKeyboardButton(
                            text="📈 История цен",
                            callback_data=f"graph_{product['id']}"
                        )
                    ]
                ]
            )

            await callback.message.answer(message_text, reply_markup=keyboard)

        confirm_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Принять изменения", callback_data="confirm_changes")],
                [InlineKeyboardButton(text="🔍 Завершить поиск", callback_data="end_search")]
            ]
        )

        await callback.message.answer("Подтвердите изменения:", reply_markup=confirm_keyboard)

    except Exception as e:
        await callback.message.answer("Произошла ошибка при загрузке списка")
    finally:
        conn.close()
    await callback.answer()


@route.callback_query(F.data.startswith("mark_remove_"))
async def mark_for_removal_handler(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id

        if user_id not in pending_changes:
            pending_changes[user_id] = {"to_remove": set(), "to_restore": set()}

        pending_changes[user_id]["to_remove"].add(product_id)
        pending_changes[user_id]["to_restore"].discard(product_id)

        new_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⚠️ Будет удалено",
                        callback_data="none"
                    ),
                    InlineKeyboardButton(
                        text="↩️ Отменить",
                        callback_data=f"unmark_remove_{product_id}"
                    )
                ]
            ]
        )

        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
        await callback.answer("Товар отмечен для удаления (изменения применятся после подтверждения)")

    except Exception as e:
        await callback.answer("Ошибка при отметке товара", show_alert=True)


@route.callback_query(F.data.startswith("unmark_remove_"))
async def unmark_removal_handler(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id

        if user_id in pending_changes:
            pending_changes[user_id]["to_remove"].discard(product_id)

        new_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Удалить",
                        callback_data=f"mark_remove_{product_id}"
                    ),
                    InlineKeyboardButton(
                        text="🔔 Уведомления",
                        callback_data=f"notify_{product_id}"
                    ),
                    InlineKeyboardButton(
                        text="📈 Истоиря цен",
                        callback_data=f"graph_{product_id}"
                    )
                ]
            ]
        )

        await callback.message.edit_reply_markup(reply_markup=new_keyboard)
        await callback.answer("Удаление товара отменено")

    except Exception as e:
        await callback.answer("Ошибка при отмене удаления", show_alert=True)


@route.callback_query(F.data == "confirm_changes")
async def confirm_changes_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        if user_id in pending_changes and (
                pending_changes[user_id]["to_remove"] or pending_changes[user_id]["to_restore"]):
            with sqlite3.connect("Db/products.db") as conn:
                cursor = conn.cursor()

                for product_id in pending_changes[user_id]["to_remove"]:
                    cursor.execute("DELETE FROM my_list WHERE product_id = ?", (product_id,))

                for product_id in pending_changes[user_id]["to_restore"]:
                    cursor.execute("INSERT OR IGNORE INTO my_list (product_id) VALUES (?)", (product_id,))

                conn.commit()

            await callback.answer("Изменения успешно применены", show_alert=True)

            await callback.message.delete()

            await show_my_list_handler(callback)
        else:
            await callback.answer("Нет изменений для применения", show_alert=True)

    except Exception as e:
        await callback.answer("Ошибка при применении изменений", show_alert=True)
    finally:
        pending_changes.pop(user_id, None)


@route.callback_query(F.data == "cancel_changes")
async def cancel_changes_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    pending_changes.pop(user_id, None)
    await callback.answer("Изменения отменены", show_alert=True)
    await callback.message.delete()
    await show_my_list_handler(callback)


@route.callback_query(F.data == "end_search")
async def end_search_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    pending_changes.pop(user_id, None)
    await callback.message.answer("Поиск завершен", reply_markup=kb.main_kb)
    await callback.answer()

@route.callback_query(F.data.startswith("graph_"))
async def show_price_graph_handler(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[1])

        with sqlite3.connect("Db/products.db") as conn:
            graph_img, caption = generate_price_graph(conn, product_id)

            if graph_img is None:
                await callback.answer(caption, show_alert=True)
                return

            # Отправляем график без кнопки обновления
            await callback.message.answer_photo(
                BufferedInputFile(
                    graph_img.getvalue(),
                    filename="price_graph.png"
                ),
                caption=caption,
                parse_mode="HTML"
            )
            await callback.answer()

    except Exception as e:
        await callback.answer("Произошла ошибка при построении графика", show_alert=True)


@route.callback_query(F.data.startswith("notify_"))
async def toggle_notifications(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[1])

        with sqlite3.connect("Db/products.db") as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT Notice FROM my_list WHERE product_id = ?", (product_id,))
            result = cursor.fetchone()

            if not result:
                await callback.answer("Товар не найден в вашем списке", show_alert=True)
                return

            current_status = result[0]
            new_status = 1 if current_status == 0 else 0

            cursor.execute("UPDATE my_list SET Notice = ? WHERE product_id = ?", (new_status, product_id))
            conn.commit()

            notice_icon = "🔔" if new_status == 1 else "🔕"

            new_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="❌ Удалить", callback_data=f"mark_remove_{product_id}"),
                        InlineKeyboardButton(text=f"{notice_icon} Уведомления", callback_data=f"notify_{product_id}"),
                        InlineKeyboardButton(text="📈 История цен", callback_data=f"graph_{product_id}")
                    ]
                ]
            )

            await callback.message.edit_reply_markup(reply_markup=new_keyboard)
            status_text = "включены" if new_status == 1 else "отключены"
            await callback.answer(f"Уведомления {status_text}")

    except Exception as e:
        await callback.answer(f"Ошибка при изменении настроек уведомлений {e}", show_alert=True)

@route.message(F.text == "⏱ Интервал обновления")
async def select_interval(message: Message):
    await message.answer(
        "Выберите интервал обновления:",
        reply_markup=kb.get_interval_kb()
    )


@route.message(F.text.regexp(r'^\d+ дней$'))
async def set_interval(message: Message):
    try:
        days = int(message.text.split()[0])

        with sqlite3.connect("Db/products.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO Settings (id, update_interval_days)
                VALUES (1, ?)
            """, (days,))
            conn.commit()

        await message.answer(
            f"✅ Интервал обновления изменен на {days} дней",
            reply_markup=kb.settings_kb
        )

    except Exception as e:
        await message.answer(
            "❌ Ошибка при изменении интервала",
            reply_markup=kb.settings_kb
        )