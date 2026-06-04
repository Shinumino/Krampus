import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
import os
import sys
from typing import Optional, Dict, List, Any

# Adiciona o diretório pai ao path para importar utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importação dos dados centralizados
from utils.emojis import WEAPON_EMOJIS, CLASS_EMOJIS
from utils.roles import CLASS_ROLES, AUTO_ROLES, PERMISSION_ROLES, OTHER_ROLES

# Mapeamento de Main Weapons para Classes
WEAPON_CLASS_MAPPING = {
    "Mo blade": "TANK",
    "Nameless Sword": "DPS",
    "Panacea Fan": "HEALER",
    "Strategic Sword": "DPS",
    "Vernal Umbrella": "DPS",
}

# Cores dos botões
COR_PARTICIPAR = 0x57F287  # Verde
COR_SAIR = 0xED4245        # Vermelho
COR_FINALIZAR = 0x5865F2   # Azul
COR_DELETAR = 0xED4245     # Vermelho (para deletar)
COR_BORDA_ATIVA = 0x23272A # Cinza escuro
COR_BORDA_FINALIZADA = 0x808080  # Cinza (para lista finalizada)

# Opções para os dropdowns COM EMOJIS REAIS
MAIN_WEAPON_OPTIONS = [
    discord.SelectOption(
        label="Mo blade",
        value="Mo blade",
        emoji=WEAPON_EMOJIS["Mo blade"]
    ),
    discord.SelectOption(
        label="Nameless Sword",
        value="Nameless Sword",
        emoji=WEAPON_EMOJIS["Nameless Sword"]
    ),
    discord.SelectOption(
        label="Panacea Fan",
        value="Panacea Fan",
        emoji=WEAPON_EMOJIS["Panacea Fan"]
    ),
    discord.SelectOption(
        label="Strategic Sword",
        value="Strategic Sword",
        emoji=WEAPON_EMOJIS["Strategic Sword"]
    ),
    discord.SelectOption(
        label="Vernal Umbrella",
        value="Vernal Umbrella",
        emoji=WEAPON_EMOJIS["Vernal Umbrella"]
    ),
]

SECOND_WEAPON_OPTIONS = [
    discord.SelectOption(
        label="Strategic Sword",
        value="Strategic Sword",
        emoji=WEAPON_EMOJIS["Strategic Sword"]
    ),
    discord.SelectOption(
        label="Nameless Spear",
        value="Nameless Spear",
        emoji=WEAPON_EMOJIS["Nameless Spear"]
    ),
    discord.SelectOption(
        label="Stormbreaker Spear",
        value="Stormbreaker Spear",
        emoji=WEAPON_EMOJIS["Stormbreaker Spear"]
    ),
    discord.SelectOption(
        label="Heavenquaker Spear",
        value="Heavenquaker Spear",
        emoji=WEAPON_EMOJIS["Heavenquaker Spear"]
    ),
    discord.SelectOption(
        label="Soulshade Umbrella",
        value="Soulshade Umbrella",
        emoji=WEAPON_EMOJIS["Soulshade Umbrella"]
    ),
    discord.SelectOption(
        label="Vernal Umbrella",
        value="Vernal Umbrella",
        emoji=WEAPON_EMOJIS["Vernal Umbrella"]
    ),
    discord.SelectOption(
        label="Inkwell Fan",
        value="Inkwell Fan",
        emoji=WEAPON_EMOJIS["Inkwell Fan"]
    ),
    discord.SelectOption(
        label="Mortal Rope Dart",
        value="Mortal Rope Dart",
        emoji=WEAPON_EMOJIS["Mortal Rope Dart"]
    ),
    discord.SelectOption(
        label="Infernal Twinblades",
        value="Infernal Twinblades",
        emoji=WEAPON_EMOJIS["Infernal Twinblades"]
    ),
]

class WeaponSelectView(View):
    """View para seleção de armas com estado gerenciado e persistência"""

    def __init__(self, gvg_embed, main_view, user_id: int):
        # Reduzido para 5 minutos para evitar problemas de timeout
        super().__init__(timeout=300)  # 5 minutos
        self.gvg_embed = gvg_embed
        self.main_view = main_view
        self.user_id = user_id  # Guardar user_id para validação
        self.main_weapon: Optional[str] = None
        self.second_weapon: Optional[str] = None
        self.state = "SELECTING_MAIN"  # Estados: SELECTING_MAIN, SELECTING_SECOND, REVIEWING
        self.message: Optional[discord.Message] = None  # Guardar referência à mensagem

        self._setup_initial_view()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verifica se o usuário que interagiu é o dono da view"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Esta seleção pertence a outro usuário!",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        """Limpeza quando a view expirar"""
        try:
            if self.message:
                await self.message.edit(
                    content="⏰ **Tempo esgotado!** A seleção expirou por inatividade.\n"
                           "Clique em PARTICIPAR novamente para recomeçar.",
                    view=None,
                    embed=None
                )
        except:
            pass  # Ignorar erros se a mensagem já foi deletada

    def _setup_initial_view(self) -> None:
        """Configura a view inicial baseada no estado atual"""
        self.clear_items()

        if self.state == "SELECTING_MAIN":
            self._add_main_select()
            self._add_cancel_button()

        elif self.state == "SELECTING_SECOND":
            self._add_second_select()
            self._add_back_button()
            self._add_cancel_button()

        elif self.state == "REVIEWING":
            self._add_confirm_button()
            self._add_edit_button()
            self._add_cancel_button()

    def _add_main_select(self) -> None:
        """Adiciona dropdown para Main Weapon - CORRIGIDO: SEM default=True"""
        placeholder = "Selecione sua Main Weapon"
        if self.main_weapon and self.state == "SELECTING_MAIN":
            # Modo edição: mostrar qual era a anterior
            placeholder = f"Anterior: {self.main_weapon} - Selecione para mudar"

        # NUNCA usar default=True - causa bugs no Discord.py
        main_select = Select(
            placeholder=placeholder,
            options=MAIN_WEAPON_OPTIONS,  # Opções ORIGINAIS sem modificação
        )
        main_select.callback = self._main_select_callback
        self.add_item(main_select)

    def _add_second_select(self) -> None:
        """Adiciona dropdown para Second Weapon com TODAS as opções"""
        placeholder = "Selecione sua Second Weapon"
        if self.main_weapon:
            placeholder = f"Main: {self.main_weapon} - Selecione Second Weapon"

        second_select = Select(
            placeholder=placeholder,
            options=SECOND_WEAPON_OPTIONS,  # TODAS as opções
        )
        second_select.callback = self._second_select_callback
        self.add_item(second_select)

    def _add_confirm_button(self) -> None:
        """Adiciona botão Confirmar"""
        confirm_button = Button(
            label="Confirmar ✅",
            style=discord.ButtonStyle.success,
        )
        confirm_button.callback = self._confirm_callback
        self.add_item(confirm_button)

    def _add_edit_button(self) -> None:
        """Adiciona botão Editar"""
        edit_button = Button(
            label="Editar 🔄",
            style=discord.ButtonStyle.secondary,
        )
        edit_button.callback = self._edit_callback
        self.add_item(edit_button)

    def _add_back_button(self) -> None:
        """Adiciona botão Voltar"""
        back_button = Button(
            label="Voltar ↩️",
            style=discord.ButtonStyle.secondary,
        )
        back_button.callback = self._back_callback
        self.add_item(back_button)

    def _add_cancel_button(self) -> None:
        """Adiciona botão Cancelar"""
        cancel_button = Button(
            label="Cancelar ❌",
            style=discord.ButtonStyle.danger,
        )
        cancel_button.callback = self._cancel_callback
        self.add_item(cancel_button)

    async def _main_select_callback(self, interaction: discord.Interaction) -> None:
        """Callback da seleção da Main Weapon"""
        try:
            await interaction.response.defer()
        except:
            # Se não conseguir deferir, a interação expirou
            await interaction.followup.send(
                "⏰ **Tempo expirado!** Por favor, clique em PARTICIPAR novamente.",
                ephemeral=True
            )
            return

        selected_main = interaction.data["values"][0]

        # Se selecionou a mesma arma que já tinha (modo edição), apenas continuar
        if selected_main == self.main_weapon and self.main_weapon is not None:
            # Já tinha essa main, vai direto para second
            self.state = "SELECTING_SECOND"
            self._setup_initial_view()

            visual_class = WEAPON_CLASS_MAPPING.get(self.main_weapon, "DESCONHECIDO")
            main_emoji = WEAPON_EMOJIS.get(self.main_weapon, "⚔️")

            try:
                await interaction.edit_original_response(
                    content=f"{main_emoji} **Main Weapon mantida:** {self.main_weapon}\n"
                           f"*(Você aparecerá como **{visual_class}** na lista)*\n\n"
                           f"**Agora selecione sua Second Weapon:**",
                    view=self
                )
            except:
                # Se falhar ao editar, tentar enviar nova mensagem
                await interaction.followup.send(
                    f"{main_emoji} **Main Weapon mantida:** {self.main_weapon}\n"
                    f"*(Você aparecerá como **{visual_class}** na lista)*\n\n"
                    f"**Agora selecione sua Second Weapon:**",
                    view=self,
                    ephemeral=True
                )
            return

        # Nova seleção de Main Weapon
        self.main_weapon = selected_main
        self.state = "SELECTING_SECOND"
        self._setup_initial_view()

        visual_class = WEAPON_CLASS_MAPPING.get(self.main_weapon, "DESCONHECIDO")
        main_emoji = WEAPON_EMOJIS.get(self.main_weapon, "⚔️")

        try:
            await interaction.edit_original_response(
                content=f"{main_emoji} **Main Weapon selecionada:** {self.main_weapon}\n"
                       f"*(Você aparecerá como **{visual_class}** na lista)*\n\n"
                       f"**Agora selecione sua Second Weapon:**",
                view=self
            )
        except:
            await interaction.followup.send(
                f"{main_emoji} **Main Weapon selecionada:** {self.main_weapon}\n"
                f"*(Você aparecerá como **{visual_class}** na lista)*\n\n"
                f"**Agora selecione sua Second Weapon:**",
                view=self,
                ephemeral=True
            )

    async def _second_select_callback(self, interaction: discord.Interaction) -> None:
        """Callback da seleção da Second Weapon com validação"""
        try:
            await interaction.response.defer()
        except:
            await interaction.followup.send(
                "⏰ **Tempo expirado!** Por favor, clique em PARTICIPAR novamente.",
                ephemeral=True
            )
            return

        selected_second = interaction.data["values"][0]

        # VALIDAÇÃO CRÍTICA: Second Weapon não pode ser igual à Main Weapon
        if selected_second == self.main_weapon:
            main_emoji = WEAPON_EMOJIS.get(self.main_weapon, "⚔️")
            await interaction.followup.send(
                f"❌ **Erro de seleção:**\n"
                f"A Second Weapon **não pode ser igual** à Main Weapon!\n\n"
                f"{main_emoji} **Sua Main Weapon:** {self.main_weapon}\n"
                f"⚠️ **Tentou selecionar:** {selected_second}\n\n"
                "Por favor, selecione uma **arma diferente** como Second Weapon.",
                ephemeral=True
            )
            return

        self.second_weapon = selected_second
        self.state = "REVIEWING"
        self._setup_initial_view()

        visual_class = WEAPON_CLASS_MAPPING.get(self.main_weapon, "DESCONHECIDO")
        main_emoji = WEAPON_EMOJIS.get(self.main_weapon, "⚔️")
        second_emoji = WEAPON_EMOJIS.get(self.second_weapon, "🛡️")

        try:
            await interaction.edit_original_response(
                content=f"**✅ Armas selecionadas:**\n"
                       f"{main_emoji} **Main:** {self.main_weapon}\n"
                       f"{second_emoji} **Second:** {self.second_weapon}\n\n"
                       f"*Você aparecerá como **{visual_class}** na lista*\n\n"
                       f"**Clique em 'Confirmar ✅' para entrar ou 'Editar 🔄' para ajustar.**",
                view=self
            )
        except:
            await interaction.followup.send(
                f"**✅ Armas selecionadas:**\n"
                f"{main_emoji} **Main:** {self.main_weapon}\n"
                f"{second_emoji} **Second:** {self.second_weapon}\n\n"
                f"*Você aparecerá como **{visual_class}** na lista*\n\n"
                f"**Clique em 'Confirmar ✅' para entrar ou 'Editar 🔄' para ajustar.**",
                view=self,
                ephemeral=True
            )

    async def _edit_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão Editar"""
        try:
            await interaction.response.defer()
        except:
            await interaction.followup.send(
                "⏰ **Tempo expirado!** Por favor, clique em PARTICIPAR novamente.",
                ephemeral=True
            )
            return

        # Reset para seleção da Main Weapon, mantendo a Main atual como referência
        old_main = self.main_weapon  # Guardar para referência na mensagem
        self.state = "SELECTING_MAIN"
        # MANTER self.main_weapon para mostrar no placeholder
        self.second_weapon = None
        self._setup_initial_view()

        main_emoji = WEAPON_EMOJIS.get(old_main, "⚔️")

        try:
            await interaction.edit_original_response(
                content=f"**✏️ Modo Edição**\n\n"
                       f"{main_emoji} **Main Weapon anterior:** {old_main}\n\n"
                       f"**Selecione uma nova Main Weapon ou a mesma se quiser manter:**",
                view=self
            )
        except:
            await interaction.followup.send(
                f"**✏️ Modo Edição**\n\n"
                f"{main_emoji} **Main Weapon anterior:** {old_main}\n\n"
                f"**Selecione uma nova Main Weapon ou a mesma se quiser manter:**",
                view=self,
                ephemeral=True
            )

    async def _back_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão Voltar"""
        try:
            await interaction.response.defer()
        except:
            await interaction.followup.send(
                "⏰ **Tempo expirado!** Por favor, clique em PARTICIPAR novamente.",
                ephemeral=True
            )
            return

        self.state = "SELECTING_MAIN"
        self.second_weapon = None
        self._setup_initial_view()

        try:
            await interaction.edit_original_response(
                content="**Voltando à seleção inicial...**\n\n"
                       "**Selecione sua Main Weapon:**\n"
                       "*(Sua posição na lista será determinada pela Main Weapon)*",
                view=self
            )
        except:
            await interaction.followup.send(
                "**Voltando à seleção inicial...**\n\n"
                "**Selecione sua Main Weapon:**\n"
                "*(Sua posição na lista será determinada pela Main Weapon)*",
                view=self,
                ephemeral=True
            )

    async def _confirm_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão Confirmar - CORRIGIDO para lidar com interações expiradas"""
        
        # Primeiro, verificar se podemos responder à interação
        try:
            # Responder imediatamente para não expirar
            await interaction.response.defer(ephemeral=True)
            print(f"✅ Interação deferida para usuário {interaction.user.id}")
        except Exception as e:
            print(f"❌ Erro ao deferir interação: {e}")
            # Se não conseguir nem deferir, a interação já expirou completamente
            try:
                await interaction.followup.send(
                    "⏰ **Tempo expirado!** Sua sessão de seleção expirou.\n"
                    "Por favor, clique em PARTICIPAR novamente.",
                    ephemeral=True
                )
            except:
                pass
            return

        # Validação básica
        if not self.main_weapon or not self.second_weapon:
            await interaction.followup.send(
                "Por favor, selecione ambas as armas!",
                ephemeral=True
            )
            return

        # Validação final: Second não pode ser igual à Main
        if self.second_weapon == self.main_weapon:
            await interaction.followup.send(
                f"❌ Erro: Second Weapon não pode ser igual à Main Weapon ({self.main_weapon})!",
                ephemeral=True
            )
            return

        # Determinar classe baseada na Main Weapon
        user_class = WEAPON_CLASS_MAPPING.get(self.main_weapon)

        if not user_class:
            await interaction.followup.send(
                "❌ Erro ao determinar classe da arma selecionada!",
                ephemeral=True
            )
            return

        # Verificar se já está participando
        if self.gvg_embed.is_user_participating(interaction.user.id):
            await interaction.followup.send(
                "Você já está participando! Use o botão SAIR para remover.",
                ephemeral=True
            )
            return

        # Verificar se a lista está finalizada
        if self.gvg_embed.finalizada:
            await interaction.followup.send(
                "A lista já foi finalizada!",
                ephemeral=True
            )
            return

        # Verificar cargos de classe
        user_role_ids = [role.id for role in interaction.user.roles]
        has_any_class_role = any(
            role_id in CLASS_ROLES.values()
            for role_id in user_role_ids
        )

        if not has_any_class_role:
            await interaction.followup.send(
                f"❌ Você precisa ter um cargo de Classe para participar, consiga o seu em <#{OTHER_ROLES['CANAL_CARGOS']}>",
                ephemeral=True
            )
            return

        # Adicionar participante
        print(f"📝 Adicionando participante {interaction.user.id} como {user_class}")
        success = self.gvg_embed.add_participant(
            user_id=interaction.user.id,
            main_weapon=self.main_weapon,
            second_weapon=self.second_weapon,
            user_class=user_class
        )

        if success:
            try:
                # Adicionar auto role
                auto_role_id = AUTO_ROLES.get(user_class)
                if auto_role_id:
                    guild = interaction.guild
                    auto_role = guild.get_role(auto_role_id)
                    if auto_role:
                        await interaction.user.add_roles(auto_role)
                        print(f"✅ Auto role adicionada para {interaction.user.id}")
            except Exception as e:
                print(f"❌ Erro ao adicionar auto role: {e}")

            # Atualizar embed principal
            embed = self.gvg_embed.create_embed()
            self.main_view.update_view()

            class_emoji = CLASS_EMOJIS.get(user_class, "🎮")

            # Enviar confirmação via followup (sempre funciona)
            await interaction.followup.send(
                f"{class_emoji} **Entrada confirmada como {user_class}!**",
                ephemeral=True
            )

            # Tentar editar a mensagem original da view de seleção (pode falhar se expirou)
            try:
                await interaction.edit_original_response(
                    content=f"{class_emoji} **Entrada confirmada como {user_class}!**",
                    view=None,
                    embed=None
                )
                print(f"✅ Mensagem da view editada para {interaction.user.id}")
            except Exception as e:
                print(f"⚠️ Não foi possível editar mensagem da view (pode ter expirado): {e}")

            # AGORA editar a mensagem principal do GvG Check (sempre deve funcionar)
            try:
                await self.main_view.message.edit(embed=embed, view=self.main_view)
                print(f"✅ Mensagem principal atualizada para {interaction.user.id}")
            except Exception as e:
                print(f"❌ Erro CRÍTICO ao editar mensagem principal: {e}")
                # Se falhar, tentar notificar
                await interaction.followup.send(
                    "❌ **Erro:** Você foi adicionado à lista, mas houve um erro ao atualizar a mensagem principal.\n"
                    "Por favor, avise um moderador.",
                    ephemeral=True
                )
        else:
            print(f"❌ Falha ao adicionar participante {interaction.user.id}")
            await interaction.followup.send(
                "❌ Ocorreu um erro ao adicionar você à lista!",
                ephemeral=True
            )

    async def _cancel_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão Cancelar"""
        try:
            await interaction.response.edit_message(
                content="❌ **Seleção cancelada.**",
                view=None,
                embed=None
            )
        except:
            try:
                await interaction.followup.send(
                    "❌ **Seleção cancelada.**",
                    ephemeral=True
                )
            except:
                pass

class GvGCheckEmbed:
    """Classe para gerenciar o embed e participantes do GvG Check"""

    def __init__(self):
        self.participants = {
            "TANK": [],
            "HEALER": [],
            "DPS": []
        }
        self.finalizada = False

    def create_embed(self) -> discord.Embed:
        """Cria embed com 3 colunas verticais: TANK | HEALER | DPS"""
        embed_color = COR_BORDA_FINALIZADA if self.finalizada else COR_BORDA_ATIVA

        embed = discord.Embed(
            title="**WANTED GvG CHECK**",
            description="Entre na lista em caso de disponibilidade para participar da GvG.",
            color=embed_color
        )

        if self.finalizada:
            embed.title = "**[FINALIZADO]** WANTED GvG CHECK"

        # Adicionar cada classe como uma coluna
        tanks = self._format_participants_list("TANK")
        embed.add_field(
            name=f"{CLASS_EMOJIS['TANK']} **TANK**",
            value=tanks[0],
            inline=True
        )
        for page in tanks[1:]:
            embed.add_field(
                name="",
                value=page,
                inline=True
            )

        healers = self._format_participants_list("HEALER")
        embed.add_field(
            name=f"{CLASS_EMOJIS['HEALER']} **HEALER**",
            value= healers[0],
            inline=True
        )
        for page in healers[1:]:
            embed.add_field(
                name="",
                value=page,
                inline=True
            )

        dps = self._format_participants_list("DPS")
        embed.add_field(
            name=f"{CLASS_EMOJIS['DPS']} **DPS**",
            value=dps[0],
            inline=True
        )
        for page in dps[1:]:
            embed.add_field(
                name="",
                value=page,
                inline=True
            )

        # Contadores
        tank_count = len(self.participants["TANK"])
        healer_count = len(self.participants["HEALER"])
        dps_count = len(self.participants["DPS"])
        total_count = tank_count + healer_count + dps_count

        embed.add_field(
            name="**CONTAGEM:**",
            value=f"**TANK:** {tank_count}\n**HEALER:** {healer_count}\n**DPS:** {dps_count}\n**TOTAL:** {total_count}",
            inline=False
        )

        # Rodapé
        if self.finalizada:
            embed.set_footer(text="✅ LISTA FINALIZADA | Guilda Wanted © | Community Server")
        else:
            embed.set_footer(text="Guilda Wanted © | Community Server")

        return embed

    def _format_participants_list(self, class_name: str) -> List[str]:
        """Formata a lista de participantes de uma classe com emojis das armas"""
        formatted = []
        for participant in self.participants[class_name]:
            main_emoji = WEAPON_EMOJIS.get(participant["main_weapon"], "⚔️")
            second_emoji = WEAPON_EMOJIS.get(participant["second_weapon"], "🛡️")
            formatted.append(f"{main_emoji}{second_emoji} <@{participant['user_id']}>")

        if not formatted:
            return ["-\n"]

        pages = [""]
        for entry in formatted:
            if len(pages[-1]) + len(entry) + 1 >= 1024:
                pages.append(entry + '\n')
                continue
            pages[-1] = pages[-1] + entry + '\n'
        return pages

    def is_user_participating(self, user_id: int) -> bool:
        """Verifica se um usuário já está participando"""
        for participants_list in self.participants.values():
            for participant in participants_list:
                if participant["user_id"] == user_id:
                    return True
        return False

    def get_user_class(self, user_id: int) -> Optional[str]:
        """Retorna a classe de um usuário participante"""
        for class_name, participants_list in self.participants.items():
            for participant in participants_list:
                if participant["user_id"] == user_id:
                    return class_name
        return None

    def finalizar_lista(self) -> None:
        """Finaliza a lista (congela os participantes)"""
        self.finalizada = True

    def add_participant(self, user_id: int, main_weapon: str, second_weapon: str, user_class: str) -> bool:
        """Adiciona participante com informações das armas"""
        if self.finalizada:
            print(f"❌ Lista finalizada, não pode adicionar {user_id}")
            return False

        if self.is_user_participating(user_id):
            print(f"❌ Usuário {user_id} já está participando")
            return False

        # Adicionar participante com armas
        self.participants[user_class].append({
            "user_id": user_id,
            "main_weapon": main_weapon,
            "second_weapon": second_weapon
        })
        print(f"✅ Usuário {user_id} adicionado como {user_class}")
        return True

    def remove_participant(self, user_id: int) -> tuple[bool, str]:
        """Remove participante de qualquer role"""
        if self.finalizada:
            return False, "A lista já foi finalizada!"

        for class_name in self.participants:
            for i, participant in enumerate(self.participants[class_name]):
                if participant["user_id"] == user_id:
                    # Remover participante da lista
                    self.participants[class_name].pop(i)
                    print(f"✅ Usuário {user_id} removido da lista")
                    return True, "Você saiu do GvG Check!"

        return False, "Você não estava participando."

class GvGCheckView(View):
    """View principal do GvG Check"""

    def __init__(self, gvg_embed: GvGCheckEmbed):
        super().__init__(timeout=None)  # View permanente
        self.gvg_embed = gvg_embed
        self.message: Optional[discord.Message] = None
        self.update_view()

    def update_view(self) -> None:
        """Atualiza a view baseado no estado da lista"""
        self.clear_items()

        if self.gvg_embed.finalizada:
            # Se finalizada, mostrar apenas botão DELETAR
            delete_button = Button(
                label="DELETAR 🗑️",
                style=discord.ButtonStyle.danger,
            )
            delete_button.callback = self._delete_callback
            self.add_item(delete_button)
        else:
            # Se não finalizada, mostrar os 3 botões normais
            participate_button = Button(
                label="PARTICIPAR 🎉",
                style=discord.ButtonStyle.success,
            )
            participate_button.callback = self._participate_callback
            self.add_item(participate_button)

            leave_button = Button(
                label="SAIR 💨",
                style=discord.ButtonStyle.danger,
            )
            leave_button.callback = self._leave_callback
            self.add_item(leave_button)

            finalize_button = Button(
                label="FINALIZAR 📋",
                style=discord.ButtonStyle.primary,
            )
            finalize_button.callback = self._finalize_callback
            self.add_item(finalize_button)

    async def _participate_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão PARTICIPAR - Abre a View de seleção"""
        # Verificar se já está participando
        if self.gvg_embed.is_user_participating(interaction.user.id):
            await interaction.response.send_message(
                "Você já está participando! Use o botão SAIR para remover.",
                ephemeral=True
            )
            return

        # Verificar se a lista está finalizada
        if self.gvg_embed.finalizada:
            await interaction.response.send_message(
                "A lista já foi finalizada!",
                ephemeral=True
            )
            return

        # Verificar cargos de classe
        user_role_ids = [role.id for role in interaction.user.roles]
        has_any_class_role = any(
            role_id in CLASS_ROLES.values()
            for role_id in user_role_ids
        )

        if not has_any_class_role:
            await interaction.response.send_message(
                f"❌ Você precisa ter um cargo de Classe para participar, consiga o seu em <#{OTHER_ROLES['CANAL_CARGOS']}>",
                ephemeral=True
            )
            return

        # Criar e enviar View de seleção de armas
        weapon_view = WeaponSelectView(self.gvg_embed, self, interaction.user.id)

        # Enviar mensagem e guardar referência
        await interaction.response.send_message(
            "**🎮 SELEÇÃO DE ARMAS - GvG CHECK**\n\n"
            "**1. Primeiro escolha sua MAIN WEAPON:**\n"
            "*(Sua posição na lista será determinada pela Main Weapon)*\n\n"
            "⚠️ **Você tem 5 minutos para completar a seleção!**",
            view=weapon_view,
            ephemeral=True
        )

        # Guardar referência à mensagem na view
        weapon_view.message = await interaction.original_response()
        print(f"✅ View de seleção criada para {interaction.user.id}")

    async def _leave_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão SAIR"""
        # Verificar se o usuário está participando
        if not self.gvg_embed.is_user_participating(interaction.user.id):
            await interaction.response.send_message(
                "Você não está participando!",
                ephemeral=True
            )
            return

        # Remover participante
        success, message = self.gvg_embed.remove_participant(interaction.user.id)

        if success:
            # Atualizar embed e view
            embed = self.gvg_embed.create_embed()
            self.update_view()
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send("✅ Você saiu do GvG Check!", ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    async def _finalize_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão FINALIZAR"""
        # Verificar permissão
        user_roles = [role.id for role in interaction.user.roles]
        user_has_permission = (
            any(role_id in PERMISSION_ROLES.values() for role_id in user_roles) or
            interaction.user.guild_permissions.administrator
        )

        if not user_has_permission:
            await interaction.response.send_message(
                "❌ Você não tem permissão para finalizar o GvG Check!",
                ephemeral=True
            )
            return

        # Finalizar a lista
        self.gvg_embed.finalizar_lista()

        # Atualizar embed e view
        embed = self.gvg_embed.create_embed()
        self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)

        await interaction.followup.send(
            "✅ Lista finalizada!",
            ephemeral=True
        )

    async def _delete_callback(self, interaction: discord.Interaction) -> None:
        """Callback do botão DELETAR"""
        # Verificar permissão
        user_roles = [role.id for role in interaction.user.roles]
        user_has_permission = (
            any(role_id in PERMISSION_ROLES.values() for role_id in user_roles) or
            interaction.user.guild_permissions.administrator
        )

        if not user_has_permission:
            await interaction.response.send_message(
                "❌ Você não tem permissão para deletar o GvG Check!",
                ephemeral=True
            )
            return

        try:
            # Remover cargos de build de todos os membros
            guild = interaction.guild
            roles_to_remove = []

            # Obter os 3 cargos de build
            for class_name in ["TANK", "HEALER", "DPS"]:
                role_id = AUTO_ROLES.get(class_name)
                if role_id:
                    role = guild.get_role(role_id)
                    if role:
                        roles_to_remove.append(role)

            if roles_to_remove:
                # Remover de todos os membros que têm esses cargos
                for role in roles_to_remove:
                    for member in role.members:
                        try:
                            await member.remove_roles(role)
                        except Exception as e:
                            print(f"Erro ao remover cargo {role.name} de {member.name}: {e}")

        except Exception as e:
            print(f"Erro ao remover cargos de build: {e}")

        # Apagar a mensagem do GvG Check
        await interaction.message.delete()
        await interaction.response.send_message(
            "🗑️ GvG Check deletado! Cargos de build removidos.",
            ephemeral=True
        )

class GvGCheck(commands.Cog):
    """Cog principal do GvG Check"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gvgcheck", description="Cria um check de disponibilidade para GvG")
    async def gvgcheck(self, interaction: discord.Interaction):
        """Cria um GvG Check para contabilizar players disponíveis"""
        # Verificar permissão
        user_roles = [role.id for role in interaction.user.roles]
        user_has_permission = (
            any(role_id in PERMISSION_ROLES.values() for role_id in user_roles) or
            interaction.user.guild_permissions.administrator
        )

        if not user_has_permission:
            await interaction.response.send_message(
                "❌ Você não tem permissão para usar este comando!",
                ephemeral=True
            )
            return

        # Criar embed do GvG Check
        gvg_embed = GvGCheckEmbed()

        # Criar embed inicial
        embed = gvg_embed.create_embed()
        view = GvGCheckView(gvg_embed)

        # Enviar mensagem e guardar referência
        await interaction.response.send_message(embed=embed, view=view)

        # Guardar referência à mensagem na view
        view.message = await interaction.original_response()
        print(f"✅ GvG Check criado por {interaction.user.id}")

async def setup(bot):
    """Setup do cog"""
    await bot.add_cog(GvGCheck(bot))