import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
import io
import pandas as pd


from apps.database import check_admin, get_all_users, get_db, gen_promo, get_tech_promo, get_all_promos, get_and_delete_promo, update_activity, get_users_by_parameter, get_all_user_info, delete_user


admin_router = Router()


broadcast_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🛠️ Сообщить о тех. перерыве', callback_data='broadcast_maintenance')],
    [InlineKeyboardButton(text='👥 Попросить поделиться с другом', callback_data='broadcast_share')],
    [InlineKeyboardButton(text='📢 Попросить подписаться на ТГК', callback_data='broadcast_channel')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


stats_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💾 Скачать базу данных', callback_data='stats_download')],
    [InlineKeyboardButton(text='🟢 Активные', callback_data='stats_active'), InlineKeyboardButton(text='🔴 Неактивные', callback_data='stats_inactive')],
    [InlineKeyboardButton(text='📄 Выписка пользователя', callback_data='stats_user_report')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


users_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗑 Удалить пользователя', callback_data='users_delete')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


promocode_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎲 Создать одноразовый', callback_data='promo_single')],
    [InlineKeyboardButton(text='🔄 Создать многоразовый', callback_data='promo_multi')],
    [InlineKeyboardButton(text='🔑 Получить тех. промокод', callback_data='promo_tech')],
    [InlineKeyboardButton(text='📋 Список промокодов', callback_data='promo_list')],
    [InlineKeyboardButton(text='🗑 Удалить промокод', callback_data='promo_delete')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_menu')]
    ])


subscribe_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔔 Подписаться', url='https://t.me/+kKVb9YkgDF03ZDdi')]])
share_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔗 Поделиться', url="https://t.me/share/url?url=t.me/Anonim_Messssage_Bot")]])


class PromoStates(StatesGroup):
    waiting_delete = State()


class UserInfoStates(StatesGroup):
    waiting_id = State()


class UserDeleteStates(StatesGroup):
    waiting_delete = State()


async def get_admin_menu(is_owner: bool):
    buttons = [
        [
            InlineKeyboardButton(
                text='📨 Рассылка',
                callback_data='admin_broadcast'
            )
        ],
        [
            InlineKeyboardButton(
                text='🎟 Промокоды',
                callback_data='admin_promocodes'
            )
        ],
        [
            InlineKeyboardButton(
                text='📊 Статистика',
                callback_data='admin_stats'
            )
        ],
        [
            InlineKeyboardButton(
                text='🔗 Реферальные ссылки',
                callback_data='admin_referrals'
            )
        ],
    ]

    if is_owner:
        buttons.extend([
            [
                InlineKeyboardButton(
                    text='👥 Управление пользователями',
                    callback_data='admin_users'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛡 Управление модераторами',
                    callback_data='admin_moderators'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Настройки бота',
                    callback_data='admin_settings'
                )
            ],
        ])

    buttons.append([
        InlineKeyboardButton(
            text='🏠 Главное меню',
            callback_data='start',
            style='success'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send_long_message(message, text, parse_mode="HTML"):
    max_length = 4000

    parts = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            parts.append(current)
            current = ""

        current += line + "\n"

    if current:
        parts.append(current)

    for part in parts:
        await message.answer(
            part,
            parse_mode=parse_mode
        )


@admin_router.message(Command('admin'))
async def admin1(message: Message):
    status = await check_admin(message.from_user.id)
    if status in ('M', 'O'):
        is_owner = status == 'O'
        status_names = {
            'O': '👑 Владелец',
            'M': '🛡 Модератор',
            'A': '⚙️ Администратор',
            'U': '👤 Пользователь'
        }

        admin_status = status_names.get(
            status,
            '👤 Администратор'
        )
        reply_markup = await get_admin_menu(is_owner)
        await message.answer(
            text=(
                "🛠 <b>Панель администратора</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>Статус:</b> {admin_status}\n\n"
                "⚙️ Управление пользователями, промокодами, "
                "рассылками и статистикой.\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "⚡ <b>Система UMAO</b>"
            ),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


@admin_router.callback_query(F.data == 'admin_menu')
async def admin2(callback: CallbackQuery):
    status = await check_admin(callback.from_user.id)
    if status in ('M', 'O'):
        is_owner = status == 'O'
        status_names = {
            'O': '👑 Владелец',
            'M': '🛡 Модератор',
            'A': '⚙️ Администратор',
            'U': '👤 Пользователь'
        }
        admin_status = status_names.get(
            status,
            '👤 Администратор'
        )
        reply_markup = await get_admin_menu(is_owner)
        await callback.message.answer(
            text=(
                "🛠 <b>Панель администратора</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>Статус:</b> {admin_status}\n\n"
                "⚙️ Управление пользователями, промокодами, "
                "рассылками и статистикой.\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "⚡ <b>Система UMAO</b>"
            ),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        await callback.answer()


@admin_router.callback_query(F.data.startswith("stats_"))
async def stats(callback: CallbackQuery, state: FSMContext):
    action = callback.data[len("stats_"):]
    match action:
        case "download":
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
        case "active" | "inactive":
            users = await get_users_by_parameter(action)
            status_text = "🟢 Активные" if action == "active" else "🔴 Неактивные"
            lines = [
                f"📋 <b>{status_text}</b>",
                f"👥 Всего: <b>{len(users)}</b>\n"
            ]
            for index, user in enumerate(users, 1):
                name = user.get("name") or "Без имени"
                id = user["id"]
                username = user.get("username") or "—"
                lines.append(
                    f"{index}. 👤 <b>{name}</b> "
                    f"🆔 <code>{id}</code>\n"
                    f"🔗 @{username}\n"
                )
            text = "\n".join(lines)
            await send_long_message(callback.message, text)
        case "user_report":
            await state.set_state(UserInfoStates.waiting_id)
            await callback.message.answer("📄 <b>Выписка пользователя</b>\n\nВведите Telegram ID пользователя:", parse_mode="HTML")
    await callback.answer()


@admin_router.message(UserInfoStates.waiting_id)
async def user_report(message: Message, state: FSMContext):
    value = message.text.strip()
    if not value.isdigit():
        await message.answer(
            "❌ Некорректный Telegram ID.\n\n"
            "Введите ID, состоящий только из цифр.\n"
            "Например: <code>123456789</code>",
            parse_mode="HTML"
        )
        return
    user = await get_all_user_info(int(value))
    if user is None:
        await message.answer(
            f"❌ Пользователь <code>{value}</code> не найден.",
            parse_mode="HTML"
        )
        return
    status_text = "🟢 Активный" if user["active"] else "🔴 Неактивный"
    username = (
        f"@{user['username']}"
        if user["username"]
        else "—"
    )
    created_at = user["created_at"]
    if created_at:
        created_at = created_at.strftime("%d.%m.%Y %H:%M")
    status_names = {
        "O": "👑 Владелец",
        "M": "🛡 Модератор",
        "A": "⚙️ Администратор",
        "U": "👤 Пользователь"
    }
    user_status = status_names.get(
        user["status"],
        "👤 Пользователь"
    )

    text = (
        "📄 <b>ВЫПИСКА ПОЛЬЗОВАТЕЛЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🔢 <b>Номер пользователя:</b> <code>{user['primary_id']}</code>\n"
        f"👤 <b>Имя:</b> {user['name'] or '—'}\n"
        f"🆔 <b>ID:</b> <code>{user['id']}</code>\n"
        f"🔑 <b>Hash:</b> <code>{user['user_hash'] or '—'}</code>\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"👑 <b>Статус:</b> {user_status}\n"
        f"📊 <b>Активность:</b> {status_text}\n\n"

        f"📅 <b>Регистрация:</b> {created_at or '—'}\n\n"

        "📈 <b>Статистика</b>\n"
        f"📨 Отправлено: <b>{user['sent']}</b>\n"
        f"👁 Просмотрено: <b>{user['viewed']}</b>\n"
        f"📥 Получено: <b>{user['received']}</b>\n"
        f"⭐ Потрачено звёзд: <b>{user['wasted']}</b>\n"
    )

    await message.answer(text, parse_mode="HTML")


@admin_router.callback_query(F.data.startswith("promo_"))
async def promocodes(callback: CallbackQuery, state: FSMContext):
    action = callback.data[len("promo_"):]
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
        case "list":
            promos = await get_all_promos()
            lines = ["📋 <b>Список промокодов</b>\n"]
            promo_type_names = {
                "single": "Одноразовый",
                "multi": "Многоразовый",
                "tech": "Технический"
            }
            for promo in promos:
                type_name = promo_type_names.get(
                    promo["type"],
                    "Неизвестный"
                )
                lines.append(
                    f"🎟 <code>{promo['code']}</code>\n"
                    f"▫️ Тип: <b>{type_name}</b>\n"
                )
            text = "\n".join(lines)
            await send_long_message(callback.message, text)
            # await callback.message.answer(text, parse_mode="HTML")
        case "delete":
            await state.set_state(PromoStates.waiting_delete)
            await callback.message.answer("⚠️ <b>Удаление промокода</b>\n\nВведите промокод, который вы хотите удалить из базы данных.\n\n❗ <i>Внимание! После удаления промокод станет недействительным и не сможет быть использован.</i>\n\n🔒 <i>Технический промокод удалить невозможно.</i>", parse_mode="HTML")
    await callback.answer()


@admin_router.message(PromoStates.waiting_delete)
async def promo_delete(message: Message, state: FSMContext):
    code = message.text.strip()
    promo = await get_and_delete_promo(code)
    if not promo:
        await message.answer("❌ Промокод не найден.\n\nПроверьте правильность написания и попробуйте ещё раз.")
        return
    if promo["type"] == "tech":
        await message.answer("🔒 <b>Технический промокод нельзя удалить.</b>", parse_mode="HTML")
        await state.clear()
        return
    await message.answer(f"🗑 <b>Промокод удалён!</b>\n\n🎟 Промокод: <code>{code}</code>", parse_mode="HTML")
    await state.clear()


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
        case "users":
            await callback.message.edit_text(text="👥 <b>Управление пользователями</b>\n\nВыберите действие:", reply_markup=users_menu, parse_mode="HTML")
        case "moderators":
            await callback.message.edit_text(text="👥 <b>Управление модераторами</b>\n\n⚠️ <i>Эта функция временно недоступна.</i>", parse_mode="HTML")
        case "settings":
            await callback.message.edit_text(text="⚙️ <b>Настройки бота</b>\n\n⚠️ <i>Эта функция временно недоступна.</i>", parse_mode="HTML")
        case _:
            await callback.answer("Неизвестная команда", show_alert=True)
    await callback.answer()


@admin_router.callback_query(F.data == 'users_delete')
async def users_delete(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserDeleteStates.waiting_delete)
    await callback.message.edit_text("🗑 <b>Удаление пользователя</b>\n\nВведите Telegram ID пользователя, которого вы хотите удалить из базы данных.\n\n❗ <i>Внимание! После удаления пользователь потеряет доступ к боту и не сможет восстановить свои данные.</i>", parse_mode="HTML")
    await callback.answer()


@admin_router.message(UserDeleteStates.waiting_delete)
async def user_delete(message: Message, state: FSMContext):
    value = message.text.strip()
    if not value.isdigit():
        await message.answer(
            "❌ Некорректный Telegram ID.\n\n"
            "Введите ID, состоящий только из цифр.\n"
            "Например: <code>123456789</code>",
            parse_mode="HTML"
        )
        await state.clear()
        return
    confirm_delete_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Удалить",
                    callback_data=f"user_delete_{value}",
                    style="danger"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel",
                    style="success"
                )
            ]
        ]
    )
    confirm_message = await message.answer(f"⚠️ <b>Удалить пользователя?</b>\n\n🆔 ID: <code>{value}</code>\n\n❗ Действие необратимо.\n⏱ Подтверждение действительно 30 секунд.", reply_markup=confirm_delete_keyboard, parse_mode="HTML")
    await state.clear()
    await asyncio.sleep(30)
    try:
        await confirm_message.delete()
    except TelegramBadRequest:
        pass


@admin_router.callback_query(F.data.startswith("user_delete_"))
async def confirm_user_delete(callback: CallbackQuery):
    value = callback.data[len("user_delete_"):]
    await delete_user(int(value))
    await callback.message.edit_text(f"🗑 <b>Пользователь удалён!</b>\n\n🆔 ID: <code>{value}</code>", parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("broadcast_"))
async def broadcast_answer(callback: CallbackQuery):
    action = callback.data[len("broadcast_"):]
    sent_users = []
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
    for id in users:
        try:
            await callback.bot.send_message(
                chat_id=id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,

            )
            sent_users.append(id)
            await asyncio.sleep(0.5)
        except TelegramAPIError:
            pass
    lines = ["📨 <b>Уведомление получили:</b>\n"]
    for user_id in sent_users:
        lines.append(f"🆔 <code>{user_id}</code>")
    await callback.message.answer(
        f"✅ <b>Рассылка завершена</b>\n"
        f"📊 Доставлено: <b>{len(sent_users)}</b>\n\n"
        + "\n".join(lines),
        parse_mode="HTML"
    )
    await update_activity(sent_users)


@admin_router.callback_query(F.data == "cancel")
async def cancel_delete(callback: CallbackQuery):
    await callback.message.edit_text("❌ Удаление отменено")
    await callback.answer()
