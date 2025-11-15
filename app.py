import gradio as gr
from src.ia_realite.room import Room

# État temporaire pour les agents ajoutés
def add_agent(name, personality, agent_list):
    """Ajoute un agent à la liste dynamique (évite le flash et gère l'erreur sans cacher la liste)."""
    # keep current display based on agent_list (no gr.update for the Markdown)
    current_display = "\n".join([f"- **{n}** : {p}" for n, p in agent_list]) if agent_list else "*(aucun agent pour le moment)*"

    if not name or not personality:
        # Ne pas écraser l'affichage des agents : renvoyer la chaîne existante + message d'erreur
        return agent_list, current_display, gr.update(value=""), gr.update(value=""), "⚠️ Nom et personnalité requis"

    # Create a new list instead of mutating the incoming one (prevents UI flicker)
    new_list = list(agent_list) + [(name, personality)]

    display = "\n".join([f"- **{n}** : {p}" for n, p in new_list])
    return new_list, display, gr.update(value="", interactive=True), gr.update(value="", interactive=True), ""


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
    for message in room.sweat(int(steps)):
        print(message)

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

    return room, logs_markdown, gr.update(interactive=True), gr.update(interactive=True)



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

    add_button = gr.Button("➕ Ajouter l'agent", elem_id="add_agent_btn")

    agent_list_display = gr.Markdown("*(aucun agent pour le moment)*")
    error_display = gr.Markdown("", visible=True)
    agent_list_state = gr.State([])

    add_button.click(
        add_agent,
        inputs=[agent_name, agent_personality, agent_list_state],
        outputs=[agent_list_state, agent_list_display, agent_name, agent_personality, error_display]
    )


    gr.Markdown("---")
    create_button = gr.Button("🚀 Créer la Room", elem_id="create_room_btn")

    room_state = gr.State(None)
    output_display = gr.Markdown()

    create_button.click(
        create_room,
        inputs=[subject, steps, agent_list_state],
        outputs=[room_state, output_display, add_button, create_button]
    )

demo.launch()