from models.user import db


class Estado(db.Model):
    __tablename__ = "estado"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    estado = db.Column(db.String(20), nullable=False)
    valor_estado = db.Column(db.Float, nullable=False)
    tipo_de_cobranca = db.Column(db.String(20), nullable=False)

    user = db.relationship("User", backref=db.backref("estado", uselist=False))
