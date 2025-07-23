from models.user import db


class Cliente(db.Model):
    __tablename__ = "cliente"
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    documento_identidade = db.Column(db.String(15), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    conta_energia_url = db.Column(db.Float, nullable=False)
    conta_kilowatts = db.Column(db.Float, nullable=False)

    user = db.relationship("User", backref=db.backref("cliente", uselist=False))
