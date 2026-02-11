from services.sefaz_payloads import build_distdfeint_cons_chave

xml = build_distdfeint_cons_chave(
    chave="35111111111111111111111111111111111111111111",
    cnpj="11111111000111",
    tp_amb=1,
)

print(xml)