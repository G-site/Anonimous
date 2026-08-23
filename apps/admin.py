import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
import io
import pandas as pd


from apps.database import check_admin, get_all_users, get_db, gen_promo, get_tech_promo


admin_router = Router()


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📨 Рассылка', callback_data='admin_broadcast')],
    [InlineKeyboardButton(text='🎟 Промокоды', callback_data='admin_promocodes')],
    [InlineKeyboardButton(text='📊 Статистика', callback_data='admin_stats')],
    [InlineKeyboardButton(text='🔗 Реферальные ссылки', callback_data='admin_referrals')],
    [InlineKeyboardButton(text='🗄 Управление базой данных', callback_data='admin_database')],
    ])


broadcast_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🛠️ Сообщить о тех. перерыве', callback_data='broadcast_maintenance')],
    [InlineKeyboardButton(text='👥 Попросить поделиться с другом', callback_data='broadcast_share')],
    [InlineKeyboardButton(text='📢 Попросить подписаться на ТГК', callback_data='broadcast_channel')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


stats_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💾 Скачать базу данных', callback_data='stats_download')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


promocode_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎲 Создать одноразовый', callback_data='gen_single')],
    [InlineKeyboardButton(text='🔄 Создать многоразовый', callback_data='gen_multi')],
    [InlineKeyboardButton(text='🔑 Получить тех. промокод', callback_data='gen_tech')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


subscribe_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔔 Подписаться', url='https://t.me/+kKVb9YkgDF03ZDdi')]])
share_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔗 Поделиться', url="https://t.me/share/url?url=t.me/Anonim_Messssage_Bot")]])


@admin_router.message(Command('admin'))
async def admin1(message: Message):
    status = await check_admin(message.from_user.id)
    if status == 'M':
        await message.answer(text="🛠 <b>Панель администратора</b>\n\n👋 Добро пожаловать в закрытый раздел управления ботом!\n\nЗдесь вы можете контролировать основные функции системы: просматривать статистику пользователей и активности, управлять промокодами и реферальными ссылками, запускать информационные рассылки, а также выполнять другие административные действия.\n\n⚙️ Используйте кнопки ниже, чтобы выбрать необходимый раздел.\n\n🔐 Все доступные здесь функции предназначены только для администраторов.", reply_markup=admin_menu, parse_mode="HTML")


@admin_router.callback_query(F.data == 'admin_menu')
async def admin2(callback: CallbackQuery):
    await callback.message.edit_text(text="🛠 <b>Панель администратора</b>\n\n👋 Добро пожаловать в закрытый раздел управления ботом!\n\nЗдесь вы можете контролировать основные функции системы: просматривать статистику пользователей и активности, управлять промокодами и реферальными ссылками, запускать информационные рассылки, а также выполнять другие административные действия.\n\n⚙️ Используйте кнопки ниже, чтобы выбрать необходимый раздел.\n\n🔐 Все доступные здесь функции предназначены только для администраторов.", reply_markup=admin_menu, parse_mode="HTML")


@admin_router.callback_query(F.data == 'stats_download')
async def download(callback: CallbackQuery):
    rows = await get_db()
    data = [dict(row) for row in rows]
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    file = BufferedInputFile(
        buffer.read(),
        filename="database.xlsx"
    )
    await callback.message.answer_document(document=file, caption="🗄️Текущая база данных пользователей бота.")


@admin_router.callback_query(F.data.startswith("gen_"))
async def promo_gen(callback: CallbackQuery):
    action = callback.data[len("gen_"):]
    match action:
        case "single":
            promo = await gen_promo(1)
            await callback.message.answer(f"🎉 *Промокод успешно создан!*\n\n🎟 Промокод: `{promo}`\n🔄 Тип: *одноразовый*", parse_mode="Markdown")
        case "multi":
            promo = await gen_promo(99)
            await callback.message.answer(f"🎉 *Промокод успешно создан!*\n\n🎟 Промокод: `{promo}`\n♾ Тип: *безлимитный*\n\n📝 Примечание: реальное количество использований промокода только 99 раз.", parse_mode="Markdown")
        case "tech":
            promo = await get_tech_promo()
            await callback.message.answer(f"🔑 *Технический промокод выдан!*\n\n🎟 Промокод: `{promo}`\n♾ Тип: *безлимитный*\n\n📝 *Примечание:*\nДанный промокод предназначен исключительно для технических тестирований и проверки работоспособности системы.\n\n🚫 Передавать или распространять этот промокод другим лицам запрещено.\n\n👥 Промокод является единым для всех администраторов и не генерируется индивидуально.\n\n🔄 Промокод автоматически меняется один раз в неделю — *каждое воскресенье в 17:00*.", parse_mode="Markdown")


@admin_router.callback_query(F.data.startswith("admin_"))
async def admin_answer(callback: CallbackQuery):
    action = callback.data[len("admin_"):]
    match action:
        case "broadcast":
            await callback.message.edit_text(text="📨 <b>Рассылка сообщений</b>\n\nВыберите тип рассылки:", reply_markup=broadcast_menu, parse_mode="HTML")
        case "promocodes":
            await callback.message.edit_text(text="🎟️ <b>Управление промокодами</b>", reply_markup=promocode_menu, parse_mode="HTML")
        case "stats":
            await callback.message.edit_text(text="📊 <b>Статистика и отчёты</b>\n\nВыберите нужный отчёт:", reply_markup=stats_menu, parse_mode="HTML")
        case "referrals":
            await callback.message.edit_text(text="🔗 <b>Реферальные ссылки</b>\n\n⚠️ <i>Эта функция временно недоступна.</i>", parse_mode="HTML")
        case "database":
            await callback.message.edit_text(text="🗄 <b>Управление базой данных</b>\n\n⚠️ <i>Эта функция временно недоступна.</i>", parse_mode="HTML")


@admin_router.callback_query(F.data.startswith("broadcast_"))
async def broadcast_answer(callback: CallbackQuery):
    action = callback.data[len("broadcast_"):]
    match action:
        case "maintenance":
            text="🛠 <b>Внимание!</b>\n\nЗавтра у нас планируется <i>технический перерыв</i> ⏳\nВо время него бот может быть недоступен или работать с перебоями ⚡\n\n🙏 Пожалуйста, имей это в виду и не переживай — после перерыва мы снова будем рады принимать твои анонимные сообщения💌"
            keyboard=None
        case "share":
            text="🤝 <b>Поделись с другом!</b>\n\nХочешь получать больше анонимных сообщений и сюрпризов? 🎁\nОтправь свою секретную ссылку другу и пусть он тоже попробует наш бот 💌\n\n📤 Чем больше друзей — тем веселее и интереснее! 😎"
            keyboard=share_menu
        case "channel":
            text="📢 <b>Будь в курсе всех новостей!</b>\n\nЧтобы не пропускать обновления и новые функции, подпишись на наш <b>Telegram-канал</b> 💌\nТам ты найдёшь интересные анонсы, советы и сюрпризы для участников нашего чата 🎁"
            keyboard=subscribe_menu
        case _:
            await callback.answer("Неизвестная рассылка", show_alert=True)
            return
    users = await get_all_users()
    sent = 0
    for id in users:
        try:
            await callback.bot.send_message(
                chat_id=id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,

            )
            sent += 1
            await asyncio.sleep(0.5)
        except TelegramAPIError:
            pass
    await callback.message.answer(f"✅ Отправлено {sent} пользователям!")
