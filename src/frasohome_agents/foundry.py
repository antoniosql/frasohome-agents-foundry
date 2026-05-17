from __future__ import annotations

from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential

from .settings import Settings


class FoundryRuntime:
    def __init__(self, settings: Settings):
        settings.require_foundry()
        from azure.ai.projects import AIProjectClient

        self.settings = settings
        self.project = AIProjectClient(
            endpoint=settings.project_endpoint,
            credential=DefaultAzureCredential(),
        )
        self.openai = self.project.get_openai_client()

    def create_prompt_agent(self, name: str, instructions: str, tools: list[Any] | None = None) -> Any:
        from azure.ai.projects.models import PromptAgentDefinition

        return self.project.agents.create_version(
            agent_name=name,
            definition=PromptAgentDefinition(
                model=self.settings.model_deployment,
                instructions=instructions,
                tools=tools or [],
            ),
        )

    def upload_file(self, path: Path, purpose: str = "assistants") -> Any:
        files_client = getattr(self.project, "files", None)
        if files_client is None:
            raise RuntimeError("This azure-ai-projects SDK version does not expose project.files.")
        if hasattr(files_client, "upload"):
            return files_client.upload(file_path=str(path), purpose=purpose)
        if hasattr(files_client, "upload_and_poll"):
            return files_client.upload_and_poll(file_path=str(path), purpose=purpose)
        raise RuntimeError("This azure-ai-projects SDK version does not expose files.upload or files.upload_and_poll.")

    def create_vector_store(self, name: str, file_ids: list[str]) -> Any:
        candidates = [
            getattr(self.project, "vector_stores", None),
            getattr(self.project, "vectorstores", None),
        ]
        for client in candidates:
            if client is None:
                continue
            if hasattr(client, "create"):
                try:
                    return client.create(name=name, file_ids=file_ids)
                except TypeError:
                    return client.create(name=name, files=file_ids)
            if hasattr(client, "create_and_poll"):
                return client.create_and_poll(name=name, file_ids=file_ids)
        raise RuntimeError(
            "Could not create a vector store with the installed SDK. "
            "Create one in Foundry Portal or SDK and set FRASOHOME_VECTOR_STORE_ID."
        )

    def run_agent(self, agent_name: str, prompt: str, *, store: bool = True) -> Any:
        return self.openai.responses.create(
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference",
                }
            },
            input=prompt,
            store=store,
        )


def response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text
    output = getattr(response, "output", None) or []
    parts: list[str] = []
    for item in output:
        if getattr(item, "type", None) == "message":
            for content in getattr(item, "content", []) or []:
                value = getattr(content, "text", None)
                if value:
                    parts.append(value)
    return "\n".join(parts).strip()


def print_tool_calls(response: Any) -> list[str]:
    calls: list[str] = []
    for item in getattr(response, "output", []) or []:
        item_type = getattr(item, "type", "")
        if item_type.endswith("_call"):
            status = getattr(item, "status", "")
            calls.append(f"{item_type}: {status}")
    return calls
