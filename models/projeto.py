from flask_sqlalchemy import SQLAlchemy

from models.user import db


class Project(db.Model):
    __tablename__ = "projeto"
    projeto_id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.user_id"))
    prestador_id = db.Column(db.Integer, db.ForeignKey("prestador.user_id"))
    data_solicitacao = db.Column(db.DateTime, nullable=False)
    data_inicial = db.Column(db.Date, nullable=False)
    data_final = db.Column(db.Date, nullable=False)
    prazo_dias = db.Column(db.Integer, nullable=False)
    valor_prestador = db.Column(db.Float, nullable=False)
    valor_material = db.Column(db.Float, nullable=False)
    valor_assinatura = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "projeto_id": self.projeto_id,
            "cliente_id": self.cliente_id,
            "prestador_id": self.prestador_id,
            "data_solicitacao": (
                self.data_solicitacao.isoformat() if self.data_solicitacao else None
            ),
            "data_inicial": (
                self.data_inicial.isoformat() if self.data_inicial else None
            ),
            "data_final": self.data_final.isoformat() if self.data_final else None,
            "prazo_dias": self.prazo_dias,
            "valor_prestador": self.valor_prestador,
            "valor_material": self.valor_material,
            "valor_assinatura": self.valor_assinatura,
            "valor_total": self.valor_total,
            "status": self.status,
        }
