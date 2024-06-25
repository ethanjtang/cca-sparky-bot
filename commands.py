#  -----------------------------------
#      SparkyBot V1 by Ethan Tang
#      Updated on August 8th, 2023
#  -----------------------------------

# test test 123

""" This bot is meant to act as a useful tool for a chess-related discord with various 
    commands which call the Lichess or chess.com API for stats, to create games, etc.
    Currently, games can only be created on Lichess because of Chess.com's API limitations.
    (Correct me if I'm wrong though since this is my first big project)
"""

# Importing useful libraries.

import discord
import keyid # Stores API tokens.
import berserk # Used for Lichess API calls.

from chessdotcom import get_player_stats # Used for the command "!stats".
from discord.ext import commands

# ***Future Changes In Progress***
# 1) Implement all TODO comments.
# 2) Add a method using Google Sheets API to store Discord, chess.com, and Lichess usernames for simpler !challenge or !create_game calls for end users.
# 3) Add more detailed comments.

# Creating a bot.
def create_bot(intents):
    bot = commands.Bot(command_prefix='!', intents=intents)

    # Acts as a temporary !help command for the time being since this bot is very simple at the moment.
    # TODO Implement custom !help command with menus.

    @bot.command()
    async def info(ctx):
        try:
            # Displays info about the different command functionalities.
            embed = discord.Embed(title="List of Valid Commands", description="", color=discord.Color.blue())
            embed.add_field(name="!info", value="Displays this help message.", inline=False)
            embed.add_field(name="!events", value="Directs you to our club website which contains our tournament and club meeting schedule.", inline=False)
            embed.add_field(name="!stats (platform) (username)", value="Displays the stats of a specific user on chess.com or lichess.org.", inline=False)
            embed.add_field(name="!challenge", value="Creates an unrated, open challenge anyone can join on lichess.org.", inline=False)
            embed.add_field(name="!create_game (time) (increment) (variant) (rated or unrated)", value="Creates a custom open game on Lichess. Valid variants include: standard and chess960.", inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await handle_error(ctx, e)

    # Links to Chess Club at ASU's website, where we post the club and tournament schedule for each academic year.
    # TODO Call Wix API directly instead of linking page.
    # TODO Add a feature to link directly to a ticket for the latest event.

    @bot.command()
    async def events(ctx):
        try:
            await ctx.send("Here's a link to our club website which contains our tournament and club meeting schedule: \n"
                       + keyid.CLUB_URL)
            return
        except Exception as e:
            await handle_error(ctx, e)

    # Creates an open, unrated challenge of the most-played time formats on Lichess.org, see code below.

    @bot.command()
    async def challenge(ctx):
        try:
            await ctx.send("Select a time format for the unrated game challenge:", view=SelectView())
        except Exception as e:
            await handle_error(ctx, e)

    # Creating a menu for the !challenge command using the Select class.
    
    class Select(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="1+0 bullet", emoji="🚀", description="1 minute bullet with no increment"),
                discord.SelectOption(label="1+1 bullet", emoji="🚀", description="1 minute + 1 second increment"),
                discord.SelectOption(label="2+1 bullet", emoji="🚀", description="2 minutes + 1 second increment"),
                discord.SelectOption(label="3+0 blitz", emoji="⚡", description="3 minutes blitz with no increment"),
                discord.SelectOption(label="3+2 blitz", emoji="⚡", description="3 minutes + 2 seconds increment"),
                discord.SelectOption(label="5+0 blitz", emoji="⚡", description="5 minutes blitz with no increment"),
                discord.SelectOption(label="5+3 blitz", emoji="⚡", description="5 minutes + 3 seconds increment"),
                discord.SelectOption(label="10+0 rapid", emoji="🕒", description="10 minutes increment"),
                discord.SelectOption(label="15+10 rapid", emoji="🕒", description="15 minutes + 10 seconds increment"),
                discord.SelectOption(label="30+0 classical", emoji="⏳", description="30 minutes classical with no increment"),
            ]
            super().__init__(placeholder="Select a time format", max_values=1, min_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            time_format = self.values[0]
            await create_unrated_game(interaction, time_format)

    class SelectView(discord.ui.View):
        def __init__(self, *, timeout=180):
            super().__init__(timeout=timeout)
            self.add_item(Select())

    # Helper command for creating an unrated, open game used by the !challenge command.
    
    async def create_unrated_game(interaction, time_format):
        time_formats = {
            "1+0 bullet": ("1", "0"),
            "1+1 bullet": ("1", "1"),
            "2+1 bullet": ("2", "1"),
            "3+0 blitz": ("3", "0"),
            "3+2 blitz": ("3", "2"),
            "5+0 blitz": ("5", "0"),
            "5+3 blitz": ("5", "3"),
            "10+0 rapid": ("10", "0"),
            "15+10 rapid": ("15", "10"),
            "30+0 classical": ("30", "0"),
        }

        if time_format not in time_formats:
            await interaction.followup.send("Invalid time format selected. Please try again.", ephemeral=False)
            return

        time, increment = time_formats[time_format]

        session = berserk.TokenSession(keyid.LICHESS_TOKEN)
        client = berserk.Client(session=session)

        game_time = int(time) * 60
        increment = int(increment)

        variant = "standard"  
        challenge_url = client.challenges.create_open(game_time, increment, variant, None, False, "Chess Club @ ASU Challenge")

        url_string = f"\nPlay as white: {challenge_url['urlWhite']} \nPlay as black: {challenge_url['urlBlack']}"

        await interaction.followup.send(f"Unrated {time_format} game challenge created! {url_string}", ephemeral=False)

    # Custom command for creating a game on Lichess.
    # TODO Create step-by-step menu for creating a game.
        
    @bot.command()
    async def create_game(ctx, time, inc, var, rat):
        try:
            session = berserk.TokenSession(keyid.LICHESS_TOKEN)
            client = berserk.Client(session=session)
            
            game_time = int(time)*60
            increment = int(inc)

            valid_variants = {
                'standard', 'atomic', 'chess960', 'antichess', 'horde', 'koth', 'racingkings', '3check'
            }
            if var not in valid_variants:
                raise ValueError("Invalid variant, please enter a valid variant (standard, chess960, etc.)")

            if rat == 'rated' and var != 'standard':
                raise ValueError("Cannot create a rated game of a non-standard variant")
            elif rat not in {'rated', 'unrated'}:
                raise ValueError("Please enter 'rated' or 'unrated' for your game type")

            rated = rat == 'rated'

            challenge_url = client.challenges.create_open(game_time, increment, var, None, rated, "Chess Club @ ASU Challenge")
            url_string = f"\n{challenge_url['challenge']['url']}"

            await ctx.send(f"\nChallenge created! \nLink: {url_string}")
        except (ValueError, berserk.BerserkException) as e:
            await ctx.send(f"An error occurred: {e}")
    
    # Displays stats of a chess.com or Lichess.org profile.

    @bot.command()
    async def stats(ctx, platform, username):
        try:
            if platform not in {'chess.com', 'lichess.org'}:
                raise ValueError("Please enter a valid platform ('chess.com', 'lichess.org')")

            if platform == 'chess.com':
                data = get_player_stats(username).json

                categories = {
                    "chess_blitz": "Blitz",
                    "chess_bullet": "Bullet",
                    "chess_rapid": "Rapid",
                    "chess_daily": "Daily",
                    "puzzle_rush": "Puzzle Rush Survival",
                    "tactics": "Puzzles",
                }

                embed = discord.Embed(title=f"Stats for {username}")

                file = discord.File("chessdotcom_logo.png", filename="chessdotcom_logo.png")
                embed.set_thumbnail(url="attachment://chessdotcom_logo.png")

                for category, label in categories.items():
                    if category in data["stats"]:
                        if category in ["chess_blitz", "chess_bullet", "chess_rapid", "chess_daily"]:
                            current_rating = data["stats"][category]["last"]["rating"]
                            best_rating = data["stats"][category]["best"]["rating"]
                            record = data["stats"][category]["record"]
                            total_games = record["draw"] + record["loss"] + record["win"]
                            
                            win_percentage = round(record["win"] / total_games * 100, 2)
                            draw_percentage = round(record["draw"] / total_games * 100, 2)
                            loss_percentage = round(record["loss"] / total_games * 100, 2)

                            wdl_string = f"W/D/L: {win_percentage}% / {draw_percentage}% / {loss_percentage}%"
                            embed.add_field(name=f"{label}", value=f"{wdl_string}\nCurrent: {current_rating}\nPeak: {best_rating}\nGames: {total_games}", inline=False)

                            embed.color = discord.Color.green()

                        elif category == "puzzle_rush":
                            best_score = data["stats"][category]["best"]["score"]
                            total_attempts = data["stats"][category]["best"]["total_attempts"]
                            embed.add_field(name=f"{label}", value=f"Best Score: {best_score}\nTotal Attempts: {total_attempts}", inline=False)
                        elif category == "tactics":
                            highest_rating = data["stats"][category]["highest"]["rating"]
                            embed.add_field(name=f"{label}", value=f"Highest Rating: {highest_rating}", inline=False)
                    else:
                        embed.add_field(name=f"{label}", value="No data available", inline=False)

                await ctx.send(file=file, embed=embed)
            else:
                session = berserk.TokenSession(keyid.LICHESS_TOKEN)
                client = berserk.Client(session=session)

                data = client.users.get_public_data(username)

                categories = {
                    "blitz": "Blitz",
                    "bullet": "Bullet",
                    "ultraBullet": "Ultrabullet",
                    "rapid": "Rapid",
                    "classical": "Classical",
                    "correspondence": "Correspondence",
                    "puzzle": "Puzzles",
                    "storm": "Puzzle Storm",
                }
                embed = discord.Embed(title=f"Stats for {username}")
                embed.color = discord.Color.lighter_grey()

                file = discord.File("lichess_logo.png", filename="lichess_logo.png")
                embed.set_thumbnail(url="attachment://lichess_logo.png")

                time_playing = data["playTime"]["total"] / 3600
                time_on_tv = data["playTime"]["tv"] / 3600
                total_playtime_hours = round(time_playing, 2)
                time_on_tv_hours = round(time_on_tv, 2)
                total_games = data["count"]["all"]
                total_wins = data["count"]["win"]
                total_losses = data["count"]["loss"]
                total_draws = data["count"]["draw"]
                total_games_played = total_wins + total_losses + total_draws
                win_percentage = round(total_wins / total_games_played * 100, 2)
                loss_percentage = round(total_losses / total_games_played * 100, 2)
                draw_percentage = round(total_draws / total_games_played * 100, 2)

                wdl_string = f"W/D/L: {win_percentage}% / {draw_percentage}% / {loss_percentage}%"

                embed.add_field(name="General", value=f"Total Playtime: {total_playtime_hours} hours\nTime on TV: {time_on_tv_hours} hours\nTotal # of Games: {total_games}\n{wdl_string}", inline=False)
                for category, label in categories.items():
                    if "perfs" in data and category in data["perfs"] and category != "puzzle" and category != "storm":
                        rating = data["perfs"][category]["rating"]
                        games = data["perfs"][category]["games"]

                        embed.add_field(name=f"{label}", value=f"Current Rating: {rating}\nGames Played: {games}", inline=False)
                    elif "perfs" in data and category in data["perfs"] and category == "puzzle":
                        rating = data["perfs"][category]["rating"]
                        games = data["perfs"][category]["games"]

                        embed.add_field(name=f"{label}", value=f"Current Rating: {rating}\nPuzzles Completed: {games}", inline=False)
                    elif "perfs" in data and category in data["perfs"] and category == "storm":
                        score = data["perfs"][category]["score"]
                        games = data["perfs"][category]["runs"]

                        embed.add_field(name=f"{label}", value=f"Highest Score: {score}\nRuns Completed: {games}", inline=False)
                    else:
                        embed.add_field(name=f"{label}", value="No data available", inline=False)

                await ctx.send(file=file, embed=embed)

        except (ValueError, berserk.BerserkException) as e:
            await ctx.send(f"An error occurred: {e}")

    # Defining a generic error handling function.

    async def handle_error(ctx, error):
        error_message = "An error occurred: " + str(error)
        await ctx.send(error_message)
    
    return bot
