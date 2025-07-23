from faker import Faker

from app import app
from models.estado import Estado
from models.user import User, db

# faker do lol
fake = Faker()

# faz o povoamento
with app.app_context():
    print("Starting seed...")

    Estado.query.delete()
    User.query.delete()

    new_users = []

    for _ in range(20):
        nome = fake.first_name()[:10]
        email = fake.unique.email()[:15]
        senha = fake.sha256()[:25]
        telefone = fake.phone_number()[:20]
        tipo = "moderador"

        new_user = User(
            nome=nome, email=email, senha=senha, telefone=telefone, tipo=tipo
        )

        db.session.add(new_user)
        db.session.flush()

        estado = Estado(
            user_id=new_user.user_id,
            estado=fake.state()[:20],
            valor_estado=round(fake.random_number(digits=4) / 100, 2),
            tipo_de_cobranca=fake.random_element(
                elements=["fixo", "variável", "por_hora"]
            ),
        )
        db.session.add(estado)

        new_users.append(new_user)

    db.session.commit()
    print("Successfully seeded")
