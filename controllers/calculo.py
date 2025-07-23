from flask import request
from flask_restful import Resource


class CalcResource(Resource):

    def post(self) -> dict:
        data = request.get_json(force=True)

        consumo_mensal = data.get("consumo_mensal")
        horas_sol = data.get("horas_sol")
        potencia_painel = data.get("potencia_painel")

        if horas_sol and potencia_painel:
            return {
                "resultado": (consumo_mensal * 1000)
                / (horas_sol * 30 * potencia_painel)
            }, 200
        else:
            return {"resultado": "Valor inválido: divisão por zero."}, 400
