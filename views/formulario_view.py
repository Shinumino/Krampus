# views/formulario_view.py
import discord
from discord.ui import View, Button

class FormularioPersistentView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)  # persistente
        self.cog = cog

    @discord.ui.button(label="Iniciar Formulário", style=discord.ButtonStyle.green, custom_id="iniciar_formulario", emoji="📝")
    async def iniciar_formulario(self, interaction: discord.Interaction, button: Button):
        # Chama o método da cog que abre o modal
        await self.cog.iniciar_formulario_callback(interaction)