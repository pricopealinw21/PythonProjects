#Încearcă AI direct în aplicațiile preferate … Folosește Gemini pentru a genera schițe și a rafina conținut și beneficiază de Gemini Pro cu acces la AI de ultimă generație de la Google la 109,99 RON 0 RON pentru o lună (preț personalizat)
import os
import asyncio
from openai import AsyncOpenAI
from typing import Optional
from agents import (
    Agent, Runner, RunConfig, handoff,
    ModelProvider, Model,
    OpenAIChatCompletionsModel,
    function_tool, set_tracing_disabled
)
from pydantic import BaseModel, Field

set_tracing_disabled(True)

# ─── Configurare Orange ────────────────────────────────────────────

ORANGE_BASE_URL = "https://llmproxy.ai.orange"
ORANGE_API_KEY  = os.environ.get("ORANGE_API_KEY", "sk-1N5VPoC1uTFngf-1PRZ6xg")

orange_client = AsyncOpenAI(base_url=ORANGE_BASE_URL, api_key=ORANGE_API_KEY)

class OrangeModelProvider(ModelProvider):
    def __init__(self, model: str = "openai/gpt-5-chat"):
        self._model = model
    def get_model(self, model_name: Optional[str]) -> Model:
        return OpenAIChatCompletionsModel(
            model=model_name or self._model,
            openai_client=orange_client
        )

RUN_CONFIG = RunConfig(model_provider=OrangeModelProvider())

# ─── Unelte ───────────────────────────────────────────────────────

@function_tool
def verifica_sold(numar_telefon: str) -> dict:
    """Verifică soldul contului unui abonat Orange.
    Args:
        numar_telefon: Numărul de telefon (format 07XXXXXXXX)
    """
    return {
        "numar": numar_telefon,
        "sold_date_gb": 12.5,
        "sold_voce_min": 450,
        "valabil_pana": "2025-04-30",
        "status_cont": "activ"
    }

@function_tool
def cauta_abonamente(tip: str = "mobil") -> list:
    """Caută abonamentele Orange disponibile.
    Args:
        tip: Tipul abonamentului: 'mobil', 'internet', 'tv', 'bundle'
    """
    catalog = {
        "mobil": [
            {"plan": "Orange 5G Start",    "pret": 29.99, "date": "10 GB",     "beneficii": "Apeluri nelimitate"},
            {"plan": "Orange 5G Pro",      "pret": 44.99, "date": "50 GB",     "beneficii": "Roaming EU, Netflix inclus"},
            {"plan": "Orange 5G Infinity", "pret": 59.99, "date": "Nelimitat", "beneficii": "All inclusive"},
        ],
        "internet": [
            {"plan": "Fibra 500 Mbps", "pret": 39.99, "viteza": "500 Mbps", "beneficii": "Router inclus"},
            {"plan": "Fibra 1 Gbps",   "pret": 59.99, "viteza": "1 Gbps",   "beneficii": "TV + router"},
        ]
    }
    return catalog.get(tip, [])

@function_tool
def raporteaza_problema(numar_telefon: str, descriere: str, prioritate: str = "normala") -> dict:
    """Creează un tichet de suport pentru o problemă raportată de client.
    Args:
        numar_telefon: Numărul clientului
        descriere: Descrierea problemei
        prioritate: Nivelul de urgență: 'scazuta', 'normala', 'ridicata', 'critica'
    """
    import random
    tichet_id = f"TKT-{random.randint(10000, 99999)}"
    timp = "2-4 ore" if prioritate in ["ridicata", "critica"] else "24-48 ore"
    return {
        "tichet_id": tichet_id,
        "status": "deschis",
        "timp_estimat": timp,
        "mesaj": f"Tichetul {tichet_id} a fost creat. Veți fi contactat în {timp}."
    }

@function_tool
def verifica_factura(numar_telefon: str, luna: str = "curenta") -> dict:
    """Verifică detaliile facturii unui client Orange.
    Args:
        numar_telefon: Numărul de telefon al clientului
        luna: Luna facturii: 'curenta', 'anterioara' sau format 'YYYY-MM'
    """
    return {
        "numar": numar_telefon,
        "luna": luna,
        "suma_totala": 74.99,
        "abonament": 49.99,
        "servicii_extra": 25.00,
        "scadenta": "2025-04-15",
        "status": "neachitata"
    }

# ─── Model Pydantic ───────────────────────────────────────────────

class RaspunsAsistenta(BaseModel):
    raspuns: str = Field(description="Răspunsul complet și clar pentru client, în limba română")
    actiune_efectuata: Optional[str] = Field(None, description="Descrierea acțiunii efectuate")
    ticket_id: Optional[str] = Field(None, description="ID-ul tichetului de suport creat")
    recomandare: Optional[str] = Field(None, description="O recomandare proactivă pentru client")
    prioritate: int = Field(1, ge=1, le=5, description="Urgența cererii: 1=scăzut, 5=critic")
    nume_agent: str = Field(description="Numele agentului: Triage, SuportTehnic sau ConsultantVanzari")

# ─── Agenți — ordinea contează pentru referințe circulare ────────
# Triage definit primul (fără handoffs), specialiștii au handoff înapoi la triage,
# apoi handoffs triage → specialiști adăugate la final.

agent_triage = Agent(
    name="Triage",
    instructions=(
        "Ești asistentul virtual Orange, te numesti OrangeBunLaToate. "
        "Vei primi istoricul conversației în mesajul primit — citește-l pentru context.\n\n"
        "Poartă o conversație naturală și prietenoasă. Poți face small talk.\n\n"
        "TRANSFERĂ IMEDIAT când mesajul curent privește:\n"
        "- transfer_vanzari: abonament, prelungire, ofertă, preț, upgrade, factură, sold\n"
        "- transfer_suport_tehnic: problemă, semnal, nu merge, eroare, rețea, conexiune\n\n"
        "Transferă fără întrebări suplimentare la primul semnal clar."
    ),
    # Fără output_type — permite SDK-ului să apeleze efectiv tool-urile de handoff.
    # handoffs adăugate mai jos după ce specialiștii sunt definiți.
)

agent_suport_tehnic = Agent(
    name="SuportTehnic",
    instructions=(
        "Ești specialistul de suport tehnic Orange, OroTechGuru. "
        "Vei primi istoricul conversației în mesajul primit — citește-l pentru context. "
        "Diagnostichezi și rezolvi probleme de rețea, conexiune, dispozitive și servicii tehnice. "
        "Creezi tichete de suport când e necesar. Te preziti cand intri in conversatie pentru prima data. Răspunzi în română, ești precis.\n\n"
        "Dacă clientul schimbă subiectul complet în afara ariei tehnice (ex: abonamente, oferte, facturi), "
        "transferă înapoi la triage folosind transfer_triage."
    ),
    tools=[raporteaza_problema, verifica_sold, verifica_factura],
    output_type=RaspunsAsistenta,
    handoffs=[
        handoff(agent_triage,
                tool_name_override="transfer_triage",
                tool_description_override="Transferă înapoi la triage când subiectul iese complet din aria suportului tehnic"),
    ],
)

agent_vanzari = Agent(
    name="ConsultantVanzari",
    instructions=(
        "Ești OroSalesMan, consultantul de vânzări Orange. "
        "Vei primi istoricul conversației în mesajul primit — citește-l pentru context. "
        "Prezinți abonamentele disponibile, verifici solduri și recomanzi planuri potrivite. "
        "Ești entuziast și orientat spre client. Te preziti cand intri in conversatie pentru prima data. Răspunzi în română.\n\n"
        "Dacă clientul schimbă subiectul complet în afara ariei vânzărilor (ex: problemă tehnică, rețea, semnal), "
        "transferă înapoi la triage folosind transfer_triage."
    ),
    tools=[cauta_abonamente, verifica_sold, verifica_factura],
    output_type=RaspunsAsistenta,
    handoffs=[
        handoff(agent_triage,
                tool_name_override="transfer_triage",
                tool_description_override="Transferă înapoi la triage când subiectul iese complet din aria vânzărilor"),
    ],
)

# Handoffs triage → specialiști (adăugate după ce specialiștii sunt definiți)
agent_triage.handoffs = [
    handoff(agent_suport_tehnic,
            tool_name_override="transfer_suport_tehnic",
            tool_description_override="Transferă la suport tehnic pentru probleme de rețea, conexiune sau dispozitiv"),
    handoff(agent_vanzari,
            tool_name_override="transfer_vanzari",
            tool_description_override="Transferă la vânzări pentru abonamente, oferte, solduri sau facturi"),
]

# ─── Chat CLI ─────────────────────────────────────────────────────

def afiseaza_raspuns(output, agent_name: str):
    """Afișează răspunsul. agent_name vine din result.last_agent.name — sursa de adevăr.
    Triage răspunde ca text simplu; specialiștii returnează RaspunsAsistenta."""
    if isinstance(output, RaspunsAsistenta):
        print(f"\nOrange [{agent_name}]: {output.raspuns}")
        # if output.actiune_efectuata:
        #     print(f"  Actiune:    {output.actiune_efectuata}")
        # if output.ticket_id:
        #     print(f"  Tichet:     {output.ticket_id}")
        # if output.recomandare:
        #     print(f"  Sfat:       {output.recomandare}")
        # if output.prioritate > 1:
        #     print(f"  Prioritate: {'*' * output.prioritate}")
    else:
        # Triage text simplu
        print(f"\nOrange [{agent_name}]: {output}")


def construieste_input(mesaj: str, istoric: list[tuple[str, str]]) -> str:
    """Construiește input-ul ca string cu istoricul embedded ca text.
    Evită pasarea history ca list de mesaje (incompatibil cu proxy-ul Orange).
    """
    if not istoric:
        return mesaj
    log = "\n".join(f"{speaker}: {text}" for speaker, text in istoric)
    return f"[Istoricul conversației până acum:\n{log}]\n\nMesaj curent al clientului: {mesaj}"


async def chat():
    print("=" * 60)
    print("  Asistenta Orange — Chat Suport")
    print("  Tastați 'quit' pentru a ieși.")
    print("=" * 60)

    # Istoric simplu ca perechi (speaker, text) — fără tool_calls
    istoric: list[tuple[str, str]] = []
    # Agentul activ curent — sticky după handoff, se resetează la triage dacă specialistul face re-handoff
    current_agent = agent_triage

    # Triage deschide conversația
    result = await Runner.run(
        agent_triage,
        "Salută clientul în mod prietenos și scurt, și întreabă cum îl poți ajuta.",
        run_config=RUN_CONFIG
    )
    current_agent = result.last_agent
    output = result.final_output
    afiseaza_raspuns(output, current_agent.name)
    raspuns_text = output.raspuns if isinstance(output, RaspunsAsistenta) else str(output)
    istoric.append(("Asistent", raspuns_text))

    while True:
        try:
            mesaj = input("\nTu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLa revedere!")
            break

        if mesaj.lower() == "quit":
            print("La revedere!")
            break

        if not mesaj:
            continue

        istoric.append(("Client", mesaj))

        inp = construieste_input(mesaj, istoric[:-1])
        result = await Runner.run(current_agent, inp, run_config=RUN_CONFIG)
        current_agent = result.last_agent  # actualizat după fiecare run
        output = result.final_output

        output = result.final_output
        afiseaza_raspuns(output, current_agent.name)
        raspuns_text = output.raspuns if isinstance(output, RaspunsAsistenta) else str(output)
        istoric.append(("Asistent", raspuns_text))


if __name__ == "__main__":
    asyncio.run(chat())