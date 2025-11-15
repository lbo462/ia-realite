import gradio as gr
from src.ia_realite.room import Room

# État temporaire pour les agents ajoutés
def add_agent(name, personality, agent_list):
    """Ajoute un agent à la liste dynamique."""
    if not name or not personality:
        return agent_list, gr.update(value="Nom et personnalité requis")

    agent_list.append((name, personality))

    display = "\n".join([f"- **{n}** : {p}" for n, p in agent_list])
    return agent_list, gr.update(value=display)

# Création de la room
def create_room(subject, steps, agent_list):
    if not subject:
        return None, "⚠️ Donne un sujet à la Room !"

    if len(agent_list) == 0:
        return None, "⚠️ Ajoute au moins un agent !"

    # Créer la room
    room = Room(subject)

    # Ajouter les agents
    for name, personality in agent_list:
        room.add_entity(name, personality)

    # Générer les messages
    room.sweat(int(steps))

    # Format sortie
    logs = ""
    for m in room.memory.messages:
        logs += m["content"] + "  \n\n"

    logs_markdown = (
        f"### Room créée : {subject}\n"
        f"### Agents :\n" +
        "\n".join([f"- **{name}** *(hover: {p})*" for name, p in agent_list]) +
        "\n\n### Messages générés :\n" +
        logs
    )

    return room, logs_markdown


# ---------------------------------------------------------
# ---------------------- GRADIO UI ------------------------
# ---------------------------------------------------------

with gr.Blocks() as demo:

    gr.Markdown("# 🧠 Room Builder — Multi Agents IA")

    with gr.Row():
        subject = gr.Textbox(label="Sujet de la Room", placeholder="Ex: Usage of AI")
        steps = gr.Number(label="Sweat steps", value=5)

    gr.Markdown("## 👥 Ajouter des agents")

    with gr.Row():
        agent_name = gr.Textbox(label="Nom de l'agent", placeholder="Agent A")
        agent_personality = gr.Textbox(
            label="System prompt / personnalité",
            placeholder="Ex: very creative artist"
        )

    add_button = gr.Button("➕ Ajouter l'agent")

    agent_list_display = gr.Markdown("*(aucun agent pour le moment)*")
    agent_list_state = gr.State([])

    add_button.click(
        add_agent,
        inputs=[agent_name, agent_personality, agent_list_state],
        outputs=[agent_list_state, agent_list_display]
    )

    gr.Markdown("---")
    create_button = gr.Button("🚀 Créer la Room")

    room_state = gr.State(None)
    output_display = gr.Markdown()

    create_button.click(
        create_room,
        inputs=[subject, steps, agent_list_state],
        outputs=[room_state, output_display]
    )

demo.launch()
