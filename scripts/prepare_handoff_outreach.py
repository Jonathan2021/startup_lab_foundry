"""Prepare the four authorized research drafts. No recipients or transport."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from startup_foundry.config import data_directory, load_settings
from startup_foundry.domain import Artifact, ArtifactKind, Venture
from startup_foundry.outreach import DraftInput, OutreachService
from startup_foundry.repository import (
    SessionFactory,
    UnitOfWork,
    create_db_engine,
    create_session_factory,
)

VARIANTS = [
    (
        "en",
        "formal",
        "Could you review a fictional work-sample receipt?",
        (
            "Hello,\n\nI am exploring whether a short, "
            "evidence-linked work sample could help a receiving "
            "hiring or training practitioner. The attached example "
            "is entirely fictional: no candidate was assessed and "
            "no credential or endorsement was issued.\n\nWould you be "
            "willing to spend ten minutes reviewing it? I would "
            "especially like to know which actual decision, if any, "
            "it would change; which evidence you would trust and "
            "inspect; what you would verify independently; and what "
            "existing process you already use. A negative answer is "
            "useful too.\n\nThere is no sales offer and no personal "
            "candidate data.\n\nThank you,\nJonathan"
        ),
    ),
    (
        "en",
        "informal",
        "Ten-minute take on a fictional work sample?",
        (
            "Hi,\n\nI am exploring a small idea: a short receipt for "
            "a specific work exercise, with the evidence and limits "
            "easy to check. I attached a completely fictional "
            "example—no real candidate, assessment or "
            "certificate.\n\nIf you have ten minutes, could you tell "
            "me whether it would change any hiring/training "
            "decision for you, what you would actually check, and "
            "what you already use instead? If it adds nothing, I "
            "want to know that too. No pressure if this is outside "
            "your role.\n\nThanks!\nJonathan"
        ),
    ),
    (
        "fr",
        "formal",
        "Avis sur un exemple fictif de compte rendu d’exercice",
        (
            "Bonjour,\n\nJ’étudie l’utilité d’un court compte rendu "
            "d’exercice, relié à des éléments vérifiables, pour une "
            "personne qui prend des décisions de recrutement ou de "
            "formation. L’exemple joint est entièrement fictif : "
            "aucun candidat réel n’a été évalué et aucune "
            "certification ou recommandation n’a été "
            "délivrée.\n\nAccepteriez-vous d’y consacrer dix minutes "
            "? Quelle décision concrète cela changerait-il, le cas "
            "échéant ? Quelles preuves consulteriez-vous, que "
            "vérifieriez-vous vous-même, et quelle méthode "
            "utilisez-vous déjà ? Un avis négatif serait tout aussi "
            "utile.\n\nIl ne s’agit pas d’une offre commerciale et le "
            "document ne contient aucune donnée de candidat "
            "réel.\n\nMerci pour votre retour,\nJonathan"
        ),
    ),
    (
        "fr",
        "informal",
        "Dix minutes pour un avis sur un exercice fictif ?",
        (
            "Salut,\n\nJ’explore une petite idée : un compte rendu "
            "d’un exercice précis, avec les preuves et les limites "
            "faciles à vérifier. L’exemple joint est complètement "
            "fictif : pas de vrai candidat, de vraie évaluation ni "
            "de certificat.\n\nSi tu as dix minutes, est-ce que ça "
            "changerait une décision de recrutement ou de formation "
            "pour toi ? Qu’est-ce que tu vérifierais et "
            "qu’utilises-tu déjà à la place ? Si ça n’apporte rien, "
            "ça m’intéresse aussi. Aucun souci si ce n’est pas ton "
            "domaine.\n\nMerci !\nJonathan"
        ),
    ),
]


def supplied_sender(inbox: Path) -> str:
    """Read the explicitly supplied identity without publishing it in source code."""
    content = inbox.read_text()
    section = content.split("## R004 — ", 1)[1].split("\n## ", 1)[0]
    addresses = set(
        re.findall(r"[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", section)
    )
    if len(addresses) != 1:
        raise ValueError("R004 must identify one sender; do not infer an account.")
    return addresses.pop()


def prepare(factory: SessionFactory, project: Path) -> list[dict[str, object]]:
    source = project / "docs/inquiry/handoff-2026-10-04/work-sample-fictional.txt"
    sender_identity = supplied_sender(project / "requests/INBOX.md")
    root = data_directory() / "outreach-attachments"
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = root / "sample-fictional-20261004-r1.txt"
    content = source.read_bytes()
    if target.exists() and target.read_bytes() != content:
        raise ValueError("Sample changed: create a new revision, do not overwrite")
    if not target.exists():
        target.write_bytes(content)
        target.chmod(0o600)
    with UnitOfWork(factory) as unit:
        s = unit.session
        assert s is not None
        venture = s.get(Venture, "v-receipt")
        assert venture is not None
        identity = "sample-fictional-20261004-r1"
        if s.get(Artifact, identity) is None:
            s.add(
                Artifact(
                    id=identity,
                    workspace_id=venture.workspace_id,
                    kind=ArtifactKind.DOCUMENT,
                    name="Fictional work-sample example",
                    location=str(target.resolve()),
                    media_type="text/plain",
                    content_digest=hashlib.sha256(content).hexdigest(),
                    semantic_version="r1",
                    metadata_json={
                        "fictional": True,
                        "authorized_attachment": True,
                        "canonical_reference": str(source),
                    },
                )
            )
    service = OutreachService(factory, [root])
    outputs = []
    for language, tone, subject, body in VARIANTS:
        draft = service.create(
            "v-receipt",
            DraftInput(
                purpose=(
                    "Ten-minute receiving-practitioner review; N003 adoption question"
                ),
                subject=subject,
                body_text=body,
                language=language,
                tone=tone,
                sender_identity=sender_identity,
                attachment_artifact_ids=[identity],
                related_request_id="R003",
            ),
            request_key="n003-review-" + language + "-" + tone,
            actor="agent:handoff-20261004",
        )
        outputs.append(
            {
                "id": draft["id"],
                "language": language,
                "tone": tone,
                "revision": draft["draft_revision"],
                "state": draft["state"],
                "unresolved_fields": draft["unresolved_fields"],
            }
        )
    return outputs


if __name__ == "__main__":
    engine = create_db_engine(load_settings().database_url)
    try:
        print(
            json.dumps(
                prepare(
                    create_session_factory(engine), Path(__file__).resolve().parents[1]
                ),
                indent=2,
            )
        )
    finally:
        engine.dispose()
