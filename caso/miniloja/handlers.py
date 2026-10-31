"""Camada HTTP independente de framework: cada função devolve (status, corpo)."""
from miniloja.cadastro import cadastrar_cliente
from miniloja.estoque import Estoque, EstoqueInsuficiente
from miniloja.pagamentos import GatewayFake
from miniloja.pedidos import PedidoService
from miniloja.repositorio import RepositorioPedidos

_repo = RepositorioPedidos()
_estoque = Estoque({"BOLA-01": 50, "CHUTEIRA-42": 20, "CAMISA-M": 100})
_service = PedidoService(_repo, _estoque, GatewayFake())


def post_clientes(payload):
    return cadastrar_cliente(payload)


def post_pedidos(usuario_id, payload):
    try:
        pedido = _service.criar(
            usuario_id,
            payload.get("itens", []),
            payload.get("cupom"),
            payload.get("uf", "PE"),
            payload.get("token", "tok_ok"),
        )
    except ValueError as e:
        return 400, {"erro": str(e)}
    except EstoqueInsuficiente as e:
        return 409, {"erro": "estoque insuficiente", "sku": str(e)}
    if pedido.get("status") == "pagamento_recusado":
        return 402, pedido
    return 201, pedido


def get_pedido(usuario_id, pedido_id):
    pedido = _repo.obter(pedido_id)
    if pedido is None or pedido.get("usuario_id") != usuario_id:
        return 404, {"erro": "não encontrado"}
    return 200, pedido
