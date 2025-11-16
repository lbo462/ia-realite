from dataclasses import dataclass
from collections.abc import Iterable

import gradio as gr

from src.ia_realite.room import Room


@dataclass
class _RegisteredMember:
    name: str
    system_prompt: str

    def __str__(self):
        return f"{self.name}: {self.system_prompt}"


class Door:
    _TITLE = "🧠 Room Builder — Multi Agents IA"

    def __init__(self):
        self._room: Room | None = None
        self._registered_members: list[_RegisteredMember] = list()

    def open(self, wide_open: bool = False):
        body = self._generate_body()
        body.launch(share=wide_open)

    def _create_room(self, subject: str, preference: str = "") -> str:
        self._room = Room(subject, preference)
        for member in self._registered_members:
            self._room.add_entity(
                entity_name=member.name, entity_system_prompt=member.system_prompt
            )

        display = f"## Room : {self._room.subject}\n"
        for m in self._registered_members:
            display += f"- {m.name}: {m.system_prompt}\n"
        display += "---"
        return display

    def _register_new_member(self, name: str, system_prompt: str) -> str:
        self._registered_members.append(
            _RegisteredMember(name=name, system_prompt=system_prompt)
        )

        display = ""
        for m in self._registered_members:
            display += f"- {m.name}: {m.system_prompt}\n"
        return display

    def _heat_up(self, duration: int) -> Iterable[str]:
        logs = []
        for message in self._room.sweat(duration): # type: ignore
            logs.append(message)
            yield "\n\n".join(logs)

    def _generate_body(self) -> gr.Blocks:
        with gr.Blocks() as body:
            gr.Markdown(f"# {self._TITLE}")

            with gr.Row():
                subject = gr.Textbox(
                    label="Room's subject",
                    placeholder="Ex: How AI will take over cat's domination",
                )
                preference = gr.Textbox(
                    label="Room's preference",
                    placeholder="Ex: Friendly discussion, formal debate, etc.",
                )
                steps = gr.Number(label="Dialog size", value=5)

            gr.Markdown("## 👥 Add agents")

            with gr.Row():
                entity_name = gr.Textbox(label="Name", placeholder="John")
                entity_system_prompt = gr.Textbox(
                    label="Personalized prompt",
                    placeholder="Ex: You are a somebody stuck in an elevator",
                )

            add_button = gr.Button("➕ Add agent")

            registered_members = gr.Markdown()

            add_button.click(
                self._register_new_member,
                inputs=[entity_name, entity_system_prompt],
                outputs=[registered_members],
            )

            gr.Markdown("---")

            create_button = gr.Button("🚀 Create room")

            room = gr.Markdown()
            messages = gr.Markdown()

            create_button.click(self._create_room, inputs=[subject, preference], outputs=[room])
            create_button.click(
                self._heat_up,
                inputs=[steps],
                outputs=[messages],
            )

        return body
