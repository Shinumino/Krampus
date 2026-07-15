# cogs/andares.py
# Comando /andares: alistamento no modo andares (1 TANK / 2 HEALER / 7 DPS).
#
# Este arquivo é SÓ a interface do comando. Todo o motor (embed, botões,
# reserva, lembretes, finalização, histórico) vive no cog Alistamento
# (cogs/alistamento.py) e é acessado via bot.get_cog("Alistamento"),
# o mesmo padrão que o formulário usa para falar com o ticket.
# Vantagem de estar separado: um erro aqui derruba só o /andares.

import discord
from discord import app_commands
from discord.ext import commands

from heroes import DIAS_SEMANA


class Andares(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="andares", description="Cria um alistamento para andares (1 TANK, 2 HEALER, 7 DPS)")
    @app_commands.guild_only()
    @app_commands.describe(
        andar="Quais andares (ex: 80, 90-100)",
        dia="Dia da Semana",
        hora="Formato 00:00",
        mastery="Mastery requerida"
    )
    async def andares(
        self,
        interaction: discord.Interaction,
        andar: str,
        dia: str,
        hora: str,
        mastery: str
    ):
        """Cria um alistamento de andares com a party 1 TANK / 2 HEALER / 7 DPS"""
        alistamentos = self.bot.get_cog("Alistamento")
        if alistamentos is None:
            await interaction.response.send_message(
                "❌ O módulo de alistamento não está carregado.", ephemeral=True
            )
            return

        andar = andar.strip()
        if not andar or len(andar) > 40:
            await interaction.response.send_message(
                "❌ Informe quais andares (ex: **80** ou **90-100**)!", ephemeral=True
            )
            return
        await alistamentos.criar_alistamento(
            interaction, f"ANDARES {andar.upper()}", dia, hora, mastery, modo="andares"
        )

    @andares.autocomplete("dia")
    async def dia_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=dia, value=dia)
            for dia in DIAS_SEMANA
            if current.lower() in dia.lower()
        ][:25]


async def setup(bot):
    await bot.add_cog(Andares(bot))
