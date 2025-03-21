import discord
from datetime import datetime
from discord.ext import commands
import asyncio
from collections import defaultdict

class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_emojis = ["🛡️", "🍃", "🔥"] 

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignorar reacciones del propio bot
        if user == self.bot.user:
            return

        message = reaction.message
        emoji = str(reaction.emoji)

        # Verificar si es un mensaje de evento
        if not await self.is_event_message(reaction.message):
            return
        
        # Eliminar reacciones no permitidas
        if emoji not in self.allowed_emojis:
            await reaction.remove(user)
            warning = await message.channel.send(
                f"{user.mention} Solo se permiten: {', '.join(self.allowed_emojis)}",
                delete_after=3
            )
            return
        
    async def is_event_message(self, message):
        """Verifica si el mensaje es un evento creado por el bot"""
        # Verificación mejorada del mensaje de evento
        return (
            message.author == self.bot.user and
            message.embeds and
            "Reacciona para participar:" in message.embeds[0].description
        )

    @commands.command(
        name='new_event',
        help='Crea un evento: !new_event DD-MM-AAAA HH:MM "Nombre"'
    )
    async def new_event(self, ctx, *args):
        # Validación
        validation = self.new_event_data_validator(ctx, args)
        if not validation[0]:
            await ctx.send(f"{ctx.author.mention} {validation[1]}")
            return

        date, time, event_name = validation[1], validation[2], validation[3]
        
        # Crear embed
        embed = discord.Embed(
            title=f"📅 {event_name.upper()}",
            color=discord.Color.green(),
            timestamp=datetime.now(),
        )
        
        # Autor y footer
        embed.set_author(
            name=f"Organizado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        embed.set_footer(
            text=f"🗓️ {date} | ⏰ {time}",
            icon_url="https://i.imgur.com/6JqjJ3p.png"  # Icono personalizado
        )
        
        # Mini calendario en descripción
        event_datetime = datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M")
        days_remaining = (event_datetime - datetime.now()).days

        embed.set_image(url=ctx.guild.icon)
        embed.description = (
            f"**Días restantes:** {days_remaining}\n"
            f"**Hora exacta:** <t:{int(event_datetime.timestamp())}:t>\n"
            f"**Fecha completa:** <t:{int(event_datetime.timestamp())}:F>\n"
            f"**Reacciona para participar:**\n🛡️ - Tank \n🍃 - Healer \n🔥 - Shooter "
        )
        embed.set_footer(text=f"Evento estimado para las {time} del dia {date}", icon_url=ctx.author.avatar)
        
        event_message = await ctx.send(embed=embed)

        # Añadir reacciones automáticamente
        reacciones = ["🛡️", "🔥", "🍃"]  
        for emoji in reacciones:
            await event_message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print("asdasdasd")
        if user == self.bot.user:
            return

        message = reaction.message
        emoji = str(reaction.emoji)

        if not await self.is_event_message(message):
            return

        if emoji not in self.allowed_emojis:
            return

        if user.id in self.user_participations[message.id]:
            self.user_participations[message.id].remove(user.id)
            await message.remove_reaction("👤", self.bot.user)

    async def is_event_message(self, message):
        return (
            message.author == self.bot.user and
            message.embeds and
            "Reacciona para participar:" in message.embeds[0].description
        )

    def new_event_data_validator(self, ctx,  args):

        if len(args) < 3:
            return (False, "❌ **Error:** Faltan parámetros. Formato correcto: `!new_event DD-MM-AAAA HH:MM \"Nombre del evento\"`")

        date_str = args[0]
        time_str = args[1]
        event_name = ' '.join(args[2:]).strip()

        # Validar fecha
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            return (False, "❌ **Fecha inválida.** Usa formato `DD-MM-AAAA` (ej. `21-03-2025`)")

        # Validar hora
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
        except ValueError:
            return (False, "❌ **Hora inválida.** Usa formato `HH:MM` en 24h (ej. `13:45`)")

        # Validar nombre del evento
        if not event_name:
            return (False, "❌ **Nombre vacío.** Usa comillas si es necesario (ej. `\"Mi evento\"`)")

        # Verificar fecha futura
        event_datetime = datetime.combine(date_obj.date(), time_obj.time())
        if event_datetime <= datetime.now():
            return (False, "❌ **El evento debe ser futuro.** Verifica fecha y hora.")

        return (True, date_str, time_str, event_name)
    
async def setup(bot):
    await bot.add_cog(EventCog(bot))

# Agrega este handler para errores generales
@commands.Cog.listener()
async def on_command_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Faltan parámetros.** Usa `!help new_event` para ayuda.")