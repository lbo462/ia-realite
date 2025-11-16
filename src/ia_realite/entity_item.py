import os
from pathlib import Path
import gradio as gr


class EntityItem:
    """A component representing an agent with avatar, name, and prompt."""

    # CSS styles for the entity items
    CSS = """
        .entity-grid {
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important;
            gap: 16px !important;
            width: 100% !important;
        }
        .entity-item-wrapper {
            width: 100% !important;
        }
        .entity-item {
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 12px;
            background: #fafafa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 100% !important;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .entity-item:hover {
            border-color: #2196F3;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .avatar-container {
            position: relative;
            width: 100px;
            height: 100px;
            margin: 0 auto 12px auto;
        }
        .avatar-container img {
            border-radius: 50% !important;
            object-fit: cover !important;
            width: 100px !important;
            height: 100px !important;
        }
        .remove-btn {
            position: absolute !important;
            top: -8px !important;
            right: -8px !important;
            z-index: 10 !important;
            min-width: 28px !important;
            width: 28px !important;
            height: 28px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            background: #ff4444 !important;
            color: white !important;
            font-size: 16px !important;
            line-height: 1 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        /* Hide the expand/fullscreen button on avatar images */
        .entity-item .image-container button {
            display: none !important;
        }
        .entity-item button[aria-label*="screen"] {
            display: none !important;
        }
    """

    def __init__(self, index: int):
        """
        Args:
            index: Unique identifier for this entity item
        """
        self.index = index
        self.container = None
        # Get the absolute path to the avatar image
        self._avatar_path = str(Path(__file__).parent / "assets" / "avatar.png")
        if not os.path.exists(self._avatar_path):
            self._avatar_path = None  # Will use emoji fallback

    def render(self):
        """Renders the entity item component."""
        with gr.Column(visible=False, elem_classes="entity-item-wrapper") as col:
            self.container = col
            with gr.Column(elem_classes="entity-item"):
                # Avatar with remove button overlay
                with gr.Column(elem_classes="avatar-container"):
                    if self._avatar_path:
                        gr.Image(
                            value=self._avatar_path,
                            label=None,
                            show_label=False,
                            interactive=False,
                            height=100,
                            width=100,
                            container=False,
                            show_download_button=False,
                            show_share_button=False,
                        )
                    else:
                        gr.Markdown("# 👤")

                # Name input
                name_input = gr.Textbox(
                    label="Name",
                    placeholder="Agent",
                    container=True,
                )

                # System prompt input
                prompt_input = gr.Textbox(
                    label="Prompt",
                    placeholder="Role description...",
                    lines=2,
                    container=True,
                )

        return col, name_input, prompt_input
