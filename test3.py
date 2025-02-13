import asyncio
from yookassa import Configuration, Payment
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройки ЮKassa
Configuration.configure(account_id='1032619', secret_key='test_oAGk-KejRiNUifJhXcHtoBCXIiZYZB1E9YDHaBkEmUY')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Используйте /pay для создания платежа.')

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        payment = Payment.create({
            "amount": {
                "value": "56000.00",  # Сумма платежа
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://your-return-url.com"  # Замените на ваш URL возврата
            },
            "capture": True,
            "description": "Тестовый платеж"
        })

        # Сохраняем payment_id в контексте пользователя
        context.user_data['payment_id'] = payment.id

        # Отправляем пользователю ссылку на оплату
        await update.message.reply_text(
            f'Платеж создан! Перейдите по [ссылке]({payment.confirmation.confirmation_url}) для оплаты.',
            parse_mode='Markdown'
        )

        # Запускаем асинхронную задачу для проверки статуса платежа
        asyncio.create_task(check_payment_status(update, context, payment.id))

    except Exception as e:
        await update.message.reply_text(f'Ошибка при создании платежа: {str(e)}')

async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str) -> None:
    while True:
        await asyncio.sleep(10)

        try:
            payment = Payment.find_one(payment_id)
            status = payment.status

            if status == 'succeeded':
                await update.message.reply_text(f'Платеж {payment_id} успешно завершен!')
                break
            elif status == 'canceled':
                await update.message.reply_text(f'Платеж {payment_id} отменен.')
                break
            else:
                await update.message.reply_text(f'Статус платежа {payment_id}: {status}. Ожидаем завершения...')

        except Exception as e:
            await update.message.reply_text(f'Ошибка при проверке статуса платежа: {str(e)}')
            break

def main() -> None:
    application = ApplicationBuilder().token("8178914232:AAEHHs8edmiStNxA5FelDC16fTo-NVidNaM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", pay))

    application.run_polling()

if __name__ == '__main__':
    main()