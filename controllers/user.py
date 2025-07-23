from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash

from models.administrador import Administrador
from models.cliente import Cliente
from models.estado import Estado
from models.prestador import Prestador
from models.user import User, db


class UsersResource(Resource):

    def get(self, user_id: int | None = None) -> dict:
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404
            return {"user": user.to_dict()}, 200

        users = User.query.all()
        return {"users": [u.to_dict() for u in users]}, 200

    def post(self) -> dict:
        data = request.get_json(force=True)

        nome = data.get("nome")
        email = data.get("email")
        senha = data.get("senha")
        senha_hash = generate_password_hash(senha)
        telefone = data.get("telefone")
        tipo = data.get("tipo")

        if not all([nome, email, senha, tipo]):
            return {
                "error": "Os campos nome, email, senha_hash e tipo são obrigatórios"
            }, 400

        new_user = User(
            nome=nome, email=email, senha=senha_hash, telefone=telefone, tipo=tipo
        )

        db.session.add(new_user)
        # forca o add no user para gera o fk para as outras
        db.session.flush()

        # add nas tabelas cliente, adm ou prestador
        if tipo == "cliente":
            cli = Cliente(
                user_id=new_user.user_id,
                documento_identidade=data.get("documento_identidade"),
                endereco=data.get("endereco"),
                conta_energia_url=data.get("conta_energia_url"),
                conta_kilowatts=data.get("conta_kilowatts"),
            )
            db.session.add(cli)

        elif tipo == "prestador":
            pr = Prestador(
                user_id=new_user.user_id,
            )
            db.session.add(pr)

        elif tipo == "administrador":
            adm = Administrador(
                user_id=new_user.user_id,
                valor_assinatura=data.get("valor_assinatura"),
            )
            db.session.add(adm)

        else:
            return {
                "error": f"Tipo '{tipo}' inválido. Deve ser cliente, prestador ou administrador."
            }, 400

        # add na tabela estado caso tenha atributo estado
        # a condicao para ser adm ou prestador vai ser feita no proprio json, ou seja, front
        if data.get("estado"):
            est = Estado(
                user_id=new_user.user_id,
                estado=data.get("estado"),
                valor_estado=data.get("valor_estado"),
                tipo_de_cobranca=data.get("tipo_de_cobranca"),
            )
            db.session.add(est)

        db.session.commit()

        return {
            "message": "User and subtype created successfully",
            "user": new_user.to_dict(),
        }, 201

    def put(self, user_id: int) -> dict:
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        data = request.get_json(force=True)
        nome = data.get("nome")
        email = data.get("email")
        senha_hash = data.get("senha_hash")
        tipo = data.get("tipo")
        telefone = data.get("telefone")

        if not nome or not email or not senha_hash or not tipo:
            return {
                "error": "Os campos nome, email, senha_hash e tipo são obrigatórios"
            }, 400

        user.nome = nome
        user.email = email
        user.senha_hash = senha_hash
        user.tipo = tipo
        user.telefone = telefone

        db.session.commit()
        return {"message": "User updated successfully", "user": user.to_dict()}, 200

    def delete(self, user_id: int) -> dict:
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200
