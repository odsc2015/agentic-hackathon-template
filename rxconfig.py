import reflex as rx

config = rx.Config(
    app_name="status200",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)