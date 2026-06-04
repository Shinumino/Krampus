import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
import re

ROLE_IDS = {
    "DPS": 1440390981307465949,
    "TANK": 1440391288615735380,
    "HEALER": 1440391235268378654
}

ALLOWED_ROLES = [
    1449931317675429960,  # DEV
    1442625294078050456,  # STAFF,
]

LOGS_CHANNEL_ID = 1450014685725200416

# Opções para boss (pode adicionar mais depois)
BOSSES = [
    "GUILD BOSS 10 PLAYERS",
    # Adicione mais bosses aqui quando quiser:
    # "NOME DO BOSS",
]

# Dias da semana
DIAS_SEMANA = [
    "SEGUNDA",
    "TERÇA", 
    "QUARTA",
    "QUINTA",
    "SEXTA",
    "SÁBADO",
    "DOMINGO",
]

# Cores personalizadas
COR_PARTICIPAR = 0x57F287  # Verde
COR_SAIR = 0xED4245        # Vermelho
COR_FINALIZAR = 0x5865F2   # Azul
COR_BORDA_ATIVA = 0x23272A # Cinza escuro

# EMOJIS PERSONALIZADOS - IDs reais fornecidos
EMOJIS = {
    "SHOT": "<a:whitearrow1213:1451780689845555282>",      # Emoji animado branco para SHOT CALLER
    "TANK": "<a:orangearrow1213:1451795513790959747>",     # Emoji animado laranja para TANK
    "HEALER": "<a:greenarrow1213:1451780601270112276>",    # Emoji animado verde para HEALER
    "DPS": "<a:purplearrow1213:1451780718748504165>",      # Emoji animado roxo para DPS
}

class AlistamentoEmbed:
    def __init__(self, boss, dia, hora, mastery, shot_caller):
        self.boss = boss
        self.dia = dia
        self.hora = hora
        self.mastery = mastery
        self.shot_caller = shot_caller
        self.participants = {
            "TANK": [],
            "HEALER": [],
            "DPS": []
        }
    
    def create_embed(self):
        """Cria embed com cor personalizada e emojis"""
        embed = discord.Embed(
            title=f"**{self.boss} - {self.dia} - {self.hora}**",
            description=f"**MASTERY MIN:** **{self.mastery}**\n\n"
                       f"{EMOJIS['SHOT']} **SHOT CALLER:** {self.shot_caller.mention}",
            color=COR_BORDA_ATIVA
        )
        
        # Construir a lista VERTICAL com emojis específicos para cada role
        lista_vertical = []
        
        # TANK (sempre 1 linha) - emoji laranja
        tank_value = f"<@{self.participants['TANK'][0]}>" if self.participants['TANK'] else ""
        lista_vertical.append(f"{EMOJIS['TANK']} **TANK:** {tank_value}")
        
        # HEALER (sempre 2 linhas) - emoji verde
        for i in range(2):
            healer_value = f"<@{self.participants['HEALER'][i]}>" if i < len(self.participants['HEALER']) else ""
            lista_vertical.append(f"{EMOJIS['HEALER']} **HEALER:** {healer_value}")
        
        # DPS (sempre 6 linhas) - emoji roxo
        for i in range(6):
            dps_value = f"<@{self.participants['DPS'][i]}>" if i < len(self.participants['DPS']) else ""
            lista_vertical.append(f"{EMOJIS['DPS']} **DPS:** {dps_value}")
        
        # Juntar tudo em um campo único
        embed.add_field(
            name="\u200b",  # Nome vazio
            value="\n".join(lista_vertical),
            inline=False
        )
        
        # Rodapé atualizado
        embed.set_footer(text="Guilda Wanted © | Community Server")
        
        return embed
    
    def is_user_participating(self, user_id):
        """Verifica se um usuário já está participando"""
        for role_list in self.participants.values():
            if user_id in role_list:
                return True
        return False
    
    def get_user_class(self, user_id):
        """Retorna a classe de um usuário participante"""
        for role_name, participants in self.participants.items():
            if user_id in participants:
                return role_name
        return None
    
    def add_participant(self, user_id, user_roles):
        # Determinar a classe do usuário
        user_class = None
        for role_name, role_id in ROLE_IDS.items():
            if role_id in user_roles:
                user_class = role_name
                break
        
        if not user_class:
            return False, "Você precisa ter um dos cargos: DPS, TANK ou HEALER para participar."
        
        # Verificar se já está participando
        if self.is_user_participating(user_id):
            return False, "Você já está participando!"
        
        # Verificar limite da classe
        limit = 1 if user_class == "TANK" else 2 if user_class == "HEALER" else 6
        
        if len(self.participants[user_class]) >= limit:
            return False, f"Todos os slots de {user_class} já estão preenchidos!"
        
        # Adicionar participante
        self.participants[user_class].append(user_id)
        return True, f"Você entrou como {user_class}!"
    
    def remove_participant(self, user_id):
        for role_name in self.participants:
            if user_id in self.participants[role_name]:
                self.participants[role_name].remove(user_id)
                return True, f"Você saiu do alistamento!"
        return False, "Você não estava participando."

class AlistamentoView(View):
    def __init__(self, alistamento_embed, command_user_id):
        super().__init__(timeout=None)
        self.alistamento = alistamento_embed
        self.command_user_id = command_user_id
        self.create_buttons()
    
    def create_buttons(self):
        """Cria os botões fixos"""
        self.clear_items()
        
        # Botão PARTICIPAR (sempre verde)
        participate_button = Button(
            label="PARTICIPAR 🎉",
            style=discord.ButtonStyle.success,
            custom_id="participar"
        )
        participate_button.callback = self.participar_callback
        
        # Botão SAIR (sempre vermelho)
        sair_button = Button(
            label="SAIR 💨",
            style=discord.ButtonStyle.danger,
            custom_id="sair"
        )
        sair_button.callback = self.sair_callback
        
        # Botão FINALIZAR
        finalize_button = Button(
            label="FINALIZAR 📋",
            style=discord.ButtonStyle.primary,
            custom_id="finalizar"
        )
        finalize_button.callback = self.finalize_callback
        
        self.add_item(participate_button)
        self.add_item(sair_button)
        self.add_item(finalize_button)
    
    async def update_message_for_user(self, interaction: discord.Interaction):
        """Atualiza a mensagem após interação"""
        embed = self.alistamento.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def participar_callback(self, interaction: discord.Interaction):
        """Callback do botão PARTICIPAR"""
        # Verificar se é o SHOT CALLER
        if interaction.user.id == self.command_user_id:
            await interaction.response.send_message(
                "Você é o SHOT CALLER e não pode se inscrever!",
                ephemeral=True
            )
            return
        
        # Verificar se o usuário já está participando
        if self.alistamento.is_user_participating(interaction.user.id):
            await interaction.response.send_message(
                "Você já está participando! Use o botão SAIR para sair.",
                ephemeral=True
            )
            return
        
        # Adicionar participante
        user_role_ids = [role.id for role in interaction.user.roles]
        success, message = self.alistamento.add_participant(interaction.user.id, user_role_ids)
        
        if success:
            await self.update_message_for_user(interaction)
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    
    async def sair_callback(self, interaction: discord.Interaction):
        """Callback do botão SAIR"""
        # Verificar se é o SHOT CALLER
        if interaction.user.id == self.command_user_id:
            await interaction.response.send_message(
                "Você é o SHOT CALLER e não pode sair!",
                ephemeral=True
            )
            return
        
        # Verificar se o usuário está participando
        if not self.alistamento.is_user_participating(interaction.user.id):
            await interaction.response.send_message(
                "Você não está participando! Use o botão PARTICIPAR para entrar.",
                ephemeral=True
            )
            return
        
        # Remover participante
        success, message = self.alistamento.remove_participant(interaction.user.id)
        
        if success:
            await self.update_message_for_user(interaction)
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    
    async def finalize_callback(self, interaction: discord.Interaction):
        """Callback do botão FINALIZAR"""
        # Verificar permissão
        user_roles = [role.id for role in interaction.user.roles]
        user_has_permission = (
            any(role_id in ALLOWED_ROLES for role_id in user_roles) or
            interaction.user.guild_permissions.administrator
        )
        
        if not user_has_permission:
            await interaction.response.send_message(
                "❌ Você não tem permissão para finalizar alistamentos!",
                ephemeral=True
            )
            return
        
        # Enviar para o canal de logs
        logs_channel = interaction.client.get_channel(LOGS_CHANNEL_ID)
        if logs_channel:
            # Criar embed finalizado (com cor diferente e rodapé atualizado)
            old_embed = interaction.message.embeds[0]
            embed_dict = old_embed.to_dict()
            embed_dict["color"] = 0x808080  # Cinza para indicar finalizado
            embed_dict["title"] = f"[FINALIZADO] {old_embed.title}"
            
            # Garantir que o rodapé esteja correto
            if "footer" in embed_dict:
                embed_dict["footer"]["text"] = "Guilda Wanted © | Community Server"
            
            final_embed = discord.Embed.from_dict(embed_dict)
            final_embed.set_footer(text="Guilda Wanted © | Community Server")
            
            # Enviar para logs
            await logs_channel.send(embed=final_embed)
            
            # APAGAR a mensagem original do chat
            await interaction.message.delete()
            
            await interaction.response.send_message(
                "✅ Alistamento finalizado, mensagem apagada e enviada para os logs!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Canal de logs não encontrado!",
                ephemeral=True
            )

class Alistamento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="alistamento", description="Cria um novo alistamento para boss")
    @app_commands.describe(
        boss="Nome do Boss",
        dia="Dia da Semana",
        hora="Formato 00:00",
        mastery="Mastery requerida"
    )
    async def alistamento(
        self, 
        interaction: discord.Interaction,
        boss: str,
        dia: str,
        hora: str,
        mastery: str
    ):
        """Cria um alistamento para boss com seleções para boss e dia"""
        # Verificar permissão
        user_roles = [role.id for role in interaction.user.roles]
        user_has_permission = (
            any(role_id in ALLOWED_ROLES for role_id in user_roles) or
            interaction.user.guild_permissions.administrator
        )
        
        if not user_has_permission:
            await interaction.response.send_message(
                "❌ Você não tem permissão para usar este comando!",
                ephemeral=True
            )
            return
        
        # Validar boss
        if boss not in BOSSES:
            await interaction.response.send_message(
                f"❌ Boss inválido! Opções disponíveis: {', '.join(BOSSES)}",
                ephemeral=True
            )
            return
        
        # Validar dia
        if dia.upper() not in DIAS_SEMANA:
            await interaction.response.send_message(
                f"❌ Dia inválido! Opções disponíveis: {', '.join(DIAS_SEMANA)}",
                ephemeral=True
            )
            return
        
        # Validar formato da hora
        if not re.match(r'^([0-1][0-9]|2[0-3]):([0-5][0-9])$', hora):
            await interaction.response.send_message(
                "❌ Formato de hora inválido! Use o formato **00:00** (ex: 20:30)",
                ephemeral=True
            )
            return
        
        # Validar mastery (deve ser número)
        if not mastery.isdigit():
            await interaction.response.send_message(
                "❌ Mastery deve conter apenas números!",
                ephemeral=True
            )
            return
        
        # Criar alistamento
        alistamento_embed = AlistamentoEmbed(boss, dia.upper(), hora, mastery, interaction.user)
        
        # Criar embed inicial
        embed = alistamento_embed.create_embed()
        view = AlistamentoView(alistamento_embed, interaction.user.id)
        
        # Enviar mensagem
        await interaction.response.send_message(embed=embed, view=view)
    
    @alistamento.autocomplete("boss")
    async def boss_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        # Filtra os bosses baseado no que o usuário está digitando
        filtered_bosses = [
            app_commands.Choice(name=boss, value=boss)
            for boss in BOSSES
            if current.lower() in boss.lower()
        ]
        return filtered_bosses[:25]  # Discord limita a 25 opções
    
    @alistamento.autocomplete("dia")
    async def dia_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        # Filtra os dias baseado no que o usuário está digitando
        filtered_dias = [
            app_commands.Choice(name=dia, value=dia)
            for dia in DIAS_SEMANA
            if current.lower() in dia.lower()
        ]
        return filtered_dias[:25]

async def setup(bot):
    await bot.add_cog(Alistamento(bot))