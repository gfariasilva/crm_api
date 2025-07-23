from models.user import db


class Administrador(db.Model):
    __tablename__ = "administrador"
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    valor_assinatura = db.Column(db.Float, nullable=False)

    user = db.relationship("User", backref=db.backref("administrador", uselist=False))
