from flask import request
from flask_restful import Resource

from models.projeto import Project, db


class ProjectsResource(Resource):

    def get(self, projeto_id=None):
        if projeto_id:
            projeto = Project.query.get(projeto_id)
            if not projeto:
                return {"error": "Projeto não encontrado"}, 404
            return {"projeto": projeto.to_dict()}, 200

        projetos = Project.query.all()
        return {"projetos": [p.to_dict() for p in projetos]}, 200

    def post(self):
        data = request.get_json(force=True)

        try:
            projeto = Project(
                cliente_id=data.get("cliente_id"),
                prestador_id=data.get("prestador_id"),
                data_solicitacao=data.get("data_solicitacao"),
                data_inicial=data.get("data_inicial"),
                data_final=data.get("data_final"),
                prazo_dias=data.get("prazo_dias"),
                valor_prestador=data.get("valor_prestador"),
                valor_material=data.get("valor_material"),
                valor_assinatura=data.get("valor_assinatura"),
                valor_total=data.get("valor_total"),
                status=data.get("status"),
            )

            db.session.add(projeto)
            db.session.commit()

            return {
                "message": "Projeto criado com sucesso",
                "projeto": projeto.to_dict(),
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao criar projeto: {str(e)}"}, 500

    def put(self, projeto_id):
        projeto = Project.query.get(projeto_id)
        if not projeto:
            return {"error": "Projeto não encontrado"}, 404

        data = request.get_json(force=True)

        # Busca cada coluna de projeto e verifica se essa coluna veio no payload. Se sim, atualiza no banco
        for attr in [
            "cliente_id",
            "prestador_id",
            "data_solicitacao",
            "data_inicial",
            "data_final",
            "prazo_dias",
            "valor_prestador",
            "valor_material",
            "valor_assinatura",
            "valor_total",
            "status",
        ]:
            if attr in data:
                setattr(projeto, attr, data[attr])

        db.session.commit()
        return {
            "message": "Projeto atualizado com sucesso",
            "projeto": projeto.to_dict(),
        }, 200

    def delete(self, projeto_id):
        projeto = Project.query.get(projeto_id)
        if not projeto:
            return {"error": "Projeto não encontrado"}, 404

        db.session.delete(projeto)
        db.session.commit()
        return {"message": "Projeto excluído com sucesso"}, 200
