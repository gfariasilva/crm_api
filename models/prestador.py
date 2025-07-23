from models.user import db


class Prestador(db.Model):
    __tablename__ = "prestador"
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    user = db.relationship("User", backref=db.backref("prestador", uselist=False))
