from app.sheets_service import listar_pedidos_para_cracha


pedidos = listar_pedidos_para_cracha()

print(f"Pedidos de crachá pendentes: {len(pedidos)}")
print("-" * 60)

for pedido in pedidos:
    print(f"Linha: {pedido['_numero_linha']}")

    for campo, valor in pedido.items():
        if campo == "_numero_linha":
            continue

        print(f"{campo}: {valor}")

    print("-" * 60)