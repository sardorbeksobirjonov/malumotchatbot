import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = "7503518853:AAHKgfSPxmXLulSMCXpVKs8QEuh9NJPM6cg"  # O'zingning tokeningni yoz
ADMIN_ID = 7752032178  # Admin Telegram user_id raqami (raqam ko‘rinishida)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot)
router = Router()

class Form(StatesGroup):
    add = State()
    delete = State()
    reklama = State()

user_data = {}
user_logs = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 Ma'lumot qo‘shish"), KeyboardButton(text="🗑 Ma'lumot o‘chirish")],
        [KeyboardButton(text="📋 Ma'lumotlarni ko‘rish"), KeyboardButton(text="📞 Admin bilan bog‘lanish")]
    ],
    resize_keyboard=True
)

@router.message(F.text == "/start")
async def start_handler(msg: Message):
    user_data.setdefault(msg.from_user.id, [])
    user_logs.setdefault(msg.from_user.id, {"added": [], "deleted": []})
    await msg.answer(
        f"👋 <b>Xush kelibsiz, {msg.from_user.full_name}!</b>\n"
        "🤖 Ushbu bot orqali siz shaxsiy ma’lumotlaringizni qo‘shish, ko‘rish va o‘chirish imkoniyatiga egasiz.",
        reply_markup=main_menu
    )

@router.message(F.text == "📥 Ma'lumot qo‘shish")
async def add_prompt(msg: Message, state: FSMContext):
    await msg.answer("✍️ Iltimos, qo‘shmoqchi bo‘lgan ma’lumotni yozing:")
    await state.set_state(Form.add)

@router.message(Form.add)
async def add_data(msg: Message, state: FSMContext):
    user_data.setdefault(msg.from_user.id, []).append(msg.text)
    user_logs[msg.from_user.id]["added"].append(msg.text)
    await msg.answer(f"✅ Siz <b>{msg.text}</b> ma'lumotini muvaffaqiyatli qo‘shdingiz!", reply_markup=main_menu)
    await state.clear()

@router.message(F.text == "🗑 Ma'lumot o‘chirish")
async def delete_prompt(msg: Message, state: FSMContext):
    data = user_data.get(msg.from_user.id, [])
    if not data:
        await msg.answer("📭 Sizda hech qanday ma’lumot yo‘q.")
        return
    formatted = "\n".join([f"{i+1}. {val}" for i, val in enumerate(data)])
    await msg.answer(f"🗑 O‘chirmoqchi bo‘lgan ma’lumot raqamini yozing:\n\n{formatted}")
    await state.set_state(Form.delete)

@router.message(Form.delete)
async def delete_data(msg: Message, state: FSMContext):
    try:
        idx = int(msg.text.strip()) - 1
        data = user_data.get(msg.from_user.id, [])
        if 0 <= idx < len(data):
            removed = data.pop(idx)
            user_logs[msg.from_user.id]["deleted"].append(removed)
            await msg.answer(f"🗑 <b>{removed}</b> ma’lumoti o‘chirildi!", reply_markup=main_menu)
        else:
            await msg.answer("❌ Noto‘g‘ri raqam! Qayta urinib ko‘ring.")
    except ValueError:
        await msg.answer("⚠️ Iltimos, faqat raqam kiriting.")
    await state.clear()

@router.message(F.text == "📋 Ma'lumotlarni ko‘rish")
async def view_data(msg: Message):
    data = user_data.get(msg.from_user.id, [])
    if not data:
        await msg.answer("📭 Sizda hech qanday ma’lumot yo‘q.")
    else:
        formatted = "\n".join([f"{i+1}. {val}" for i, val in enumerate(data)])
        await msg.answer(f"📋 <b>Sizning ma’lumotlaringiz:</b>\n\n{formatted}")

@router.message(F.text == "📞 Admin bilan bog‘lanish")
async def contact_admin(msg: Message):
    await msg.answer(
        " 📞 <b>Admin bilan bog‘lanish:</b>\n\n"
        "📩 Telegram: @sardorbeksobirjonov \n\n"
        "📺  Instagram: hozircha yoq\n\n"
        "📲 telnomer: +998 94 089 81 19"
    )

@router.message(F.text.lower() == "reklama1020")
async def reklama_prompt(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("⛔ Sizga bu buyruq taqiqlangan!")
        return
    await msg.answer("📢 Yuboriladigan reklama matnini yozing:")
    await state.set_state(Form.reklama)

@router.message(Form.reklama)
async def reklama_send(msg: Message, state: FSMContext):
    count = 0
    for uid in user_data:
        try:
            await bot.send_message(uid, f"📢 <b>REKLAMA:</b>\n{msg.text}")
            count += 1
        except:
            pass
    await msg.answer(f"✅ Reklama yuborildi: {count} ta foydalanuvchiga.")
    await state.clear()

@router.message(F.text.lower() == "foydalanuvchilar1")
async def show_users(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("⛔ Bu bo‘lim faqat admin uchun!")
        return
    if not user_data:
        await msg.answer("📭 Hech qanday foydalanuvchi topilmadi.")
        return

    text = "👥 <b>Foydalanuvchilar ro‘yxati va ularning ma’lumotlari:</b>\n\n"
    for uid, values in user_data.items():
        log = user_logs.get(uid, {"added": [], "deleted": []})
        added = ", ".join(log['added']) or "yo‘q"
        deleted = ", ".join(log['deleted']) or "yo‘q"
        text += f"🆔 <code>{uid}</code>\n➕ Qo‘shgan: {added}\n❌ O‘chirgan: {deleted}\n\n"

    await msg.answer(text)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
