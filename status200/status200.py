import reflex as rx
from rxconfig import config


class State(rx.State):
    text_input: str = ""
    response_text: str = ""

    def submit(self):
        self.response_text = f"Agent is thinking about: {self.text_input}"


def index() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.heading("SmartAgent AI", size="7", color_scheme="blue"),
                rx.spacer(),
                rx.color_mode.button(position="top-right"),
            ),
            padding_y="4",
            padding_x="6",
            border_bottom="1px solid #e0e0e0",
            width="100%",
            position="sticky",
            top="0",
            opacity="1",
            z_index="999",
            background_color=rx.color_mode_cond(light="white", dark="gray.800"),
            shadow="lg",
        ),

        rx.center(
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.heading("Your Query", size="6", text_align="left", width="100%"),
                        rx.text_area(
                            placeholder="Ask me anything, describe a task, or provide instructions...",
                            value=State.text_input,
                            on_change=State.set_text_input,
                            rows="6",
                            width="100%",
                            size="2",
                        ),
                        rx.vstack(
                            rx.upload(
                                rx.button("📤 Upload Image", color_scheme="teal", variant="outline", width="30%"),
                                accept=["image/*"],
                                max_files=1,
                                width="100%",
                            ),
                            rx.button("🚀 Get Response", on_click=State.submit, color_scheme="blue", size="3", width="100%"),
                            spacing="3",
                            width="100%",
                        ),
                        spacing="5",
                    ),
                    width="100%", 
                    padding="6",
                    border_radius="lg",
                    shadow="lg",
                ),

                rx.card(
                    rx.vstack(
                        rx.heading("Agent Response", size="6", text_align="left", width="100%"),
                        rx.text_area(
                            value=State.response_text,
                            is_read_only=True,
                            rows="12",
                            width="100%",
                            size="2",
                            background_color=rx.color_mode_cond(light="gray.50", dark="gray.700"),
                            border_color=rx.color_mode_cond(light="gray.200", dark="gray.600"),
                        ),
                    ),
                    width="100%",
                    padding="6",
                    border_radius="lg",
                    shadow="lg",
                ),

                rx.card(
                    rx.vstack(
                        rx.heading("Agent Settings", size="6", text_align="left", width="100%"),
                        rx.grid(
                            rx.select(
                                ["General AI", "Fitness Coach", "Nutritionist", "Productivity Assistant"],
                                placeholder="Choose Agent Type",
                                width="100%",
                            ),
                            rx.select(
                                ["Friendly", "Direct", "Motivational", "Analytical"],
                                placeholder="Tone / Style",
                                width="100%",
                            ),
                            rx.select(
                                ["Text-only", "Image + Text", "Task Planning", "Interactive Flow"],
                                placeholder="Response Mode",
                                width="100%",
                            ),
                            rx.select(
                                ["Beginner", "Intermediate", "Advanced"],
                                placeholder="Experience Level",
                                width="100%",
                            ),
                            columns="2",
                            spacing="4",
                            width="100%",
                        ),
                        rx.button("🧹 Clear Chat", color_scheme="red", variant="outline", align_self="end"),
                        spacing="5",
                    ),
                    width="100%", 
                    padding="6",
                    border_radius="lg",
                    shadow="lg",
                ),
                spacing="8",
                padding_y="8",
                max_width="75%", 
                                
                width="100%", 
            ),
            width="100%", 
        ),

        rx.box(
            rx.text("© 2025 SmartAgent AI Inc. · Built with Reflex", color="gray.600"),
            padding="4",
            text_align="center",
            font_size="sm",
            border_top="1px solid #e0e0e0",
            width="100%",
            background_color=rx.color_mode_cond(light="white", dark="gray.800"),
            bottom="0",
            z_index="999",
            shadow="lg",
        ),
        align="center",
        width="100%",
        min_height="100vh",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="full",
        accent_color="blue",
    ),
)
app.add_page(index)