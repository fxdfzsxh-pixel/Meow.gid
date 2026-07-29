import os
import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# ========== تنظیمات ==========
TOKEN = "8630392451:AAHJvr2vv3_563txO14bThr1DlciU24KayA"
ADMIN_ID = 7775328471
CHANNEL_ID = "@Meow_gid"
SUPPORT_LINK = "https://t.me/iWas_Mamad"

# ========== دیتابیس ==========
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "weekly_claimed": {}, "bot_status": True}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ========== لاگ ==========
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== توابع کمکی ==========
def get_user_data(user_id):
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"invites": 0, "invited_by": None, "name": ""}
        save_data(data)
    return data["users"][user_id]

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_bot_active():
    return data.get("bot_status", True)

def back_button():
    return InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu")

# ========== بررسی عضویت در کانال ==========
def check_channel_membership(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            return True
        return False
    except:
        return False

# ========== منوی اصلی ==========
def main_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    if not is_bot_active() and not is_admin(user_id):
        update.message.reply_text("⛔ ربات در حال حاضر غیرفعال است.")
        return
    
    if not check_channel_membership(context.bot, user_id):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/Meow_gid")]]
        msg = update.message.reply_text(
            "❗️ برای استفاده از ربات ابتدا در کانال زیر عضو شوید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data["join_message_id"] = msg.message_id
        return
    
    if "join_message_id" in context.user_data:
        try:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data["join_message_id"])
        except:
            pass
        context.user_data.pop("join_message_id", None)
    
    keyboard = [
        [
            InlineKeyboardButton("🤖 حساب کاربری", callback_data="profile"),
            InlineKeyboardButton("📎 لینک دعوت", callback_data="invite")
        ],
        [
            InlineKeyboardButton("✉️ پشتیبانی", url=SUPPORT_LINK),
            InlineKeyboardButton("🎁 پاداش هفتگی", callback_data="weekly")
        ]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("⚙️ پنل ادمین", callback_data="admin_panel")])
    
    update.message.reply_text(
        f"👋 سلام {user_name} عزیز!\nبه ربات خوش آمدی.\n\n📌 لطفاً یکی از گزینه‌های زیر را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== /start ==========
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    user_data = get_user_data(user_id)
    user_data["name"] = user_name
    save_data(data)
    
    if context.args and context.args[0].isdigit():
        referrer_id = int(context.args[0])
        if referrer_id != user_id:
            referrer_data = get_user_data(referrer_id)
            referrer_data["invites"] += 1
            save_data(data)
            update.message.reply_text(f"✅ شما توسط کاربری دعوت شدید! به جمع ما خوش آمدی.")
    
    main_menu(update, context)

# ========== حساب کاربری ==========
def profile(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    user_data = get_user_data(user_id)
    
    text = f"""👤 **حساب کاربری**

📛 **نام:** {user_name}
🆔 **آیدی:** `{user_id}`
📊 **تعداد دعوت:** {user_data['invites']} نفر
"""
    
    keyboard = [[back_button()]]
    query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ========== لینک دعوت ==========
def invite(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    bot_username = context.bot.get_me().username
    invite_link = f"https://t.me/{bot_username}?start={user_id}"
    
    text = f"""📎 **لینک دعوت اختصاصی شما**

`{invite_link}`

📊 **تعداد دعوت تا این لحظه:** {user_data['invites']} نفر

🎁 **با دعوت کردن دوستان، امتیاز کسب کنید!**
هر دوست که دعوت کنید، ۱ امتیاز به حساب شما اضافه می‌شود.
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 کپی لینک", callback_data="copy_link")],
        [back_button()]
    ]
    
    query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ========== پاداش هفتگی ==========
def weekly_reward(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
    user_data = get_user_data(user_id)
    
    today = datetime.now().date()
    last_claim = data["weekly_claimed"].get(user_id)
    
    if last_claim:
        last_claim_date = datetime.fromisoformat(last_claim).date()
        if (today - last_claim_date).days < 7:
            days_left = 7 - (today - last_claim_date).days
            text = f"⏳ شما قبلاً این هفته پاداش خود را دریافت کرده‌اید.\n📅 {days_left} روز دیگر می‌توانید مجدداً دریافت کنید."
            query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[back_button()]]))
            return
    
    user_data["invites"] += 1
    data["weekly_claimed"][user_id] = today.isoformat()
    save_data(data)
    
    text = f"🎁 **تبریک!**\n\n✅ شما ۱ امتیاز دعوت دریافت کردید.\n📊 تعداد کل دعوت‌های شما: {user_data['invites']}"
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[back_button()]]))

# ========== دکمه کپی لینک ==========
def copy_link(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer("✅ لینک کپی شد!", show_alert=True)

# ========== بازگشت به منوی اصلی ==========
def back_to_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    keyboard = [
        [
            InlineKeyboardButton("🤖 حساب کاربری", callback_data="profile"),
            InlineKeyboardButton("📎 لینک دعوت", callback_data="invite")
        ],
        [
            InlineKeyboardButton("✉️ پشتیبانی", url=SUPPORT_LINK),
            InlineKeyboardButton("🎁 پاداش هفتگی", callback_data="weekly")
        ]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("⚙️ پنل ادمین", callback_data="admin_panel")])
    
    query.edit_message_text(
        f"👋 سلام {user_name} عزیز!\nبه ربات خوش آمدی.\n\n📌 لطفاً یکی از گزینه‌های زیر را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== پنل ادمین ==========
def admin_panel(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        query.answer("❌ شما دسترسی به این بخش ندارید!", show_alert=True)
        return
    
    status_text = "✅ فعال" if is_bot_active() else "❌ غیرفعال"
    status_emoji = "🟢" if is_bot_active() else "🔴"
    
    keyboard = [
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_stats")],
        [InlineKeyboardButton("➕ افزایش دعوت", callback_data="admin_add_invite")],
        [InlineKeyboardButton("➖ کاهش دعوت", callback_data="admin_remove_invite")],
        [InlineKeyboardButton("📨 ارسال پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton(f"{status_emoji} وضعیت ربات: {status_text}", callback_data="admin_toggle_bot")],
        [back_button()]
    ]
    
    query.edit_message_text(
        f"⚙️ **پنل مدیریت**\n\n📋 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:\n\n📌 وضعیت ربات: {status_text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ========== خاموش/روشن ==========
def admin_toggle_bot(update: Update, context: CallbackContext):
    query = update.callback_query
    
    if not is_admin(query.from_user.id):
        query.answer("❌ شما دسترسی ندارید!", show_alert=True)
        return
    
    data["bot_status"] = not data.get("bot_status", True)
    save_data(data)
    
    status_text = "فعال" if data["bot_status"] else "غیرفعال"
    query.answer(f"✅ ربات {status_text} شد!", show_alert=True)
    admin_panel(update, context)

# ========== آمار کاربران ==========
def admin_stats(update: Update, context: CallbackContext):
    query = update.callback_query
    
    if not data["users"]:
        text = "📊 **آمار کاربران**\n\n❌ هیچ کاربری یافت نشد."
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]]
        query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return
    
    users_list = []
    for user_id, user_info in data["users"].items():
        name = user_info.get("name", "نامشخص")
        invites = user_info.get("invites", 0)
        users_list.append(f"👤 {name}\n🆔 `{user_id}`\n📊 {invites} دعوت\n---")
    
    display_users = users_list[:10]
    text = f"📊 **لیست کاربران**\n\n" + "\n".join(display_users)
    
    if len(users_list) > 10:
        text += f"\n\n📌 و {len(users_list) - 10} کاربر دیگر..."
    
    text += f"\n\n👥 **کل کاربران:** {len(users_list)}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]]
    query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ========== افزایش دعوت ==========
def admin_add_invite(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text(
        "➕ **افزایش دعوت**\n\n📝 لطفاً آیدی کاربر و تعداد دعوت را وارد کنید:\n📌 مثال: `123456789 5`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="admin_panel")]])
    )
    context.user_data["admin_action"] = "add_invite"

# ========== کاهش دعوت ==========
def admin_remove_invite(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text(
        "➖ **کاهش دعوت**\n\n📝 لطفاً آیدی کاربر و تعداد دعوت را وارد کنید:\n📌 مثال: `123456789 3`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="admin_panel")]])
    )
    context.user_data["admin_action"] = "remove_invite"

# ========== پیام همگانی ==========
def admin_broadcast(update: Update, context: CallbackContext):
    query = update.callback_query
    query.edit_message_text(
        "📨 **ارسال پیام همگانی**\n\n📝 لطفاً پیام خود را ارسال کنید.\n📢 این پیام برای همه کاربران ارسال خواهد شد",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لغو", callback_data="admin_panel")]])
    )
    context.user_data["admin_action"] = "broadcast"

# ========== مدیریت ورودی‌های ادمین ==========
def handle_admin_input(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return
    
    action = context.user_data.get("admin_action")
    if not action:
        return
    
    try:
        if action in ["add_invite", "remove_invite"]:
            parts = update.message.text.split()
            if len(parts) != 2:
                update.message.reply_text("❌ فرمت اشتباه! 📌 مثال: `123456789 5`", parse_mode="Markdown")
                return
            
            target_id, count = parts[0], int(parts[1])
            user_data = get_user_data(target_id)
            
            if action == "add_invite":
                user_data["invites"] += count
                update.message.reply_text(f"✅ {count} دعوت به کاربر {target_id} اضافه شد.")
            else:
                user_data["invites"] = max(0, user_data["invites"] - count)
                update.message.reply_text(f"✅ {count} دعوت از کاربر {target_id} کم شد.")
            
            save_data(data)
            context.user_data["admin_action"] = None
        
        elif action == "broadcast":
            sent = 0
            for user_id in data["users"].keys():
                try:
                    context.bot.send_message(int(user_id), f"📢 **پیام مدیریت**\n\n{update.message.text}")
                    sent += 1
                except:
                    pass
            
            update.message.reply_text(f"✅ پیام برای {sent} کاربر ارسال شد.")
            context.user_data["admin_action"] = None
    
    except Exception as e:
        update.message.reply_text(f"❌ خطا: {str(e)}")

# ========== هندلر دکمه‌ها ==========
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    handlers = {
        "profile": profile,
        "invite": invite,
        "weekly": weekly_reward,
        "copy_link": copy_link,
        "back_to_menu": back_to_menu,
        "admin_panel": admin_panel,
        "admin_stats": admin_stats,
        "admin_add_invite": admin_add_invite,
        "admin_remove_invite": admin_remove_invite,
        "admin_broadcast": admin_broadcast,
        "admin_toggle_bot": admin_toggle_bot,
    }
    
    if query.data in handlers:
        handlers[query.data](update, context)

# ========== اجرا ==========
if __name__ == "__main__":
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_admin_input))
    
    print("🚀 ربات روشن شد...")
    updater.start_polling()
    updater.idle()
