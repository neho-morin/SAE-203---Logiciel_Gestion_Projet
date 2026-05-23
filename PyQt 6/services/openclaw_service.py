"""
Client HTTP OpenAI-compatible vers OpenClaw.

Le token OpenClaw reste côté serveur — il n'est jamais transmis au frontend.
"""
import httpx

from config.settings import OPENCLAW_BASE_URL, OPENCLAW_TOKEN, OPENCLAW_MODEL, OPENCLAW_TIMEOUT

_SYSTEM_PROMPT = (
    "Tu es l'assistant IA de l'application Nudge. "
    "Tu aides l'utilisateur à comprendre ses tâches, projets, retards, priorités et échéances. "
    "Réponds directement, clairement et sans faire d'onboarding. "
    "Quand la question concerne Nudge, utilise uniquement les données fournies dans le contexte. "
    "Si une information n'est pas disponible, dis-le clairement."
)


class OpenClawError(Exception):
    pass


async def ask(message: str, context: str = "") -> str:
    """
    Envoie un message à OpenClaw via POST /chat/completions et retourne la réponse.
    Lève OpenClawError en cas d'échec réseau, d'auth ou de réponse inattendue.
    """
    if not OPENCLAW_BASE_URL:
        raise OpenClawError("OPENCLAW_BASE_URL non configuré dans .env")
    if not OPENCLAW_TOKEN:
        raise OpenClawError("OPENCLAW_TOKEN non configuré dans .env")

    system_content = _SYSTEM_PROMPT
    if context:
        system_content += f"\n\n{context}"

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": message},
    ]

    url = OPENCLAW_BASE_URL.rstrip("/") + "/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=OPENCLAW_TIMEOUT) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {OPENCLAW_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENCLAW_MODEL,
                    "messages": messages,
                },
            )
    except httpx.TimeoutException:
        raise OpenClawError(
            f"OpenClaw n'a pas répondu dans les {OPENCLAW_TIMEOUT} secondes."
        )
    except httpx.ConnectError:
        raise OpenClawError(
            f"Impossible de joindre OpenClaw à {OPENCLAW_BASE_URL}. "
            "Vérifiez que le serveur est démarré et accessible via Tailscale."
        )
    except httpx.RequestError as exc:
        raise OpenClawError(f"Erreur réseau : {exc}")

    if response.status_code == 401:
        raise OpenClawError("Token OpenClaw invalide (401 Unauthorized).")
    if response.status_code == 403:
        raise OpenClawError("Accès refusé par OpenClaw (403 Forbidden).")
    if response.status_code != 200:
        raise OpenClawError(
            f"OpenClaw a répondu {response.status_code} : {response.text[:300]}"
        )

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise OpenClawError(
            "Réponse OpenClaw inattendue — champ choices[0].message.content absent."
        )
    except ValueError:
        raise OpenClawError("Réponse OpenClaw non-JSON.")

    return content.strip() or "Aucune réponse reçue d'OpenClaw."


def ask_sync(message: str, context: str = "") -> str:
    """Version synchrone — à utiliser depuis un QThread PyQt6."""
    import asyncio
    return asyncio.run(ask(message, context))
