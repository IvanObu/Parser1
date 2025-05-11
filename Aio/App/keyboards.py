import json
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder

from Db.main_db import IPHONES, MacBooks


def load_iphones_from_json(filename="Db/iphones.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Преобразуем списки обратно в множества
    for series in data:
        data[series]["models"] = set(data[series]["models"])
        data[series]["memory"] = {model: set(mem) for model, mem in data[series]["memory"].items()}
        data[series]["colors"] = {model: set(colors) for model, colors in data[series]["colors"].items()}

    return data

IPHONES = load_iphones_from_json()

def load_macbooks_from_json(filename="Db/macbooks.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Преобразуем списки обратно в множества
    for series in data:
        data[series]["models"] = set(data[series]["models"])
        data[series]["cpu"] = {model: set(cpu) for model, cpu in data[series]["cpu"].items()}
        data[series]["ram"] = {model: set(ram) for model, ram in data[series]["ram"].items()}
        data[series]["storage"] = {model: set(stor) for model, stor in data[series]["storage"].items()}
        data[series]["colors"] = {model: set(colors) for model, colors in data[series]["colors"].items()}

    return data

MacBooks = load_macbooks_from_json()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Search")],
        [KeyboardButton(text="📁 Make exel file"), KeyboardButton(text="⚙️ Settings")],
        [KeyboardButton(text="📘 Instruction"), KeyboardButton(text="📦 About shops")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

search_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 iPhone", callback_data="device_iphone")],
    [InlineKeyboardButton(text="💻 Mac", callback_data="device_mac")],
    [InlineKeyboardButton(text="⌚ Watch", callback_data="device_watch")],
    [InlineKeyboardButton(text="📱 iPad", callback_data="device_ipad")],
    [InlineKeyboardButton(text="⭐ My List", callback_data="my_list")],
    [InlineKeyboardButton(text="⬅️ Back", callback_data="back_main")]
])

def get_series_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"iPhone {series}", callback_data=f"series_{series}")]
            for series in IPHONES
        ]
    )

def get_model_kb(series):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=model, callback_data=f"model_{model}")]
            for model in sorted(IPHONES[series]["models"])
        ]
    )

def get_memory_kb(series, model):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=mem, callback_data=f"memory_{mem}")]
            for mem in sorted(IPHONES[series]["memory"].get(model, []))
        ]
    )

def get_color_kb(series, model):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=color, callback_data=f"color_{color}")]
            for color in sorted(IPHONES[series]["colors"].get(model, []))
        ]
    )

confirm_selection_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="c_finish")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="device_iphone")]
    ]
)

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="↩️ Назад", callback_data="back_main")]
])



def get_mac_series_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"MacBook {series}", callback_data=f"mac_series_{series}")]
            for series in MacBooks
        ]
    )

def get_mac_model_kb(series):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=model, callback_data=f"mac_model_{model}")]
            for model in sorted(MacBooks[series]["models"])
        ]
    )

def get_mac_cpu_kb(series, model):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cpu, callback_data=f"mac_cpu_{cpu}")]
            for cpu in sorted(MacBooks[series]["cpu"].get(model, []))
        ]
    )

def get_mac_ram_kb(series, model):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ram, callback_data=f"mac_ram_{ram}")]
            for ram in sorted(MacBooks[series]["ram"].get(model, []))
        ]
    )

def get_mac_storage_kb(series, model):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=storage, callback_data=f"mac_storage_{storage}")]
            for storage in sorted(MacBooks[series]["storage"].get(model, []))
        ]
    )

def get_mac_color_kb(series, model):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=color, callback_data=f"mac_color_{color}")]
            for color in sorted(MacBooks[series]["colors"].get(model, []))
        ]
    )

def confirm_mac_selection_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="c_finish_mac")],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="device_mac")]
        ]
    )

confirm_selection_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="c_finish")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="device_iphone")]
    ]
)

end_search_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Завершить поиск", callback_data="end_search")]
    ]
)

settings_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Смена имени")],
        [KeyboardButton(text="⏱ Интервал обновления")],
        [KeyboardButton(text="️↩️ Назад")]
    ],
    resize_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

def get_interval_kb():
    builder = ReplyKeyboardBuilder()
    for days in range(1, 11):
        builder.add(KeyboardButton(text=f"{days} дней"))
    builder.adjust(3)
    builder.row(KeyboardButton(text="↩️ Назад"))
    return builder.as_markup(resize_keyboard=True)