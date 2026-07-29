import qrcode

# Número de teste
telefone = "5521999999999"

# Mensagem automática
mensagem = "Olá, tudo bem?"

# Monta o link do WhatsApp
link = f"https://wa.me/{telefone}?text={mensagem}"

# Gera o QR Code
qr = qrcode.make(link)

# Salva na pasta output
qr.save("output/qr_teste.png")

print("QR Code criado com sucesso!")