from app.drive_service import baixar_foto_drive
from app.sheets_service import listar_pedidos_para_cracha


pedidos = listar_pedidos_para_cracha()

if not pedidos:
    print("Nenhum pedido de crachá pendente.")
    raise SystemExit


pedido = pedidos[0]

link_foto = pedido["Foto (boa qualidade, rosto visível)"]
numero_linha = pedido["_numero_linha"]

caminho = baixar_foto_drive(
    link=link_foto,
    nome_arquivo=f"foto_linha_{numero_linha}",
)

print("Foto baixada com sucesso:")
print(caminho)