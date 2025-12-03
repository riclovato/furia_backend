from app.models import TelegramUser
async def handle_update(update: dict, db):

    #mensagem normal
    if "message" in update:
        await handle_message(update["message"], db)


async def handle_message(message: dict, db):
    chat_id = message["chat"]["id"]
    user_info = message["from"]

    username = user_info.get("username")
    first_name = user_info.get("first_name")
    last_name = user_info.get("last_name")

    #verifica se usuario existe
    user = db.query(TelegramUser).filter_by(chat_id=chat_id).first()

    if not user:
        #cria novo usuario
        user = TelegramUser(
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Novo usuario salvo: @{username}")
        
    print(f"Mensagem recebida de @{username}: {message.get('text')}")

