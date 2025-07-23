from flask import request
from flask_restful import Resource

from models.proposta import Offer, db


class OffersResource(Resource):

    def get(self, proposta_id=None):
        if proposta_id:
            proposta = Offer.query.get(proposta_id)
            if not proposta:
                return {"error": "Proposta não encontrada"}, 404
            return {"proposta": proposta.to_dict()}, 200

        propostas = Offer.query.all()
        return {"propostas": [p.to_dict() for p in propostas]}, 200

    def post(self):
        data = request.get_json(force=True)

        try:
            proposta = Offer(
                projeto_id=data.get("projeto_id"),
                prestador_id=data.get("prestador_id"),
                valor_proposto=data.get("valor_proposto"),
                prazo_proposto=data.get("prazo_proposto"),
                data_envio=data.get("data_envio"),
            )

            db.session.add(proposta)
            db.session.commit()

            return {
                "message": "Proposta criada com sucesso",
                "proposta": proposta.to_dict(),
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao criar proposta: {str(e)}"}, 500

    def put(self, proposta_id):
        proposta = Offer.query.get(proposta_id)
        if not proposta:
            return {"error": "Proposta não encontrada"}, 404

        data = request.get_json(force=True)

        # Busca cada coluna de proposta e verifica se essa coluna veio no payload. Se sim, atualiza no banco
        for attr in [
            "projeto_id",
            "prestador_id",
            "valor_proposto",
            "prazo_proposto",
            "data_envio",
        ]:
            if attr in data:
                setattr(proposta, attr, data[attr])

        db.session.commit()
        return {
            "message": "Proposta atualizada com sucesso",
            "proposta": proposta.to_dict(),
        }, 200

    def delete(self, proposta_id):
        proposta = Offer.query.get(proposta_id)
        if not proposta:
            return {"error": "Proposta não encontrada"}, 404

        db.session.delete(proposta)
        db.session.commit()
        return {"message": "Proposta excluída com sucesso"}, 200
