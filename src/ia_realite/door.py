from dataclasses import dataclass
from collections.abc import Iterable
import gradio as gr

from .room import Room
from .entity_item import EntityItem
from .room_generator import randomize_room


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

    def _create_room(self, subject: str, preference: str = ""):
        self._room = Room(subject, preference)
        for member in self._registered_members:
            self._room.add_entity(
                entity_name=member.name, entity_system_prompt=member.system_prompt
            )

    def _generate_random_room_and_updates(
        self, room_subject: str, number_of_entities: int, preference: str = ""
    ):
        room = randomize_room(
            room_subject=room_subject,
            number_of_entities=number_of_entities,
            preference=preference,
        )[0]
        self._room = room
        self._registered_members.clear()
        for e in room.entities:
            self._registered_members.append(
                _RegisteredMember(name=e.name, system_prompt=e.system_prompt)
            )

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

        display = "## Registered Agents\n"
        for m in self._registered_members:
            display += f"- **{m.name}**: {m.system_prompt}\n"
        return display

    def _generate_random_room(
        self, room_subject: str, number_of_entities: int, preference: str = ""
    ):
        """Generate a random room and return updated UI values."""
        # Call your randomize_room function
        self._room = randomize_room(room_subject, number_of_entities, preference)[0]
        response = randomize_room(room_subject, number_of_entities, preference)[1]

        # Prepare outputs
        num_entities = len(self._room.entities)

        # Update visibility for entity columns
        visibilities = [
            gr.Column(visible=True) if i < num_entities else gr.Column(visible=False)
            for i in range(15)
        ]

        # Update entity names and prompts
        names = []
        prompts = []
        for i in range(15):
            if i < num_entities:
                names.append(response[i][0])
                prompts.append(response[i][1])
            else:
                names.append("")
                prompts.append("")

        # Return: subject, preference, agent_count, *visibilities, *names, *prompts
        return [room_subject, preference, num_entities] + visibilities + names + prompts

    def _heat_up(self, duration: int) -> Iterable[tuple[str, str]]:
        display = f"## Room : {self._room.subject}\n"
        for m in self._registered_members:
            display += f"- {m.name}: {m.system_prompt}\n"
        display += "---"

        logs = []
        for message in self._room.sweat(duration):  # type: ignore
            logs.append(message)
            yield "\n\n".join(logs), display

        yield "\n\n".join(logs), display

    def _generate_body(self) -> gr.Blocks:
        with gr.Blocks(css=EntityItem.CSS) as body:
            with gr.Tab("Room's painting"):
                gr.Markdown(f"# {self._TITLE}")

                # ----- Random room configuration -----
                add_random_btn = gr.Button("🎲 Random Room Setup", variant="secondary")

                # Hidden container that acts as popup
                with gr.Column(visible=False) as popup:
                    gr.Markdown("## Random Room Settings")
                    popup_room_subject = gr.Textbox(
                        label="Room's subject",
                        placeholder="Ex: How AI will take over cat's domination",
                    )
                    popup_room_preference = gr.Textbox(
                        label="Room's preference",
                        placeholder="Ex: Friendly discussion, formal debate, etc.",
                    )
                    number_of_entities = gr.Number(
                        label="Number of agents",
                        value=3,
                    )
                    with gr.Row():
                        generate_btn = gr.Button("Generate", variant="primary")
                        close_btn = gr.Button("Close")

                # Main configuration block (will be hidden when popup is shown)
                with gr.Column(visible=True) as main_config:
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

                    add_agent_btn = gr.Button(
                        "➕ Add Another Agent", variant="secondary"
                    )

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
                    ).then(
                        self._heat_up,
                        inputs=[steps],
                        outputs=[messages, room],
                    )

                # Close popup and show main config
                close_btn.click(
                    lambda: [gr.update(visible=False), gr.update(visible=True)],
                    [],
                    [popup, main_config],
                )

                # Show popup and hide main config
                add_random_btn.click(
                    lambda: [gr.update(visible=True), gr.update(visible=False)],
                    [],
                    [popup, main_config],
                )

                # Generate random room and update all UI
                generate_btn.click(
                    self._generate_random_room,
                    inputs=[
                        popup_room_subject,
                        number_of_entities,
                        popup_room_preference,
                    ],
                    outputs=[subject, preference, agent_count]
                    + entity_columns
                    + [comp["name"] for comp in entity_components]
                    + [comp["prompt"] for comp in entity_components],
                ).then(
                    lambda: [gr.update(visible=False), gr.update(visible=True)],
                    [],
                    [popup, main_config],
                )

            # inside Door._generate_body (replacing Chatboxes tab)
            with gr.Tab("Chatboxes"):
                @gr.render(inputs=room)
                def show_chatboxes(_):
                    if not self._room:
                        gr.Markdown("## Room hasn't started yet")
                        return
                    # Summary area (existing)
                    gr.Markdown("# Room's summary :")
                    gr.Markdown(self._room.generate_entity_summary())
                    gr.Markdown("---")
                    gr.Markdown("You can now talk to the participants.")

                    # fix closure: capture entity per chatbox
                    def make_chat_fn(entity):
                        def chat_fn(message, history=None):
                            return entity.talk(prompt=message)
                        return chat_fn

                    with gr.Row():
                        for e in self._room.entities:
                            gr.ChatInterface(
                                fn=make_chat_fn(e),
                                type="messages",
                                textbox=gr.Textbox(
                                    placeholder=f"Write a message to {e.name}",
                                    container=False,
                                    scale=7,
                                ),
                                title=f"Chat with {e.name}",
                            )

            with gr.Tab("Metrics"):
                gr.Markdown("# Metrics — visualiser la frugalité")
                # Controls
                metric_select = gr.Dropdown(
                    label="Select metric",
                    choices=[
                        "duration_s",
                        "power_w",
                        "energy_Wh",
                        "co2_g",
                        "tokens",
                        "tokens_per_Wh",
                    ],
                    value="co2_g",
                )
                sample_count = gr.Slider(label="Number of points", minimum=10, maximum=1000, step=10, value=200)
                refresh_btn = gr.Button("Refresh graph")

                plot_output = gr.Plot(label="Metric evolution")
                export_btn = gr.Button("Export CSV")

                # helper to produce matplotlib figure from Room metrics
                def _plot_metric(metric_name: str, count: int):
                    import pandas as pd
                    import matplotlib.pyplot as plt
                    if not self._room or not hasattr(self._room, "metrics"):
                        fig, ax = plt.subplots()
                        ax.text(0.5, 0.5, "No metrics yet", ha="center", va="center")
                        return fig
                    df = self._room.metrics_dataframe()
                    if df is None or df.empty or metric_name not in df.columns:
                        fig, ax = plt.subplots()
                        ax.text(0.5, 0.5, "Metric not available", ha="center", va="center")
                        return fig
                    series = df[metric_name].dropna().tail(count).reset_index(drop=True)
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.plot(series.index.values, series.values)
                    ax.set_title(f"{metric_name} (last {len(series)} points)")
                    ax.set_xlabel("sample index")
                    ax.set_ylabel(metric_name)
                    ax.grid(True)
                    return fig

                def _export_csv():
                    # return path to CSV stored by metrics_collector
                    import os
                    from .metrics_collector import OUT_CSV
                    if os.path.exists(OUT_CSV):
                        return OUT_CSV
                    return None

                refresh_btn.click(lambda m, c: _plot_metric(m, c), inputs=[metric_select, sample_count], outputs=[plot_output])
                # initial plot
                plot_output.figure = _plot_metric(metric_select.value, sample_count.value)
                export_btn.click(_export_csv, outputs=[])

            return body
