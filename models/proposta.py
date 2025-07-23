from flask_sqlalchemy import SQLAlchemy

from models.user import db


class Offer(db.Model):
    __tablename__ = "proposta"
    proposta_id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey("projeto.projeto_id"))
    prestador_id = db.Column(db.Integer, db.ForeignKey("prestador.user_id"))
    valor_proposto = db.Column(db.Float, nullable=False)
    prazo_proposto = db.Column(db.Integer, nullable=False)
    data_envio = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "proposta_id": self.proposta_id,
            "projeto_id": self.projeto_id,
            "prestador_id": self.prestador_id,
            "valor_proposto": self.valor_proposto,
            "prazo_proposto": self.prazo_proposto,
            "data_envio": self.data_envio.isoformat() if self.data_envio else None,
        }
