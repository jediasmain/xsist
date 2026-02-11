import requests
from zeep import Client
from zeep.transports import Transport

# Tente primeiro esse (às vezes o www1 bloqueia)
WSDL = "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx?wsdl"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
})
transport = Transport(session=session, timeout=30)

client = Client(WSDL, transport=transport)

print("WSDL OK:", WSDL)
print("\nOperações encontradas:")
for service in client.wsdl.services.values():
    for port in service.ports.values():
        ops = list(port.binding._operations.keys())
        print("-", service.name, "/", port.name, "->", ops)