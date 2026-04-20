import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from openai import AsyncOpenAI

TELEGRAM_TOKEN = "7997006661:AAERQ3n4flz1-ZyQgUsoZY222nJyGAd7SKs"
client = AsyncOpenAI(api_key="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")

PROMPT = """Ты Angel AI. Анализируй задачи предпринимателя. Отвечай ТОЛЬКО JSON без текста. Формат: {"tasks": [{"task": "название", "profit": число 1-100, "minutes": число, "priority": "Делать сейчас" или "Делать сегодня" или "Делегировать" или "Отложить" или "После работы", "reason": "одно предложение", "warning": "одно предложение"}]}. Правила: 70+ прибыль = Делать сейчас, 45-69 = Делать сегодня, 20-44 = Делегировать, 1-19 = Отложить, личное = После работы."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я Angel AI.\n\nПиши задачи — скажу что принесёт деньги 👇")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Анализирую...")
    try:
        r = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"system","content":PROMPT},{"role":"user","content":update.message.text}]
        )
        raw = r.choices[0].message.content.replace("```json","").replace("```","").strip()
        tasks = json.loads(raw).get("tasks",[])
        order = {"Делать сейчас":0,"Делать сегодня":1,"Делегировать":2,"Отложить":3,"После работы":4}
        tasks.sort(key=lambda x: order.get(x.get("priority","Отложить"),5))
        em = {"Делать сейчас":"🔥","Делать сегодня":"✅","Делегировать":"👥","Отложить":"⏳","После работы":"🏠"}
        reply = f"📋 Проанализировал {len(tasks)} задач:\n\n"
        for t in tasks:
            reply += f"{em.get(t.get('priority',''),'⏳')} {t.get('task','')}\n"
            reply += f"💰 Прибыль: {t.get('profit',0)}%  ⏱ {t.get('minutes',0)} мин\n"
            reply += f"💡 {t.get('reason','')}\n"
            reply += f"⚠️ {t.get('warning','')}\n"
            reply += f"👉 {t.get('priority','')}\n\n"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Точно",callback_data="agree"),InlineKeyboardButton("❌ Ошибки",callback_data="disagree")]])
        await update.message.reply_text(reply,reply_markup=kb)
    except Exception as e:
        print(f"ERROR: {e}")
        await update.message.reply_text("⚠️ Ошибка. Попробуй ещё раз.")

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_reply_markup(reply_markup=None)
    if q.data=="agree":
        await q.message.reply_text("👍 Удачного дня! 💪")
    else:
        await q.message.reply_text("🙏 Напиши что было неточно.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,analyze))
    app.add_handler(CallbackQueryHandler(btn))
    print("✅ Angel AI запущен!")
    app.run_polling()

if __name__=="__main__":
    main()
