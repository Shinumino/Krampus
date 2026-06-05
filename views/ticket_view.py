# views/ticket_view.py
import discord
from discord.ui import View, Button

class TicketPersistentView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="❌ Fechar", style=discord.ButtonStyle.danger, custom_id="ticket_fechar", emoji="🔒")
    async def fechar_ticket(self, interaction: discord.Interaction, button: Button):
        if not await self.cog.verificar_permissao_staff(interaction):
            return await interaction.response.send_message("❌ Apenas staff pode fechar tickets!", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        await self.cog.fechar_ticket(interaction)

    @discord.ui.button(label="📦 Arquivar", style=discord.ButtonStyle.secondary, custom_id="ticket_arquivar", emoji="📋")
    async def arquivar_ticket(self, interaction: discord.Interaction, button: Button):
        if not await self.cog.verificar_permissao_staff(interaction):
            return await interaction.response.send_message("❌ Apenas staff pode arquivar tickets!", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        await self.cog.arquivar_ticket(interaction)