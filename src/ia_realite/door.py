from dataclasses import dataclass
from collections.abc import Iterable
import gradio as gr

from .room import Room
from .entity_item import EntityItem


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

    def _add_agent(self, current_count):
        """Shows one more agent card."""
        new_count = min(current_count + 1, 15)  # Cap at 15
        # Return visibility states for all possible agent cards
        visibilities = [
            gr.Column(visible=True) if i < new_count else gr.Column(visible=False)
            for i in range(15)
        ]
        return [new_count] + visibilities

    def _collect_entities(self, *args) -> str:
        """Collects all entity data from the form."""
        self._registered_members.clear()

        # Args come in groups of 2: name, prompt
        for i in range(0, len(args), 2):
            if i + 1 < len(args):
                name = args[i]
                prompt = args[i + 1]
                if name and prompt:  # Only add if both fields are filled
                    self._registered_members.append(
                        _RegisteredMember(name=name, system_prompt=prompt)
                    )

    def _heat_up(self, duration: int) -> Iterable[str]:
        logs = []
        for message in self._room.sweat(duration):  # type: ignore
            logs.append(message)
            yield "\n\n".join(logs)

    def _generate_body(self) -> gr.Blocks:
        with gr.Blocks(css=EntityItem.CSS) as body:
            with gr.Tab("Room's painting"):
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

                # Track the number of visible agents
                agent_count = gr.State(value=2)

                # Container for entity items - using grid layout
                entity_columns = []
                entity_components = []

                # Create grid container
                with gr.Column(elem_classes="entity-grid"):
                    # Create 15 possible entity items (2 visible initially)
                    for i in range(15):
                        entity_item = EntityItem(index=i)
                        col, name_input, prompt_input = entity_item.render()

                        if i < 2:
                            col.visible = True

                        entity_columns.append(col)
                        entity_components.append(
                            {
                                "col": col,
                                "name": name_input,
                                "prompt": prompt_input,
                                "index": i,
                            }
                        )

                add_agent_btn = gr.Button("➕ Add Another Agent", variant="secondary")

                # Wire up the add button
                add_agent_btn.click(
                    self._add_agent,
                    inputs=[agent_count],
                    outputs=[agent_count] + entity_columns,
                )

                # Collect all entity inputs for processing
                all_inputs = []
                for comp in entity_components:
                    all_inputs.extend([comp["name"], comp["prompt"]])

                create_button = gr.Button("🚀 Create room")
                room = gr.Markdown()
                messages = gr.Markdown()

                create_button.click(
                    self._collect_entities,
                    inputs=all_inputs,
                ).then(
                    self._create_room,
                    inputs=[subject, preference],
                    outputs=[room],
                ).then(
                    self._heat_up,
                    inputs=[steps],
                    outputs=[messages],
                )

            with gr.Tab("Chatboxes"):

                @gr.render(inputs=room)
                def show_chatboxes(_):
                    if not self._room:
                        gr.Markdown("## Room hasn't started yet")
                    else:
                        gr.Markdown("# Room's summary :")
                        gr.Markdown(self._room.generate_entity_summary())

                        gr.Markdown("---")
                        gr.Markdown("You can now talk to the participants.")

                        with gr.Row():
                            for e in self._room.entities:
                                gr.ChatInterface(
                                    fn=lambda x, _: e.talk(x),
                                    type="messages",
                                    textbox=gr.Textbox(
                                        placeholder=f"Write a message to {e.name}",
                                        container=False,
                                        scale=7,
                                    ),
                                    title=f"Chat with {e.name}",
                                )

        return body
