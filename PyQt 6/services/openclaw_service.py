"""
Client HTTP OpenAI-compatible vers OpenClaw.

Le token OpenClaw reste côté serveur — il n'est jamais transmis au frontend
et n'apparaît jamais dans les logs, erreurs ou messages affichés à l'utilisateur.

Configuration : ~/.nudge_openclaw.json (géré via l'interface Nudge).
"""
import time
import httpx

_SYSTEM_PROMPT = (
    "Tu es l'assistant IA de l'application Nudge. "
    "Tu aides l'utilisateur à comprendre ses tâches, projets, retards, priorités et échéances. "
    "Réponds directement, clairement et sans faire d'onboarding. "
    "Quand la question concerne Nudge, utilise uniquement les données fournies dans le contexte. "
    "Si une information n'est pas disponible, dis-le clairement."
)


class OpenClawError(Exception):
    pass


def _load_config() -> dict:
    from config.openclaw_config import load
    return load()


def _build_url(cfg: dict) -> str:
    return cfg.get("gateway_url", "").rstrip("/") + cfg.get("endpoint", "/chat/completions")


def _explain_status(status: int, url: str, body: str) -> str:
    """Génère un message d'erreur lisible selon le code HTTP reçu."""
    safe_url = url  # l'URL est sûre — le token est dans l'en-tête, pas dans l'URL

    if status == 401:
        return (
            "Token OpenClaw refusé (401 Unauthorized).\n"
            "Vérifiez le token API dans Configuration > Config. OpenClaw."
        )
    if status == 403:
        return (
            "Accès refusé par OpenClaw (403 Forbidden).\n"
            "Vérifiez les permissions associées à votre token."
        )
    if status == 404:
        return (
            f"Endpoint introuvable (404 Not Found).\n"
            f"URL appelée : {safe_url}\n"
            "Vérifiez l'endpoint dans Configuration > Config. OpenClaw."
        )
    if status == 502:
        detail = body[:200].strip() if body else "(aucun détail)"
        return (
            f"OpenClaw a répondu 502 Bad Gateway.\n\n"
            "Cela signifie que Nudge a contacté le gateway, mais que le service "
            "derrière le gateway n'a pas répondu correctement.\n\n"
            "Causes possibles :\n"
            "  - le gateway OpenClaw est démarré mais le bot ne répond pas\n"
            "  - l'endpoint configuré est incorrect\n"
            "  - OpenClaw n'arrive pas à joindre son modèle ou son backend\n"
            "  - le proxy ou tunnel renvoie une erreur\n"
            "  - le serveur OpenClaw a crashé pendant la requête\n\n"
            f"URL appelée : {safe_url}\n"
            f"Détail serveur : {detail}"
        )
    if status == 503:
        return (
            f"Service indisponible (503 Service Unavailable).\n"
            f"URL appelée : {safe_url}\n"
            "Le gateway OpenClaw est surchargé ou en cours de redémarrage."
        )
    return (
        f"OpenClaw a répondu HTTP {status}.\n"
        f"URL appelée : {safe_url}\n"
        f"Détail : {body[:300].strip() if body else '(aucun détail)'}"
    )


async def ask(message: str, context: str = "") -> str:
    """
    Envoie un message à OpenClaw via POST {endpoint} et retourne la réponse.
    Lève OpenClawError en cas d'échec réseau, d'auth ou de réponse inattendue.
    Le token n'est jamais inclus dans les messages d'erreur.
    """
    cfg = _load_config()

    if not cfg.get("enabled", True):
        raise OpenClawError(
            "L'intégration OpenClaw est désactivée.\n"
            "Activez-la dans Configuration > Config. OpenClaw."
        )

    gateway_url = cfg.get("gateway_url", "")
    token       = cfg.get("api_token", "")
    timeout     = cfg.get("timeout_seconds", 30)
    bot_name    = cfg.get("bot_name", "nudge-bot")

    if not gateway_url:
        raise OpenClawError(
            "URL du gateway OpenClaw non configurée.\n"
            "Ouvrez Configuration > Config. OpenClaw pour la configurer."
        )
    if not token:
        raise OpenClawError(
            "Token API OpenClaw non configuré.\n"
            "Ouvrez Configuration > Config. OpenClaw pour le renseigner."
        )

    url = _build_url(cfg)

    system_content = _SYSTEM_PROMPT
    if context:
        system_content += f"\n\n{context}"

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": message},
    ]

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={"model": bot_name, "messages": messages},
            )
    except httpx.TimeoutException:
        raise OpenClawError(
            f"OpenClaw ne répond pas dans le délai configuré ({timeout}s).\n"
            "Vous pouvez augmenter le timeout dans Configuration > Config. OpenClaw."
        )
    except httpx.ConnectError:
        raise OpenClawError(
            f"Impossible de joindre OpenClaw à {gateway_url}.\n"
            "Vérifiez que le gateway est démarré et que l'URL est correcte."
        )
    except httpx.RequestError as exc:
        raise OpenClawError(f"Erreur réseau : {type(exc).__name__}")

    if response.status_code != 200:
        raise OpenClawError(_explain_status(response.status_code, url, response.text))

    try:
        data    = response.json()
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


def test_connection() -> tuple[bool, float, str]:
    """
    Teste la connexion au gateway OpenClaw de façon synchrone.

    Retourne (success: bool, latency_ms: float, message: str).
    Le token n'apparaît jamais dans le message retourné.
    """
    cfg = _load_config()

    if not cfg.get("enabled", True):
        return False, 0.0, "L'intégration OpenClaw est désactivée."

    gateway_url = cfg.get("gateway_url", "").rstrip("/")
    endpoint    = cfg.get("endpoint", "/chat/completions")
    token       = cfg.get("api_token", "")
    timeout     = cfg.get("timeout_seconds", 30)
    bot_name    = cfg.get("bot_name", "nudge-bot")

    if not gateway_url:
        return False, 0.0, "URL du gateway non configurée."

    url = gateway_url + endpoint
    t0  = time.perf_counter()

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": bot_name,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
            )
    except httpx.TimeoutException:
        elapsed = (time.perf_counter() - t0) * 1000
        return False, elapsed, (
            f"Timeout après {timeout}s.\n"
            "Vérifiez que le gateway est démarré et accessible."
        )
    except httpx.ConnectError:
        elapsed = (time.perf_counter() - t0) * 1000
        return False, elapsed, (
            f"Impossible de joindre {gateway_url}.\n"
            "Vérifiez que le gateway est démarré."
        )
    except Exception as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        return False, elapsed, f"Erreur réseau : {type(exc).__name__}"

    elapsed = (time.perf_counter() - t0) * 1000

    if resp.status_code in (200, 201):
        return True, elapsed, "Connexion réussie."

    msg = _explain_status(resp.status_code, url, resp.text)
    return False, elapsed, msg
