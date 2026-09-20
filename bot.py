# -*- coding: utf-8 -*-
"""Игровой Telegram-бот для группы: звания, скины КС, рынок, кейсы, игры, модерация, магазин."""
import os, json, sqlite3, random, time, re, logging, asyncio

from telegram import Update, InlineKeyboardButton as B, InlineKeyboardMarkup as M, ChatPermissions
from telegram.error import BadRequest, TelegramError
from telegram.ext import (Application, CommandHandler, MessageHandler, CallbackQueryHandler,
                          ChatMemberHandler, ContextTypes, filters)

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("bot")

BASE = os.path.dirname(os.path.abspath(__file__))
def _load(name, default):
    path = os.path.join(BASE, name)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return default


CFG = _load("config.json", {})
TOKEN = os.getenv("BOT_TOKEN") or CFG.get("token", "")
if not TOKEN or TOKEN.startswith("ВСТАВЬ"):
    raise SystemExit("Не задан токен: укажите переменную BOT_TOKEN на хостинге или token в config.json")
OWNER = int(os.getenv("OWNER_ID") or CFG.get("owner_id", 5139892680))
DEFAULT_DATA = json.loads(r'''{
 "cases": {
  "common": {
   "name": "Обычный кейс",
   "price": 500,
   "emoji": "📦"
  },
  "rare": {
   "name": "Редкий кейс",
   "price": 3000,
   "emoji": "🎁"
  },
  "epic": {
   "name": "Эпический кейс",
   "price": 12000,
   "emoji": "💜"
  },
  "legendary": {
   "name": "Легендарный кейс",
   "price": 46000,
   "emoji": "🌟"
  }
 },
 "skins": [
  {
   "id": 1,
   "name": "P250 | Sand Dune",
   "price": 15,
   "tier": "common"
  },
  {
   "id": 2,
   "name": "Glock-18 | Sand Dune",
   "price": 20,
   "tier": "common"
  },
  {
   "id": 3,
   "name": "Nova | Predator",
   "price": 40,
   "tier": "common"
  },
  {
   "id": 4,
   "name": "Dual Berettas | Colony",
   "price": 50,
   "tier": "common"
  },
  {
   "id": 5,
   "name": "MP9 | Storm",
   "price": 60,
   "tier": "common"
  },
  {
   "id": 6,
   "name": "UMP-45 | Carbon Fiber",
   "price": 70,
   "tier": "common"
  },
  {
   "id": 7,
   "name": "MAC-10 | Silver",
   "price": 90,
   "tier": "common"
  },
  {
   "id": 8,
   "name": "P90 | Module",
   "price": 100,
   "tier": "common"
  },
  {
   "id": 9,
   "name": "Five-SeveN | Forest Night",
   "price": 120,
   "tier": "common"
  },
  {
   "id": 10,
   "name": "SG 553 | Anodized Navy",
   "price": 200,
   "tier": "common"
  },
  {
   "id": 11,
   "name": "AK-47 | Safari Mesh",
   "price": 350,
   "tier": "common"
  },
  {
   "id": 12,
   "name": "M4A1-S | Boreale",
   "price": 700,
   "tier": "common"
  },
  {
   "id": 13,
   "name": "USP-S | Cortex",
   "price": 600,
   "tier": "rare"
  },
  {
   "id": 14,
   "name": "Glock-18 | Water Elemental",
   "price": 900,
   "tier": "rare"
  },
  {
   "id": 15,
   "name": "Desert Eagle | Oxide Blaze",
   "price": 800,
   "tier": "rare"
  },
  {
   "id": 16,
   "name": "AK-47 | Elite Build",
   "price": 1100,
   "tier": "rare"
  },
  {
   "id": 17,
   "name": "M4A4 | Desert-Strike",
   "price": 1400,
   "tier": "rare"
  },
  {
   "id": 18,
   "name": "AWP | Atheris",
   "price": 1700,
   "tier": "rare"
  },
  {
   "id": 19,
   "name": "P90 | Asiimov",
   "price": 2500,
   "tier": "rare"
  },
  {
   "id": 20,
   "name": "M4A4 | Neo-Noir",
   "price": 3000,
   "tier": "rare"
  },
  {
   "id": 21,
   "name": "AK-47 | Redline",
   "price": 3200,
   "tier": "rare"
  },
  {
   "id": 22,
   "name": "USP-S | Kill Confirmed",
   "price": 4000,
   "tier": "rare"
  },
  {
   "id": 23,
   "name": "AK-47 | Neon Revolution",
   "price": 4500,
   "tier": "epic"
  },
  {
   "id": 24,
   "name": "M4A1-S | Hyper Beast",
   "price": 5500,
   "tier": "epic"
  },
  {
   "id": 25,
   "name": "AWP | Neo-Noir",
   "price": 6000,
   "tier": "epic"
  },
  {
   "id": 26,
   "name": "AWP | Hyper Beast",
   "price": 6500,
   "tier": "epic"
  },
  {
   "id": 27,
   "name": "M4A4 | The Emperor",
   "price": 7000,
   "tier": "epic"
  },
  {
   "id": 28,
   "name": "AWP | Asiimov",
   "price": 7500,
   "tier": "epic"
  },
  {
   "id": 29,
   "name": "AK-47 | Vulcan",
   "price": 8000,
   "tier": "epic"
  },
  {
   "id": 30,
   "name": "Desert Eagle | Printstream",
   "price": 10000,
   "tier": "epic"
  },
  {
   "id": 31,
   "name": "AK-47 | Fire Serpent",
   "price": 13500,
   "tier": "epic"
  },
  {
   "id": 32,
   "name": "Glock-18 | Fade",
   "price": 18000,
   "tier": "epic"
  },
  {
   "id": 33,
   "name": "Bayonet | Doppler",
   "price": 27000,
   "tier": "legendary"
  },
  {
   "id": 34,
   "name": "Flip Knife | Fade",
   "price": 25000,
   "tier": "legendary"
  },
  {
   "id": 35,
   "name": "M9 Bayonet | Doppler",
   "price": 36000,
   "tier": "legendary"
  },
  {
   "id": 36,
   "name": "Karambit | Doppler",
   "price": 45000,
   "tier": "legendary"
  },
  {
   "id": 37,
   "name": "Butterfly Knife | Doppler",
   "price": 60000,
   "tier": "legendary"
  },
  {
   "id": 38,
   "name": "Butterfly Knife | Fade",
   "price": 90000,
   "tier": "legendary"
  },
  {
   "id": 39,
   "name": "Karambit | Fade",
   "price": 135000,
   "tier": "legendary"
  },
  {
   "id": 40,
   "name": "AWP | Gungnir",
   "price": 315000,
   "tier": "legendary"
  },
  {
   "id": 41,
   "name": "AWP | Dragon Lore",
   "price": 720000,
   "tier": "legendary"
  }
 ]
}''')
DATA = _load("skins.json", DEFAULT_DATA)
SKINS = {s["id"]: s for s in DATA["skins"]}
CASES = DATA["cases"]

RANKS = ["Рядовой", "Ефрейтор", "Сержант", "Старшина", "Прапорщик", "Лейтенант",
         "Капитан", "Майор", "Подполковник", "Полковник", "Генерал"]
R_MAJOR, R_PODPOLK, R_COLONEL, R_GENERAL = 7, 8, 9, 10
START_COINS = 1_000_000_000
GENERAL_MSGS = 1000
PRICES = {"mute": 10_000, "ban": 40_000, "warn": 15_000}
MARKET_STOCK = 100
RESTOCK_SEC = 10 * 86400
LISTING_TTL = 2 * 86400
DUEL_WIN_COINS = 100
MATH_REWARD = 10
GROUPS = ("group", "supergroup")

FULL = ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True,
                       can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                       can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                       can_add_web_page_previews=True, can_invite_users=True)
MUTED = ChatPermissions(can_send_messages=False)

# ---------- мат-фильтр: начала слов (можно дополнять) ----------
BAD_STEMS = ["хуй", "хуе", "хуя", "хуё", "хуи", "пизд", "бляд", "блят", "блять", "ебан", "ебат", "ебал",
             "ебуч", "ебну", "еблан", "ёбан", "ёбну", "заеб", "заёб", "уеб", "уёб", "наеб", "наёб",
             "долбоеб", "долбоёб", "мудак", "мудил", "пидор", "пидар", "пидр", "залуп", "гандон",
             "шлюх", "сучк", "сука", "суки", "сучар"]


def has_bad(text):
    for w in re.findall(r"[а-яё]+", text.lower()):
        if w == "бля" or any(w.startswith(s) for s in BAD_STEMS):
            return True
    return False


# ---------- база ----------
db = sqlite3.connect(os.path.join(BASE, "bot.db"), check_same_thread=False)
db.row_factory = sqlite3.Row
db.executescript("""
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT DEFAULT '', name TEXT DEFAULT '', coins INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS inv(user_id INTEGER, skin_id INTEGER, qty INTEGER, PRIMARY KEY(user_id, skin_id));
CREATE TABLE IF NOT EXISTS cases(user_id INTEGER, case_key TEXT, qty INTEGER, PRIMARY KEY(user_id, case_key));
CREATE TABLE IF NOT EXISTS chats(chat_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER);
CREATE TABLE IF NOT EXISTS members(chat_id INTEGER, user_id INTEGER, rank INTEGER DEFAULT 0, msgs INTEGER DEFAULT 0,
  warns INTEGER DEFAULT 0, oral INTEGER DEFAULT 0, muted_until INTEGER DEFAULT 0, banned INTEGER DEFAULT 0,
  PRIMARY KEY(chat_id, user_id));
CREATE TABLE IF NOT EXISTS stock(skin_id INTEGER PRIMARY KEY, qty INTEGER, restock_at INTEGER);
CREATE TABLE IF NOT EXISTS listings(id INTEGER PRIMARY KEY AUTOINCREMENT, seller INTEGER, skin_id INTEGER,
  price INTEGER, created INTEGER, status TEXT DEFAULT 'open');
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, status TEXT DEFAULT 'open', created INTEGER);
""")
db.commit()


def now():
    return int(time.time())


def one(sql, *a):
    return db.execute(sql, a).fetchone()


def allr(sql, *a):
    return db.execute(sql, a).fetchall()


def run(sql, *a):
    cur = db.execute(sql, a)
    db.commit()
    return cur


def fmt(n):
    return f"{n:,}".replace(",", " ")


def touch(u):
    if u is None or u.is_bot:
        return
    run("INSERT INTO users(id,username,name) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET "
        "username=excluded.username, name=excluded.name", u.id, (u.username or "").lower(), u.full_name)


def ensure_user(uid):
    run("INSERT OR IGNORE INTO users(id,name,username) VALUES(?,?,'')", uid, str(uid))


def name_of(uid):
    r = one("SELECT name FROM users WHERE id=?", uid)
    return r["name"] if r and r["name"] else str(uid)


def coins(uid):
    r = one("SELECT coins FROM users WHERE id=?", uid)
    return r["coins"] if r else 0


def add_coins(uid, n):
    ensure_user(uid)
    run("UPDATE users SET coins=coins+? WHERE id=?", n, uid)


def add_item(uid, sid, n=1):
    run("INSERT INTO inv VALUES(?,?,?) ON CONFLICT(user_id,skin_id) DO UPDATE SET qty=qty+?", uid, sid, n, n)


def take_item(uid, sid, n=1):
    r = one("SELECT qty FROM inv WHERE user_id=? AND skin_id=?", uid, sid)
    if not r or r["qty"] < n:
        return False
    if r["qty"] == n:
        run("DELETE FROM inv WHERE user_id=? AND skin_id=?", uid, sid)
    else:
        run("UPDATE inv SET qty=qty-? WHERE user_id=? AND skin_id=?", n, uid, sid)
    return True


def add_case(uid, key, n=1):
    run("INSERT INTO cases VALUES(?,?,?) ON CONFLICT(user_id,case_key) DO UPDATE SET qty=qty+?", uid, key, n, n)


def take_case(uid, key, n=1):
    r = one("SELECT qty FROM cases WHERE user_id=? AND case_key=?", uid, key)
    if not r or r["qty"] < n:
        return False
    if r["qty"] == n:
        run("DELETE FROM cases WHERE user_id=? AND case_key=?", uid, key)
    else:
        run("UPDATE cases SET qty=qty-? WHERE user_id=? AND case_key=?", n, uid, key)
    return True


def member(chat_id, uid):
    run("INSERT OR IGNORE INTO members(chat_id,user_id) VALUES(?,?)", chat_id, uid)
    return one("SELECT * FROM members WHERE chat_id=? AND user_id=?", chat_id, uid)


def eff_rank(chat_id, uid):
    if uid == OWNER:
        return 99
    return member(chat_id, uid)["rank"]


def resolve(arg):
    arg = arg.strip()
    if arg.startswith("@"):
        r = one("SELECT id FROM users WHERE username=?", arg[1:].lower())
        return r["id"] if r else None
    if arg.lstrip("-").isdigit():
        return int(arg)
    return None


def roll_skin(tier):
    pool = [s for s in SKINS.values() if s["tier"] == tier]
    return random.choices(pool, weights=[1 / s["price"] for s in pool])[0]


def random_case_key():
    return random.choices(["common", "rare", "epic", "legendary"], weights=[70, 20, 8, 2])[0]


async def edit(q, text, kb=None):
    try:
        await q.edit_message_text(text, reply_markup=kb)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


async def safe_send(bot, uid, text, kb=None):
    try:
        await bot.send_message(uid, text, reply_markup=kb)
        return True
    except TelegramError as e:
        log.info("send to %s failed: %s", uid, e)
        return False


# ---------- меню ----------
def menu_kb():
    return M([[B("👤 Профиль", callback_data="m:profile"), B("🎒 Инвентарь", callback_data="m:inv")],
              [B("🛒 Рынок", callback_data="mk:p:0"), B("📦 Кейсы", callback_data="m:cases")],
              [B("🎮 Игры", callback_data="m:games"), B("🔁 Трейд", callback_data="m:trade")],
              [B("🏪 Магазин", callback_data="m:shop"), B("✉️ Связь с владельцем", callback_data="m:contact")]])


BACK = [B("◀ Меню", callback_data="m:home")]
HOME_TEXT = "🎖 Главное меню"


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = update.message
    touch(m.from_user)
    if m.chat.type != "private":
        await m.reply_text("Напишите мне в личные сообщения — там меню, рынок, кейсы и магазин.")
        return
    ctx.user_data.clear()
    await m.reply_text("Привет! Здесь можно торговать скинами КС, открывать кейсы, играть и "
                       "покупать снятие наказаний.\n\n" + HOME_TEXT, reply_markup=menu_kb())


def inv_value(uid):
    return sum(SKINS[r["skin_id"]]["price"] * r["qty"] for r in allr("SELECT * FROM inv WHERE user_id=?", uid)
               if r["skin_id"] in SKINS)


async def h_menu(update, ctx, q, uid, p):
    await q.answer()
    act = p[1]
    if act == "home":
        ctx.user_data.clear()
        await edit(q, HOME_TEXT, menu_kb())
    elif act == "profile":
        rows = allr("SELECT m.rank, c.title FROM members m JOIN chats c ON c.chat_id=m.chat_id WHERE m.user_id=?", uid)
        ranks = "\n".join(f"• {r['title']}: {RANKS[r['rank']]}" for r in rows) or "• пока нет (напишите в группе с ботом)"
        n_sk = sum(r["qty"] for r in allr("SELECT qty FROM inv WHERE user_id=?", uid))
        await edit(q, f"👤 {name_of(uid)}\n💰 Монеты: {fmt(coins(uid))}\n🔫 Скинов: {n_sk} "
                      f"(на {fmt(inv_value(uid))} монет)\n\n🎖 Звания:\n{ranks}", M([BACK]))
    elif act == "inv":
        rows = allr("SELECT * FROM inv WHERE user_id=?", uid)
        lines = [f"• {SKINS[r['skin_id']]['name']} ×{r['qty']} — {fmt(SKINS[r['skin_id']]['price'])}"
                 for r in rows if r["skin_id"] in SKINS]
        cs = [f"• {CASES[r['case_key']]['name']} ×{r['qty']}" for r in allr("SELECT * FROM cases WHERE user_id=?", uid)
              if r["case_key"] in CASES]
        text = "🎒 Инвентарь\n\n🔫 Скины:\n" + ("\n".join(lines[:60]) or "пусто")
        if len(lines) > 60:
            text += f"\n… и ещё {len(lines) - 60}"
        text += "\n\n📦 Кейсы:\n" + ("\n".join(cs) or "нет")
        await edit(q, text, M([BACK]))
    elif act == "cases":
        rows, kb = [], []
        for k, c in CASES.items():
            r = one("SELECT qty FROM cases WHERE user_id=? AND case_key=?", uid, k)
            qty = r["qty"] if r else 0
            rows.append(f"{c['emoji']} {c['name']} — {fmt(c['price'])} монет (у вас: {qty})")
            if qty:
                kb.append([B(f"Открыть: {c['name']} ({qty})", callback_data=f"oc:{k}")])
        kb.append(BACK)
        await edit(q, "📦 Кейсы\n\n" + "\n".join(rows) + "\n\nКупить кейсы — в магазине. "
                      "Легендарный кейс можно выиграть в дуэли.", M(kb))
    elif act == "games":
        await edit(q, "🎮 Игры", M([[B("⚔️ Дуэль", callback_data="g:duel")],
                                    [B("➕ Математика", callback_data="g:math")],
                                    [B("❌⭕ Крестики-нолики", callback_data="g:xo")], BACK]))
    elif act == "trade":
        ctx.user_data.clear()
        ctx.user_data["state"] = "trade_user"
        await edit(q, "🔁 Трейд\n\nВведите @юзернейм или ID игрока, с которым хотите обменяться "
                      "(он должен хотя бы раз запускать бота).", M([BACK]))
    elif act == "shop":
        await show_shop(q, uid)
    elif act == "contact":
        ctx.user_data.clear()
        ctx.user_data["state"] = "contact"
        await edit(q, "✉️ Связь с владельцем\n\nНапишите одним сообщением ваш вопрос или жалобу. "
                      "Владелец получит его анонимно — без вашего имени.", M([BACK]))


async def h_open_case(update, ctx, q, uid, p):
    key = p[1]
    if key not in CASES or not take_case(uid, key):
        await q.answer("У вас нет такого кейса", show_alert=True)
        return
    await q.answer()
    s = roll_skin(key)
    add_item(uid, s["id"])
    left = one("SELECT qty FROM cases WHERE user_id=? AND case_key=?", uid, key)
    kb = []
    if left:
        kb.append([B(f"Открыть ещё ({left['qty']})", callback_data=f"oc:{key}")])
    kb.append([B("📦 Кейсы", callback_data="m:cases")])
    await edit(q, f"{CASES[key]['emoji']} {CASES[key]['name']} открыт!\n\n🎁 Выпало: {s['name']}\n"
                  f"💰 Цена: {fmt(s['price'])} монет", M(kb))


# ---------- магазин ----------
async def show_shop(q, uid):
    t = now()
    rows = allr("SELECT m.*, c.title FROM members m JOIN chats c ON c.chat_id=m.chat_id WHERE m.user_id=? AND "
                "(m.muted_until>? OR m.banned=1 OR m.warns>0 OR m.oral>0)", uid, t)
    text = f"🏪 Магазин\n💰 Баланс: {fmt(coins(uid))}\n\n"
    kb = []
    if rows:
        text += "Ваши наказания:\n"
        for r in rows:
            st = []
            if r["muted_until"] > t:
                st.append("мут")
            if r["banned"]:
                st.append("бан")
            if r["warns"]:
                st.append(f"варнов: {r['warns']}")
            if r["oral"]:
                st.append(f"устных: {r['oral']}")
            text += f"• {r['title']}: {', '.join(st)}\n"
            cid = r["chat_id"]
            if r["muted_until"] > t:
                kb.append([B(f"Снять мут — {fmt(PRICES['mute'])} ({r['title'][:15]})", callback_data=f"sh:mute:{cid}")])
            if r["banned"]:
                kb.append([B(f"Снять бан — {fmt(PRICES['ban'])} ({r['title'][:15]})", callback_data=f"sh:ban:{cid}")])
            if r["warns"] or r["oral"]:
                kb.append([B(f"Снять варн/устное — {fmt(PRICES['warn'])} ({r['title'][:15]})", callback_data=f"sh:warn:{cid}")])
    else:
        text += "Наказаний нет 🙂\n"
    text += "\nКейсы:"
    for k, c in CASES.items():
        kb.append([B(f"{c['emoji']} {c['name']} — {fmt(c['price'])}", callback_data=f"sh:case:{k}")])
    kb.append(BACK)
    await edit(q, text, M(kb))


async def h_shop(update, ctx, q, uid, p):
    act, arg = p[1], p[2]
    if act == "case":
        c = CASES.get(arg)
        if not c or coins(uid) < c["price"]:
            await q.answer("Не хватает монет", show_alert=True)
            return
        add_coins(uid, -c["price"])
        add_case(uid, arg)
        await q.answer(f"Куплен: {c['name']}", show_alert=True)
        await show_shop(q, uid)
        return
    chat_id = int(arg)
    mem = member(chat_id, uid)
    price = PRICES[act]
    if coins(uid) < price:
        await q.answer("Не хватает монет", show_alert=True)
        return
    try:
        if act == "mute":
            if mem["muted_until"] <= now():
                await q.answer("Мута нет", show_alert=True)
                return
            await ctx.bot.restrict_chat_member(chat_id, uid, FULL)
            run("UPDATE members SET muted_until=0 WHERE chat_id=? AND user_id=?", chat_id, uid)
        elif act == "ban":
            if not mem["banned"]:
                await q.answer("Бана нет", show_alert=True)
                return
            await ctx.bot.unban_chat_member(chat_id, uid, only_if_banned=True)
            run("UPDATE members SET banned=0 WHERE chat_id=? AND user_id=?", chat_id, uid)
        else:
            if mem["warns"] > 0:
                run("UPDATE members SET warns=warns-1 WHERE chat_id=? AND user_id=?", chat_id, uid)
            elif mem["oral"] > 0:
                run("UPDATE members SET oral=oral-1 WHERE chat_id=? AND user_id=?", chat_id, uid)
            else:
                await q.answer("Нечего снимать", show_alert=True)
                return
    except TelegramError as e:
        await q.answer(f"Не получилось: {e}. Возможно, бот не админ в группе.", show_alert=True)
        return
    add_coins(uid, -price)
    extra = " Вернуться в группу можно по ссылке-приглашению." if act == "ban" else ""
    await q.answer("Готово!" + extra, show_alert=True)
    await show_shop(q, uid)


# ---------- рынок ----------
PER_PAGE = 8


def market_sorted():
    return sorted(SKINS.values(), key=lambda s: (s["price"], s["id"]))


def avail(sid, exclude=0):
    st = one("SELECT qty FROM stock WHERE skin_id=?", sid)
    ls = one("SELECT COUNT(*) c FROM listings WHERE skin_id=? AND status='open' AND seller!=?", sid, exclude)
    return (st["qty"] if st else 0), ls["c"]


async def h_market(update, ctx, q, uid, p):
    act = p[1]
    lst = market_sorted()
    if act == "p":
        await q.answer()
        page = int(p[2])
        pages = (len(lst) + PER_PAGE - 1) // PER_PAGE
        kb = [[B(f"{s['name']} — {fmt(s['price'])}", callback_data=f"mk:i:{s['id']}")]
              for s in lst[page * PER_PAGE:(page + 1) * PER_PAGE]]
        nav = []
        if page > 0:
            nav.append(B("⬅", callback_data=f"mk:p:{page - 1}"))
        nav.append(B(f"{page + 1}/{pages}", callback_data="noop"))
        if page < pages - 1:
            nav.append(B("➡", callback_data=f"mk:p:{page + 1}"))
        kb.append(nav)
        kb.append([B("💰 Продать скин", callback_data="mk:sell"), B("◀ Назад", callback_data="m:home")])
        await edit(q, f"🛒 Рынок скинов\n💰 Баланс: {fmt(coins(uid))}\nВыберите скин:", M(kb))
    elif act == "i":
        await q.answer()
        s = SKINS[int(p[2])]
        st, ls = avail(s["id"], uid)
        page = [x["id"] for x in lst].index(s["id"]) // PER_PAGE
        await edit(q, f"🔫 {s['name']}\n💰 Цена: {fmt(s['price'])} монет\n📦 В наличии: {st + ls}\n"
                      f"💼 Ваш баланс: {fmt(coins(uid))}",
                   M([[B("Купить", callback_data=f"mk:buy:{s['id']}")], [B("◀ Назад", callback_data=f"mk:p:{page}")]]))
    elif act == "buy":
        s = SKINS[int(p[2])]
        if coins(uid) < s["price"]:
            await q.answer("Не хватает монет", show_alert=True)
            return
        listing = one("SELECT * FROM listings WHERE skin_id=? AND status='open' AND seller!=? ORDER BY created LIMIT 1",
                      s["id"], uid)
        if listing:
            run("UPDATE listings SET status='sold' WHERE id=?", listing["id"])
            add_coins(listing["seller"], listing["price"])
            await safe_send(ctx.bot, listing["seller"], f"✅ Ваш скин {s['name']} купили за {fmt(listing['price'])} монет!")
        else:
            st = one("SELECT qty FROM stock WHERE skin_id=?", s["id"])
            if not st or st["qty"] <= 0:
                await q.answer("Нет в наличии", show_alert=True)
                return
            run("UPDATE stock SET qty=qty-1 WHERE skin_id=?", s["id"])
            add_coins(OWNER, s["price"])
        add_coins(uid, -s["price"])
        add_item(uid, s["id"])
        await q.answer(f"Куплено: {s['name']}", show_alert=True)
        await edit(q, f"✅ Вы купили {s['name']} за {fmt(s['price'])} монет.",
                   M([[B("🛒 Рынок", callback_data="mk:p:0"), B("◀ Меню", callback_data="m:home")]]))
    elif act == "sell":
        await q.answer()
        rows = allr("SELECT * FROM inv WHERE user_id=?", uid)
        kb = [[B(f"{SKINS[r['skin_id']]['name']} ×{r['qty']} — {fmt(SKINS[r['skin_id']]['price'])}",
                 callback_data=f"mk:sl:{r['skin_id']}")] for r in rows if r["skin_id"] in SKINS][:40]
        kb.append([B("◀ Назад", callback_data="mk:p:0")])
        await edit(q, "💰 Продать скин\nВыберите скин из инвентаря:" if len(kb) > 1 else "У вас нет скинов для продажи.", M(kb))
    elif act == "sl":
        await q.answer()
        s = SKINS[int(p[2])]
        await edit(q, f"💰 Продажа: {s['name']}\nСредняя цена рынка: {fmt(s['price'])} монет.\n\n"
                      "Скин будет выставлен на рынок. Если его не купят в течение 2 дней — купит бот.",
                   M([[B("✅ Выставить", callback_data=f"mk:ok:{s['id']}")], [B("◀ Назад", callback_data="mk:sell")]]))
    elif act == "ok":
        s = SKINS[int(p[2])]
        if not take_item(uid, s["id"]):
            await q.answer("Скина нет в инвентаре", show_alert=True)
            return
        run("INSERT INTO listings(seller,skin_id,price,created) VALUES(?,?,?,?)", uid, s["id"], s["price"], now())
        await q.answer("Выставлено!", show_alert=True)
        await edit(q, f"✅ {s['name']} выставлен за {fmt(s['price'])} монет. Уведомлю, когда купят.",
                   M([[B("🛒 Рынок", callback_data="mk:p:0"), B("◀ Меню", callback_data="m:home")]]))


async def market_job(ctx: ContextTypes.DEFAULT_TYPE):
    t = now()
    run("UPDATE stock SET qty=?, restock_at=? WHERE restock_at<=?", MARKET_STOCK, t + RESTOCK_SEC, t)
    for l in allr("SELECT * FROM listings WHERE status='open' AND created<=?", t - LISTING_TTL):
        run("UPDATE listings SET status='bot' WHERE id=?", l["id"])
        add_coins(l["seller"], l["price"])
        run("UPDATE stock SET qty=qty+1 WHERE skin_id=?", l["skin_id"])
        await safe_send(ctx.bot, l["seller"], f"🤖 Ваш скин {SKINS[l['skin_id']]['name']} никто не купил за 2 дня — "
                                              f"его выкупил бот за {fmt(l['price'])} монет.")


# ---------- игры ----------
DUELS, XO, TRADES = {}, {}, {}
_counter = [0]


def next_id():
    _counter[0] += 1
    return _counter[0]


async def h_games(update, ctx, q, uid, p):
    await q.answer()
    act = p[1]
    if act == "duel":
        await edit(q, "⚔️ Дуэль 1 на 1 (в группе с ботом)\n\nКоманды:\n"
                      "/searchduel — найти соперника, внизу появится кнопка «Присоединиться»\n"
                      "/searchduel @ник — пригласить конкретного игрока\n\n"
                      "Игроки по очереди жмут «Стрелять»: голова 30% — победа, воздух 65% — мимо, "
                      "рука 45% — соперник пропускает ход (шансы приводятся к 100%).\n"
                      f"Победитель получает {DUEL_WIN_COINS} монет и кейс.", M([[B("◀ Игры", callback_data="m:games")]]))
    elif act == "xo":
        await edit(q, "❌⭕ Крестики-нолики\n\nС ботом — кнопка ниже. С игроком — команда /xo в группе.",
                   M([[B("Играть с ботом", callback_data="xo:new")], [B("◀ Игры", callback_data="m:games")]]))
    elif act == "math":
        await send_math(q.message, ctx, first=True)
    elif act == "mathstop":
        ctx.user_data.pop("math", None)
        await edit(q, "Математика остановлена.", M([[B("◀ Игры", callback_data="m:games")]]))


def gen_math():
    g = random.randint(1, 4)
    if g == 1:
        a, b = random.randint(1, 10), random.randint(1, 10)
        return (f"{a} + {b}", a + b) if random.random() < 0.5 else (f"{a + b} - {b}", a)
    if g == 2:
        a = random.randint(10, 90)
        b = random.randint(1, 99 - a)
        return (f"{a} + {b}", a + b) if random.random() < 0.5 else (f"{a + b} - {b}", a)
    if g == 3:
        a, b = random.randint(2, 9), random.randint(2, 9)
        return (f"{a} × {b}", a * b) if random.random() < 0.6 else (f"{a * b} ÷ {b}", a)
    k = random.randint(1, 3)
    if k == 1:
        a, b = random.randint(11, 99), random.randint(2, 9)
        return f"{a} × {b}", a * b
    if k == 2:
        b, c = random.randint(3, 9), random.randint(11, 30)
        return f"{b * c} ÷ {b}", c
    a, b, c = random.randint(2, 20), random.randint(2, 20), random.randint(2, 5)
    return f"({a} + {b}) × {c}", (a + b) * c


async def send_math(message, ctx, first=False, prefix=""):
    ex, ans = gen_math()
    ctx.user_data["math"] = ans
    ctx.user_data.pop("state", None)
    head = "➕ Математика (1–4 классы). Присылайте ответ числом.\n\n" if first else ""
    await message.reply_text(f"{prefix}{head}Сколько будет: {ex} ?",
                             reply_markup=M([[B("Стоп", callback_data="g:mathstop")]]))


# --- дуэль ---
async def searchduel(update, ctx):
    m = update.message
    touch(m.from_user)
    if m.chat.type not in GROUPS:
        await m.reply_text("Дуэли проходят в группе. Добавьте меня в группу и напишите там /searchduel")
        return
    inv = ctx.args[0][1:].lower() if ctx.args and ctx.args[0].startswith("@") else None
    did = next_id()
    DUELS[did] = {"p": [m.from_user.id], "names": {m.from_user.id: m.from_user.full_name}, "inv": inv,
                  "turn": None, "log": [], "state": "wait"}
    text = f"⚔️ {m.from_user.full_name} ищет соперника для дуэли!"
    if inv:
        text += f"\nПриглашён: @{inv}"
    await m.reply_text(text, reply_markup=M([[B("Присоединиться", callback_data=f"dl:j:{did}")]]))


def duel_text(d):
    a, b = d["p"]
    return (f"⚔️ Дуэль: {d['names'][a]} vs {d['names'][b]}\nХод: {d['names'][d['turn']]}\n\n" + "\n".join(d["log"][-4:]))


async def h_duel(update, ctx, q, uid, p):
    act, did = p[1], int(p[2])
    d = DUELS.get(did)
    if not d:
        await q.answer("Дуэль недоступна", show_alert=True)
        return
    if act == "j":
        if d["state"] != "wait":
            await q.answer("Дуэль уже началась", show_alert=True)
            return
        if uid == d["p"][0]:
            await q.answer("Нужен другой игрок", show_alert=True)
            return
        if d["inv"] and (q.from_user.username or "").lower() != d["inv"]:
            await q.answer("Эта дуэль для другого игрока", show_alert=True)
            return
        touch(q.from_user)
        d["p"].append(uid)
        d["names"][uid] = q.from_user.full_name
        d["state"] = "play"
        d["turn"] = random.choice(d["p"])
        d["log"].append("Дуэль началась!")
        await q.answer()
        await edit(q, duel_text(d), M([[B("🔫 Стрелять", callback_data=f"dl:s:{did}")]]))
        return
    if d["state"] != "play":
        await q.answer()
        return
    if uid != d["turn"]:
        await q.answer("Сейчас не ваш ход", show_alert=True)
        return
    await q.answer()
    opp = d["p"][1] if d["p"][0] == uid else d["p"][0]
    me, him = d["names"][uid], d["names"][opp]
    res = random.choices(["head", "air", "arm"], weights=[30, 65, 45])[0]
    if res == "head":
        DUELS.pop(did, None)
        add_coins(uid, DUEL_WIN_COINS)
        key = random_case_key()
        add_case(uid, key)
        await edit(q, f"⚔️ Дуэль: {me} vs {him}\n\n💥 {me} попал в голову!\n\n🏆 Победил {me}: "
                      f"+{DUEL_WIN_COINS} монет и {CASES[key]['name']}!")
        return
    if res == "air":
        d["log"].append(f"{me} выстрелил в воздух 💨")
        d["turn"] = opp
    else:
        d["log"].append(f"{me} попал {him} в руку — {him} пропускает ход 🩸")
    await edit(q, duel_text(d), M([[B("🔫 Стрелять", callback_data=f"dl:s:{did}")]]))


# --- крестики-нолики ---
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
SYM = {"X": "❌", "O": "⭕", ".": "⬜"}


def xo_winner(b):
    for i, j, k in LINES:
        if b[i] != "." and b[i] == b[j] == b[k]:
            return b[i]
    return None


def xo_kb(gid, g):
    return M([[B(SYM[g["b"][r * 3 + c]], callback_data=f"xo:m:{gid}:{r * 3 + c}") for c in range(3)] for r in range(3)])


def xo_bot_move(b):
    empty = [i for i in range(9) if b[i] == "."]
    for s in ("O", "X"):
        for i in empty:
            b[i] = s
            w = xo_winner(b)
            b[i] = "."
            if w == s:
                return i
    if b[4] == ".":
        return 4
    corners = [i for i in (0, 2, 6, 8) if b[i] == "."]
    return random.choice(corners or empty)


def xo_text(g):
    return f"❌⭕ {g['names']['X']} (❌) vs {g['names']['O']} (⭕)\nХод: {g['names'][g['turn']]} ({SYM[g['turn']]})"


async def xo_group(update, ctx):
    m = update.message
    touch(m.from_user)
    if m.chat.type not in GROUPS:
        await m.reply_text("Команда /xo работает в группе. Игра с ботом — в меню «Игры».")
        return
    gid = next_id()
    XO[gid] = {"b": ["."] * 9, "p": {"X": m.from_user.id, "O": None}, "names": {"X": m.from_user.full_name, "O": "?"},
               "turn": "X", "bot": False, "state": "wait"}
    await m.reply_text(f"❌⭕ {m.from_user.full_name} ищет соперника!",
                       reply_markup=M([[B("Присоединиться", callback_data=f"xo:j:{gid}")]]))


async def h_xo(update, ctx, q, uid, p):
    act = p[1]
    if act == "new":
        await q.answer()
        gid = next_id()
        XO[gid] = {"b": ["."] * 9, "p": {"X": uid, "O": 0}, "names": {"X": q.from_user.full_name, "O": "Бот"},
                   "turn": "X", "bot": True, "state": "play"}
        await edit(q, xo_text(XO[gid]), xo_kb(gid, XO[gid]))
        return
    gid = int(p[2])
    g = XO.get(gid)
    if not g:
        await q.answer("Игра недоступна", show_alert=True)
        return
    if act == "j":
        if g["state"] != "wait" or uid == g["p"]["X"]:
            await q.answer("Нужен другой игрок", show_alert=True)
            return
        touch(q.from_user)
        g["p"]["O"] = uid
        g["names"]["O"] = q.from_user.full_name
        g["state"] = "play"
        await q.answer()
        await edit(q, xo_text(g), xo_kb(gid, g))
        return
    cell = int(p[3])
    if g["state"] != "play" or g["p"][g["turn"]] != uid:
        await q.answer("Сейчас не ваш ход", show_alert=True)
        return
    if g["b"][cell] != ".":
        await q.answer("Клетка занята", show_alert=True)
        return
    await q.answer()
    g["b"][cell] = g["turn"]
    w = xo_winner(g["b"])
    if not w and "." in g["b"] and g["bot"]:
        g["b"][xo_bot_move(g["b"])] = "O"
        w = xo_winner(g["b"])
        g["turn"] = "X"
    elif not w:
        g["turn"] = "O" if g["turn"] == "X" else "X"
    if w or "." not in g["b"]:
        XO.pop(gid, None)
        res = f"🏆 Победил {g['names'][w]} ({SYM[w]})" if w else "🤝 Ничья"
        rows = [[B(SYM[g["b"][r * 3 + c]], callback_data="noop") for c in range(3)] for r in range(3)]
        if g["bot"]:
            rows.append([B("Ещё раз", callback_data="xo:new"), B("◀ Игры", callback_data="m:games")])
        await edit(q, f"❌⭕ {g['names']['X']} vs {g['names']['O']}\n\n{res}", M(rows))
        return
    await edit(q, xo_text(g), xo_kb(gid, g))


# ---------- трейд ----------
def desc(kind, val, qty):
    if kind == "coins":
        return f"{fmt(qty)} монет"
    if kind == "skin":
        return f"скин {SKINS[val]['name']} ×{qty}"
    return f"{CASES[val]['name']} ×{qty}"


async def send_offer(ctx, uid, kind, val, qty):
    to = ctx.user_data.get("trade", {}).get("to")
    if not to:
        return "Сессия трейда устарела, начните заново."
    ok = (coins(uid) >= qty) if kind == "coins" else False
    if kind == "skin":
        r = one("SELECT qty FROM inv WHERE user_id=? AND skin_id=?", uid, val)
        ok = bool(r and r["qty"] >= qty)
    elif kind == "case":
        r = one("SELECT qty FROM cases WHERE user_id=? AND case_key=?", uid, val)
        ok = bool(r and r["qty"] >= qty)
    if not ok:
        return "Недостаточно ресурсов для передачи."
    tid = next_id()
    TRADES[tid] = {"from": uid, "to": to, "kind": kind, "val": val, "qty": qty}
    sent = await safe_send(ctx.bot, to, f"🔁 {name_of(uid)} хочет передать вам: {desc(kind, val, qty)}",
                           M([[B("✅ Принять", callback_data=f"td:y:{tid}"), B("❌ Отказать", callback_data=f"td:n:{tid}")]]))
    ctx.user_data.clear()
    if not sent:
        TRADES.pop(tid, None)
        return "Не удалось отправить: игрок ещё не запускал бота."
    return f"✅ Предложение отправлено игроку {name_of(to)}: {desc(kind, val, qty)}. Ждём ответа."


async def h_trade(update, ctx, q, uid, p):
    act = p[1]
    if "trade" not in ctx.user_data:
        await q.answer("Сессия устарела", show_alert=True)
        return
    await q.answer()
    if act == "c":
        ctx.user_data["state"] = "trade_amount"
        await edit(q, f"Сколько монет передать? У вас {fmt(coins(uid))}. Напишите число.", M([BACK]))
    elif act == "s":
        rows = allr("SELECT * FROM inv WHERE user_id=?", uid)
        kb = [[B(f"{SKINS[r['skin_id']]['name']} ×{r['qty']}", callback_data=f"tr:sk:{r['skin_id']}")]
              for r in rows if r["skin_id"] in SKINS][:40] + [BACK]
        await edit(q, "Выберите скин (передаётся 1 шт.):", M(kb))
    elif act == "k":
        rows = allr("SELECT * FROM cases WHERE user_id=?", uid)
        kb = [[B(f"{CASES[r['case_key']]['name']} ×{r['qty']}", callback_data=f"tr:cs:{r['case_key']}")]
              for r in rows if r["case_key"] in CASES] + [BACK]
        await edit(q, "Выберите кейс (передаётся 1 шт.):", M(kb))
    elif act == "sk":
        await edit(q, await send_offer(ctx, uid, "skin", int(p[2]), 1), M([BACK]))
    elif act == "cs":
        await edit(q, await send_offer(ctx, uid, "case", p[2], 1), M([BACK]))


async def h_trade_reply(update, ctx, q, uid, p):
    t = TRADES.pop(int(p[2]), None)
    if not t or t["to"] != uid:
        await q.answer("Предложение недоступно", show_alert=True)
        return
    await q.answer()
    if p[1] == "n":
        await edit(q, "❌ Вы отказались от обмена.")
        await safe_send(ctx.bot, t["from"], f"❌ {name_of(uid)} отказался от вашего предложения.")
        return
    a, kind, val, qty = t["from"], t["kind"], t["val"], t["qty"]
    if kind == "coins":
        ok = coins(a) >= qty
        if ok:
            add_coins(a, -qty)
            add_coins(uid, qty)
    elif kind == "skin":
        ok = take_item(a, val, qty)
        if ok:
            add_item(uid, val, qty)
    else:
        ok = take_case(a, val, qty)
        if ok:
            add_case(uid, val, qty)
    if not ok:
        await edit(q, "У отправителя больше нет этого. Обмен отменён.")
        return
    await edit(q, f"✅ Вы получили: {desc(kind, val, qty)}")
    await safe_send(ctx.bot, a, f"✅ {name_of(uid)} принял: {desc(kind, val, qty)}")


# ---------- связь с владельцем ----------
def owner_kb(tid):
    return M([[B("💬 Ответить", callback_data=f"tk:r:{tid}"), B("🤖 Автоответчик", callback_data=f"tk:a:{tid}")]])


async def h_ticket(update, ctx, q, uid, p):
    act, tid = p[1], int(p[2])
    t = one("SELECT * FROM tickets WHERE id=?", tid)
    if act == "u":  # пользователь дописывает
        if not t or t["user_id"] != uid or t["status"] != "open":
            await q.answer("Тема закрыта", show_alert=True)
            return
        await q.answer()
        ctx.user_data["state"] = "contact_reply"
        ctx.user_data["tid"] = tid
        await q.message.reply_text("Напишите ответ — он уйдёт владельцу анонимно.")
        return
    if uid != OWNER:
        await q.answer("Только для владельца", show_alert=True)
        return
    if not t or t["status"] != "open":
        await q.answer("Тема закрыта", show_alert=True)
        return
    await q.answer()
    ctx.user_data["state"] = "owner_reply" if act == "r" else "owner_auto"
    ctx.user_data["tid"] = tid
    await q.message.reply_text(f"Обращение #{tid}: напишите ответ." if act == "r" else
                               f"Обращение #{tid}: опишите причину и дату, когда сможете ответить.")


async def verdict_cmd(update, ctx):
    m = update.message
    if m.from_user.id != OWNER or m.chat.type != "private":
        return
    if not ctx.args or not ctx.args[0].isdigit():
        await m.reply_text("Использование: /verdict НОМЕР")
        return
    tid = int(ctx.args[0])
    t = one("SELECT * FROM tickets WHERE id=?", tid)
    if not t or t["status"] != "open":
        await m.reply_text("Такой открытой темы нет.")
        return
    await m.reply_text(f"Вердикт по обращению #{tid}:",
                       reply_markup=M([[B("✅ Одобрено", callback_data=f"vd:y:{tid}"),
                                        B("❌ Отказано", callback_data=f"vd:n:{tid}")]]))


async def h_verdict(update, ctx, q, uid, p):
    if uid != OWNER:
        await q.answer("Только для владельца", show_alert=True)
        return
    tid = int(p[2])
    t = one("SELECT * FROM tickets WHERE id=?", tid)
    if not t or t["status"] != "open":
        await q.answer("Тема уже закрыта", show_alert=True)
        return
    await q.answer()
    run("UPDATE tickets SET status='closed' WHERE id=?", tid)
    word = "одобрено ✅" if p[1] == "y" else "отказано ❌"
    await safe_send(ctx.bot, t["user_id"], f"Обращение #{tid}: {word}. Тема закрыта.")
    await edit(q, f"Обращение #{tid} закрыто: {word}")


# ---------- личные сообщения ----------
async def private_text(update, ctx):
    m = update.message
    uid = m.from_user.id
    touch(m.from_user)
    t = m.text.strip()
    st = ctx.user_data.get("state")
    if st in ("contact", "contact_reply"):
        if st == "contact":
            tid = run("INSERT INTO tickets(user_id,created) VALUES(?,?)", uid, now()).lastrowid
            head = f"📩 Обращение #{tid}\nКто-то хочет связаться с вами:"
        else:
            tid = ctx.user_data.get("tid")
            head = f"📩 Обращение #{tid} — новое сообщение от анонима:"
        ctx.user_data.clear()
        if await safe_send(ctx.bot, OWNER, f"{head}\n\n{t}", owner_kb(tid)):
            await m.reply_text(f"✅ Отправлено анонимно (обращение #{tid}). Ответ придёт сюда.", reply_markup=menu_kb())
        else:
            await m.reply_text("Владелец пока недоступен. Попробуйте позже.", reply_markup=menu_kb())
    elif st in ("owner_reply", "owner_auto") and uid == OWNER:
        tid = ctx.user_data.pop("tid")
        ctx.user_data.pop("state")
        tk = one("SELECT * FROM tickets WHERE id=?", tid)
        if st == "owner_reply":
            await safe_send(ctx.bot, tk["user_id"], f"💬 Ответ владельца по обращению #{tid}:\n\n{t}",
                            M([[B("Ответить", callback_data=f"tk:u:{tid}")]]))
        else:
            await safe_send(ctx.bot, tk["user_id"], f"🤖 Автоответчик (обращение #{tid})\nВладелец сейчас не может "
                                                    f"ответить.\n\n{t}", M([[B("Ответить", callback_data=f"tk:u:{tid}")]]))
        await m.reply_text(f"Отправлено. Закрыть тему: /verdict {tid}")
    elif st == "trade_user":
        to = resolve(t)
        if not to or not one("SELECT 1 FROM users WHERE id=?", to):
            await m.reply_text("Игрок не найден. Он должен хотя бы раз запускать бота. Попробуйте ещё раз.")
        elif to == uid:
            await m.reply_text("Нельзя торговать с собой.")
        else:
            ctx.user_data["trade"] = {"to": to}
            ctx.user_data["state"] = None
            await m.reply_text(f"Что передать игроку {name_of(to)}?",
                               reply_markup=M([[B("💰 Монеты", callback_data="tr:c"), B("🔫 Скин", callback_data="tr:s"),
                                                B("📦 Кейс", callback_data="tr:k")], BACK]))
    elif st == "trade_amount":
        if not t.isdigit() or int(t) <= 0:
            await m.reply_text("Введите положительное число.")
        else:
            ctx.user_data["state"] = None
            await m.reply_text(await send_offer(ctx, uid, "coins", None, int(t)), reply_markup=menu_kb())
    elif "math" in ctx.user_data:
        if t.lstrip("-").isdigit() and int(t) == ctx.user_data["math"]:
            add_coins(uid, MATH_REWARD)
            await send_math(m, ctx, prefix=f"✅ Верно! +{MATH_REWARD} монет\n\n")
        else:
            await m.reply_text("❌ Неверно, попробуйте ещё раз.")
    else:
        await m.reply_text(HOME_TEXT, reply_markup=menu_kb())


# ---------- группа: регистрация, звания, наказания ----------
_reg_fail = {}


async def register_chat(ctx, chat):
    if one("SELECT 1 FROM chats WHERE chat_id=?", chat.id):
        return
    if now() - _reg_fail.get(chat.id, 0) < 300:
        return
    _reg_fail[chat.id] = now()
    try:
        admins = await ctx.bot.get_chat_administrators(chat.id)
    except TelegramError as e:
        log.info("admins error: %s", e)
        return
    owner = next((a for a in admins if a.status == "creator"), None)
    if not owner:
        return
    ou = owner.user
    touch(ou)
    run("INSERT INTO chats VALUES(?,?,?)", chat.id, chat.title or str(chat.id), ou.id)
    member(chat.id, ou.id)
    run("UPDATE members SET rank=? WHERE chat_id=? AND user_id=?", R_COLONEL, chat.id, ou.id)
    add_coins(ou.id, START_COINS)
    await ctx.bot.send_message(chat.id, f"🎖 Владелец группы {ou.full_name} становится Полковником и "
                                        f"получает {fmt(START_COINS)} монет!")


async def on_my_chat_member(update, ctx):
    c = update.my_chat_member
    if c.chat.type in GROUPS and c.new_chat_member.status in ("member", "administrator"):
        await register_chat(ctx, c.chat)


async def init_cmd(update, ctx):
    if update.message.chat.type in GROUPS:
        await register_chat(ctx, update.message.chat)


async def group_text(update, ctx):
    m = update.message
    u = m.from_user
    if not u or u.is_bot or not m.text:
        return
    touch(u)
    chat = m.chat
    await register_chat(ctx, chat)
    row = one("SELECT * FROM chats WHERE chat_id=?", chat.id)
    if not row:
        return
    mem = member(chat.id, u.id)
    run("UPDATE members SET msgs=msgs+1 WHERE chat_id=? AND user_id=?", chat.id, u.id)
    if mem["rank"] == R_COLONEL and mem["msgs"] + 1 >= GENERAL_MSGS:
        run("UPDATE members SET rank=? WHERE chat_id=? AND user_id=?", R_GENERAL, chat.id, u.id)
        text = f"🎖 {u.full_name} выполнил задание ({GENERAL_MSGS} сообщений) и получает звание Генерал!"
        if u.id == row["owner_id"]:
            knives = [s for s in SKINS.values() if s["tier"] == "legendary" and
                      any(w in s["name"] for w in ("Knife", "Bayonet", "Karambit"))]
            got = [random.choice(knives) for _ in range(3)]
            for s in got:
                add_item(u.id, s["id"])
            text += "\n🔪 Награда — 3 ножа: " + ", ".join(s["name"] for s in got)
        await m.reply_text(text)
    if u.id != row["owner_id"] and u.id != OWNER and has_bad(m.text):
        await safe_send(ctx.bot, row["owner_id"],
                        f"⚠️ В чате «{chat.title}» {u.full_name}" + (f" (@{u.username})" if u.username else "") +
                        f" написал плохое слово:\n«{m.text[:300]}»\n\nЧто с ним делать?",
                        M([[B("🔇 Мут 60 мин", callback_data=f"bd:m:{chat.id}:{u.id}"),
                            B("📢 Устное пред.", callback_data=f"bd:p:{chat.id}:{u.id}")],
                           [B("Игнорировать", callback_data=f"bd:i:{chat.id}:{u.id}")]]))


async def do_mute(bot, chat_id, uid, minutes):
    until = now() + minutes * 60
    await bot.restrict_chat_member(chat_id, uid, MUTED, until_date=until)
    run("UPDATE members SET muted_until=? WHERE chat_id=? AND user_id=?", until, chat_id, uid)


def do_oral(chat_id, uid):
    """+1 устное предупреждение; 3 устных = 1 варн. Возвращает текст."""
    mem = member(chat_id, uid)
    oral = mem["oral"] + 1
    if oral >= 3:
        run("UPDATE members SET oral=0, warns=warns+1 WHERE chat_id=? AND user_id=?", chat_id, uid)
        return "3 устных предупреждения → выдан 1 варн"
    run("UPDATE members SET oral=? WHERE chat_id=? AND user_id=?", oral, chat_id, uid)
    return f"устное предупреждение ({oral}/3)"


async def h_badword(update, ctx, q, uid, p):
    if uid != OWNER and not one("SELECT 1 FROM chats WHERE chat_id=? AND owner_id=?", int(p[2]), uid):
        await q.answer("Нет прав", show_alert=True)
        return
    await q.answer()
    chat_id, target = int(p[2]), int(p[3])
    if p[1] == "m":
        try:
            await do_mute(ctx.bot, chat_id, target, 60)
            res = "мут на 60 минут"
        except TelegramError as e:
            res = f"не удалось замутить ({e}) — сделайте бота админом"
    elif p[1] == "p":
        res = do_oral(chat_id, target)
        await safe_send(ctx.bot, chat_id, f"📢 {name_of(target)}: {res} за нецензурную лексику.")
    else:
        res = "проигнорировано"
    await edit(q, f"{q.message.text}\n\n✅ Решение: {res}")


MOD_NEED = {"mute": R_MAJOR, "unmute": R_MAJOR, "warn": R_PODPOLK, "unwarn": R_COLONEL,
            "pred": R_COLONEL, "ban": R_COLONEL, "unban": R_COLONEL}


async def mod_cmd(update, ctx):
    m = update.message
    if m.chat.type not in GROUPS:
        return
    cmd = m.text.split()[0].lstrip("/").split("@")[0].lower()
    touch(m.from_user)
    if not m.reply_to_message or not m.reply_to_message.from_user:
        await m.reply_text("Ответьте этой командой на сообщение игрока.")
        return
    actor, target = m.from_user.id, m.reply_to_message.from_user
    if target.is_bot or target.id == actor:
        await m.reply_text("Нельзя применить к боту или к себе.")
        return
    touch(target)
    ra, rt = eff_rank(m.chat.id, actor), eff_rank(m.chat.id, target.id)
    if ra < MOD_NEED[cmd]:
        await m.reply_text(f"Нужно звание {RANKS[MOD_NEED[cmd]]} или выше.")
        return
    if rt >= ra:
        await m.reply_text("Нельзя наказать игрока с равным или более высоким званием.")
        return
    cid, tid, nm = m.chat.id, target.id, target.full_name
    try:
        if cmd == "mute":
            mins = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 60
            await do_mute(ctx.bot, cid, tid, mins)
            await m.reply_text(f"🔇 {nm} в муте на {mins} мин.")
        elif cmd == "unmute":
            await ctx.bot.restrict_chat_member(cid, tid, FULL)
            run("UPDATE members SET muted_until=0 WHERE chat_id=? AND user_id=?", cid, tid)
            await m.reply_text(f"🔊 Мут с {nm} снят.")
        elif cmd == "warn":
            run("UPDATE members SET warns=warns+1 WHERE chat_id=? AND user_id=?", cid, tid)
            await m.reply_text(f"⚠️ {nm} получил варн. Всего варнов: {member(cid, tid)['warns']}")
        elif cmd == "pred":
            await m.reply_text(f"📢 {nm}: {do_oral(cid, tid)}")
        elif cmd == "unwarn":
            mem = member(cid, tid)
            if mem["warns"] > 0:
                run("UPDATE members SET warns=warns-1 WHERE chat_id=? AND user_id=?", cid, tid)
            elif mem["oral"] > 0:
                run("UPDATE members SET oral=oral-1 WHERE chat_id=? AND user_id=?", cid, tid)
            await m.reply_text(f"✅ Предупреждение снято с {nm}.")
        elif cmd == "ban":
            await ctx.bot.ban_chat_member(cid, tid)
            run("UPDATE members SET banned=1 WHERE chat_id=? AND user_id=?", cid, tid)
            await m.reply_text(f"⛔ {nm} забанен.")
        elif cmd == "unban":
            await ctx.bot.unban_chat_member(cid, tid, only_if_banned=True)
            run("UPDATE members SET banned=0 WHERE chat_id=? AND user_id=?", cid, tid)
            await m.reply_text(f"✅ {nm} разбанен.")
    except TelegramError as e:
        await m.reply_text(f"Не получилось: {e}\nСделайте бота админом с правом ограничивать участников.")


async def rank_cmd(update, ctx):
    m = update.message
    if m.chat.type not in GROUPS or not m.reply_to_message or not ctx.args:
        await m.reply_text("В группе, ответом на сообщение: /rank название (например /rank сержант) или /rank 1–11")
        return
    row = one("SELECT owner_id FROM chats WHERE chat_id=?", m.chat.id)
    if m.from_user.id != OWNER and not (row and row["owner_id"] == m.from_user.id):
        await m.reply_text("Звания выдаёт владелец чата.")
        return
    a = ctx.args[0].lower()
    idx = int(a) - 1 if a.isdigit() else next((i for i, r in enumerate(RANKS) if r.lower() == a), None)
    if idx is None or not 0 <= idx < len(RANKS):
        await m.reply_text("Звания: " + ", ".join(f"{i + 1}. {r}" for i, r in enumerate(RANKS)))
        return
    t = m.reply_to_message.from_user
    touch(t)
    member(m.chat.id, t.id)
    run("UPDATE members SET rank=? WHERE chat_id=? AND user_id=?", idx, m.chat.id, t.id)
    await m.reply_text(f"🎖 {t.full_name} теперь {RANKS[idx]}")


# ---------- команды владельца ----------
def owner_only(fn):
    async def w(update, ctx):
        if update.effective_user and update.effective_user.id == OWNER:
            await fn(update, ctx)
    return w


def target_args(m, ctx):
    if m.reply_to_message and m.reply_to_message.from_user:
        touch(m.reply_to_message.from_user)
        return m.reply_to_message.from_user.id, list(ctx.args)
    if not ctx.args:
        return None, []
    return resolve(ctx.args[0]), list(ctx.args[1:])


@owner_only
async def givecoins(update, ctx):
    m = update.message
    to, a = target_args(m, ctx)
    if not to or not a or not a[0].lstrip("-").isdigit():
        await m.reply_text("/givecoins @ник|ID сумма (или ответом на сообщение)")
        return
    add_coins(to, int(a[0]))
    await m.reply_text(f"💰 {name_of(to)}: {int(a[0]):+d} монет, баланс {fmt(coins(to))}")


@owner_only
async def giveskin(update, ctx):
    m = update.message
    to, a = target_args(m, ctx)
    if not to or not a or not a[0].isdigit() or int(a[0]) not in SKINS:
        await m.reply_text("/giveskin @ник|ID номер_скина [кол-во]. Список номеров: /skins")
        return
    n = int(a[1]) if len(a) > 1 and a[1].isdigit() else 1
    add_item(to, int(a[0]), n)
    await m.reply_text(f"🔫 {name_of(to)} получил {SKINS[int(a[0])]['name']} ×{n}")


@owner_only
async def givecase(update, ctx):
    m = update.message
    to, a = target_args(m, ctx)
    if not to or not a or a[0] not in CASES:
        await m.reply_text("/givecase @ник|ID common|rare|epic|legendary [кол-во]")
        return
    n = int(a[1]) if len(a) > 1 and a[1].isdigit() else 1
    add_case(to, a[0], n)
    await m.reply_text(f"📦 {name_of(to)} получил {CASES[a[0]]['name']} ×{n}")


@owner_only
async def skins_cmd(update, ctx):
    lines = [f"{s['id']}. {s['name']} — {fmt(s['price'])}" for s in SKINS.values()]
    chunk = ""
    for l in lines:
        if len(chunk) + len(l) > 3800:
            await update.message.reply_text(chunk)
            chunk = ""
        chunk += l + "\n"
    await update.message.reply_text(chunk)


# ---------- диспетчер ----------
async def noop(update, ctx, q, uid, p):
    await q.answer()


ROUTES = {"m": h_menu, "oc": h_open_case, "sh": h_shop, "mk": h_market, "g": h_games, "dl": h_duel, "xo": h_xo,
          "tr": h_trade, "td": h_trade_reply, "tk": h_ticket, "vd": h_verdict, "bd": h_badword, "noop": noop}


async def cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    touch(q.from_user)
    p = q.data.split(":")
    h = ROUTES.get(p[0])
    try:
        if h:
            await h(update, ctx, q, q.from_user.id, p)
        else:
            await q.answer()
    except TelegramError as e:
        log.warning("callback %s failed: %s", q.data, e)


async def on_error(update, ctx):
    log.error("Ошибка: %s", ctx.error, exc_info=ctx.error)


async def market_loop(app):
    class _Ctx:
        bot = app.bot
    await asyncio.sleep(10)
    while True:
        try:
            await market_job(_Ctx)
        except Exception as e:
            log.warning("market_job: %s", e)
        await asyncio.sleep(300)


async def post_init(app):
    app.bot_data["market_task"] = asyncio.create_task(market_loop(app))


def main():
    for s in SKINS.values():
        run("INSERT OR IGNORE INTO stock VALUES(?,?,?)", s["id"], MARKET_STOCK, now() + RESTOCK_SEC)
    ensure_user(OWNER)
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("searchduel", searchduel))
    app.add_handler(CommandHandler("xo", xo_group))
    app.add_handler(CommandHandler("init", init_cmd))
    app.add_handler(CommandHandler(list(MOD_NEED), mod_cmd))
    app.add_handler(CommandHandler("rank", rank_cmd))
    app.add_handler(CommandHandler("verdict", verdict_cmd))
    app.add_handler(CommandHandler("givecoins", givecoins))
    app.add_handler(CommandHandler("giveskin", giveskin))
    app.add_handler(CommandHandler("givecase", givecase))
    app.add_handler(CommandHandler("skins", skins_cmd))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(ChatMemberHandler(on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, private_text))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, group_text))
    app.add_error_handler(on_error)
    log.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
