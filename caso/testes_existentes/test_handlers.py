import unittest

from miniloja import handlers


class TestHandlers(unittest.TestCase):
    def test_criar_e_obter_pedido(self):
        status, pedido = handlers.post_pedidos(
            10, {"itens": [{"sku": "BOLA-01", "preco": 50.0, "qtd": 2}], "uf": "PE"}
        )
        self.assertEqual(status, 201)
        self.assertEqual(pedido["total"], 118.55)
        status2, corpo = handlers.get_pedido(10, pedido["id"])
        self.assertEqual(status2, 200)
        self.assertEqual(corpo["id"], pedido["id"])

    def test_pedido_inexistente(self):
        status, _ = handlers.get_pedido(10, 9999)
        self.assertEqual(status, 404)

    def test_estoque_insuficiente_retorna_409(self):
        status, corpo = handlers.post_pedidos(
            11, {"itens": [{"sku": "CHUTEIRA-42", "preco": 300.0, "qtd": 999}]}
        )
        self.assertEqual(status, 409)
        self.assertEqual(corpo["sku"], "CHUTEIRA-42")

    def test_usuario_nao_ve_pedido_de_outro_usuario(self):
        # R4.1: um usuário só pode ver os próprios pedidos.
        # Decisão (ESCOPO-AV3.md): pedido alheio responde 404, como um inexistente.
        status, pedido = handlers.post_pedidos(
            10, {"itens": [{"sku": "CAMISA-M", "preco": 40.0, "qtd": 1}], "uf": "PE"}
        )
        self.assertEqual(status, 201)
        status2, corpo = handlers.get_pedido(99, pedido["id"])
        status_inexistente, corpo_inexistente = handlers.get_pedido(99, -1)
        self.assertEqual(status_inexistente, 404)
        self.assertEqual(status2, 404)
        for campo in ("id", "usuario_id", "itens", "total", "total_fmt"):
            self.assertNotIn(campo, corpo)
        self.assertEqual(corpo, corpo_inexistente)
