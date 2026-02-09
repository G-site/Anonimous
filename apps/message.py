from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButtonRequestUser, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramAPIError
import os
from hashids import Hashids
from dotenv import load_dotenv


from apps.database import get_my_hash, get_name_by_id
from bot_instance import bot


message_router = Router()


load_dotenv()
ADMIN = os.getenv("ADMIN")
HASHLIB_KEY = os.getenv("HASHLIB_KEY")
hashids = Hashids(salt=HASHLIB_KEY, min_length=8)


send_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Выбрать", request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False))],
        [KeyboardButton(text="❌ Отмена")]
        ], resize_keyboard=True, one_time_keyboard=True)
share_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🤝 Поделиться ботом', url='https://t.me/share/url?url=Зайди в бота, что бы получать анонимные сообщения👉 t.me/Anonim_Messssage_Bot')]
    ])
close_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
    ])


class MessageStates(StatesGroup):
    user = State()
    text = State()


@message_router.message(Command('send'))
async def send_by_command(message: Message, state: FSMContext):
    await message.answer(text="📬 <b>Кому хочешь отправить анонимное сообщение?</b>\n\n👤 Выбери пользователя из списка ниже, чтобы отправить своё послание 🤫", reply_markup=send_menu, parse_mode="HTML")
    await state.set_state(MessageStates.user)


@message_router.callback_query(F.data == 'send')
async def send_by_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text="📬 <b>Кому хочешь отправить анонимное сообщение?</b>\n\n👤 Выбери пользователя из списка ниже, чтобы отправить своё послание 🤫", reply_markup=send_menu, parse_mode="HTML")
    await state.set_state(MessageStates.user)
    await callback.answer("👤 Выбери получателя")


async def send_by_args(args, message: Message, state: FSMContext):
    user_id = hashids.decode(args)[0]
    await state.update_data(user=user_id)
    await message.answer(text="✏️ <b>Напиши своё анонимное послание</b>\n\nТы можешь отправить текст, фото, стикер или любое другое сообщение 🤫\nКогда будешь готов, просто отправь его в чат.", reply_markup=close_menu, parse_mode="HTML")
    await state.set_state(MessageStates.text)


@message_router.message(MessageStates.user)
async def get_message(message: Message, state: FSMContext):
    if message.text:
        text = message.text
        if text == '❌ Отмена':
            await state.clear()
    else:
        try:
            user_id = message.user_shared.user_id
            if not user_id:
                await message.edit_reply_markup(reply_markup=None)
                await state.clear()
            else:
                await state.update_data(user=user_id)
                await message.answer(text="✏️ <b>Напиши своё анонимное послание</b>\n\nТы можешь отправить текст, фото, стикер или любое другое сообщение 🤫\nКогда будешь готов, просто отправь его в чат.", reply_markup=close_menu, parse_mode="HTML")
                await state.set_state(MessageStates.text)
        except Exception as e:
            print(e)


@message_router.message(MessageStates.text)
async def send_message(message: Message, state: FSMContext):
    data = await state.get_data()
    my_id = message.from_user.id
    if message.text == '❌ Отмена':
        await state.clear()
    else:
        try:
            user = data["user"]
            recipient_menu = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='💬 Ответить', callback_data=f'answer_{my_id}')],
                [InlineKeyboardButton(text='🕵️‍♂️ Узнать кто', callback_data=f'who_{my_id}')]
            ])
            await bot.send_message(text="🔔 <b>У тебя новое анонимное сообщение!</b>", chat_id=user, parse_mode="HTML")
            await bot.copy_message(
                chat_id=user,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=recipient_menu
            )
            await message.answer(text="✅ <b>Сообщение отправлено!</b>", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        except TelegramBadRequest:
            hash = await get_my_hash(my_id)
            await message.answer(text=f"😅 <b>Упс...</b>\n\nСообщение не было отправлено, потому что этот пользователь ещё не пользуется ботом 🚫\n\n🔗 <b>Твоя ссылка для приглашения:</b>\n<i>https://t.me/Anonim_Messssage_Bot?start={hash}</i>\n\nОтправь её другу, чтобы он подключился и вы смогли обмениваться анонимными сообщениями 🤫", reply_markup=share_menu, parse_mode="HTML", disable_web_page_preview=True)
        except TelegramForbiddenError:
            hash = await get_my_hash(my_id)
            await message.answer(text=f"😅 <b>Упс...</b>\n\nСообщение не было отправлено, потому что этот пользователь ещё не пользуется ботом 🚫\n\n🔗 <b>Твоя ссылка для приглашения:</b>\n<i>https://t.me/Anonim_Messssage_Bot?start={hash}</i>\n\nОтправь её другу, чтобы он подключился и вы смогли обмениваться анонимными сообщениями 🤫", reply_markup=share_menu, parse_mode="HTML", disable_web_page_preview=True)
        except TelegramAPIError as e:
            hash = await get_my_hash(my_id)
            await message.answer(text=f"😅 <b>Упс...</b>\n\nСообщение не было отправлено, потому что этот пользователь ещё не пользуется ботом 🚫\n\n🔗 <b>Твоя ссылка для приглашения:</b>\n<i>https://t.me/Anonim_Messssage_Bot?start={hash}</i>\n\nОтправь её другу, чтобы он подключился и вы смогли обмениваться анонимными сообщениями 🤫", reply_markup=share_menu, parse_mode="HTML", disable_web_page_preview=True)
            print("TelegramAPIError:", e)
        except Exception as e:
            await message.answer(text="⚙️ <b>Упс...</b>\n\nСообщение не было отправлено по техническим причинам 😔\n\nПожалуйста, попробуй ещё раз чуть позже ⏳", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
            print(e)
        finally:
            await state.clear()


@message_router.callback_query(MessageStates.text, F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("❌ Отмена")


@message_router.callback_query(F.data.startswith("answer_"))
async def answer(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.data[len("answer_"):]
    await state.update_data(user=user_id)
    await callback.message.answer(text="✏️ <b>Напиши своё анонимное послание</b>\n\nТы можешь отправить текст, фото, стикер или любое другое сообщение 🤫\nКогда будешь готов, просто отправь его в чат.", reply_markup=close_menu, parse_mode="HTML")
    await state.set_state(MessageStates.text)
    await callback.answer("✏️ Напиши сообщение")


@message_router.callback_query(F.data.startswith("who_"))
async def who(callback: CallbackQuery):
    user_id = callback.data[len("who_"):]
    user = user_id
    prices = [LabeledPrice(label="🕵️‍♂️ Узнай, кто отправил сообщение!", amount=20)]
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="🕵️‍♂️ Узнай, кто отправил сообщение!",
        description="🕵️‍♂️ Узнай, кто отправил сообщение!",
        payload=user,
        currency="XTR",
        prices=prices,
        start_parameter="buy_stars_product"
    )
    await callback.answer("🕵️‍♂️ Узнать кто")


@message_router.pre_checkout_query()
async def pre_checkout(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


@message_router.message(F.successful_payment)
async def handle_payment(message: Message):
    comment = message.successful_payment.invoice_payload
    name = await get_name_by_id(comment)
    await message.answer(f"✅ <b>Оплата прошла успешно!</b>\n\n💬 Сообщение было отправлено пользователем <b><a href='tg://openmessage?user_id={comment}'>{name}</a></b>🤫", parse_mode="HTML", message_effect_id="5046509860389126442")


@message_router.message(Command("refund"))
async def refund_handler(message: Message, command: CommandObject):
    if message.from_user.id != ADMIN:
        await message.answer("🚫 У тебя нет прав на выполнение этой команды.")
        return
    if not command.args:
        await message.answer("❗ Формат: `/refund <user_id> <charge_id>`", parse_mode="Markdown")
        return
    args = command.args.split()
    if len(args) < 2:
        await message.answer("⚠️ Нужно указать два аргумента: `/refund <user_id> <charge_id>`", parse_mode="Markdown")
        return
    user_id = int(args[0])
    telegram_payment_charge_id = args[1]
    try:
        result = await bot.refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=telegram_payment_charge_id
        )
        if result:
            await message.answer(
                f"✅ Возврат пользователю `{user_id}` по платёжному ID `{telegram_payment_charge_id}` успешно оформлен.",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"⚠️ Telegram не подтвердил возврат `{telegram_payment_charge_id}`.",
                parse_mode="Markdown"
            )
    except Exception as e:
        await message.answer(f"❌ Ошибка: `{e}`", parse_mode="Markdown")
