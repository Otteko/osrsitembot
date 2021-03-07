import praw;
import requests;
from bs4 import BeautifulSoup
import time
from datetime import datetime
from bottr.bot import CommentBot

class main:
    def construct_Response(items):
        BASE_TABLE = ("Hello, I've found " + str(len(items)) + " item(s) in your post, "
        "let me look up some information about them..\n\n"
                        "| Item             | Examine text          | Members | HA | LA | GE Price | Limit |\n"
                        "|------------------|-----------------------|:-------:|:----:|:----:|:-------:|:-------:|\n")
        strItems = main.lookup_Items(items)
        BASE_POST_TABLE = ("\n\nI am a bot, use (playername) or [itemname] in any comment on /r/2007scape to trigger me, "
                            "some nicknamed items like [tbow] or [76] work! | "
                            "[Message my owner](https://www.reddit.com/message/compose?to=swordstoo&subject=osrsitemsbot) | "
                            "Made with [PRAW](https://github.com/praw-dev/praw) | "
                            "Use !goodbot to give me the good chemicals | "
                            "Criticize me on [Github](https://github.com/Otteko/osrsitembot)!")
        return BASE_TABLE + strItems + BASE_POST_TABLE
        
    def lookup_Items(items):
        strItems = ""
        for item in items:
            URL = 'https://oldschool.runescape.wiki/w/' + item.replace(' ', "_")
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            strItems = strItems + ("|" + item + "|" +
                          str(soup.get_text()).split("Examine")[1].split(".")[0] + "|" +
                          str(soup.get_text()).split("Members")[1].split("Quest")[0] + "|" +
                          str(soup.get_text()).split("High alch")[1].split(" ")[0] + "gp" + "|" +
                          str(soup.get_text()).split("Low alch")[1].split(" ")[0] + "gp" + "|" +
                          str(soup.get_text()).split("ExchangeExchange")[1].split(" ")[0] + "gp" + "|" +
                          str(soup.get_text()).split("Buy limit")[1].split("Daily")[0] + "|\n")
        return strItems
    
    def findItemsInComment(commentString):
        foundItemsInComment = []
        while '[' in commentString and ']' in commentString:
            #\\ incase they're using new editor
            foundItemsInComment.append(commentString.split('[')[1].split(']')[0].split('\\')[0])
            #remove everything up to the found set of '[' and ']'
            commentString = commentString.split(']', 1)[1]
        return main.verifyItemsInComment(foundItemsInComment)
         
    def verifyItemsInComment(unverifiedItemsList):
        verifiedItemsList = []
        for item in unverifiedItemsList:
            URL = 'https://oldschool.runescape.wiki/w/' + item.replace(" ", "_")
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            if "This page doesn't exist on the wiki" in soup.get_text() or URL == "https://oldschool.runescape.wiki/w/" or "Quest item" not in soup.get_text():
                """Do nothing"""
            else:
                verifiedItemsList.append(item)
        return verifiedItemsList
    def curr_Time():
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")
    
    def write_To_Disk(comment, response):
        file1 = open("responses.txt", "a")  # append mode 
        file1.write("I responded to " + comment.author.name)
        file1.write("\nOn " + main.curr_Time())
        file1.write("\nLink to comment: https://www.reddit.com" + comment.permalink)
        file1.write("\nI said: ")
        file1.write(response)
        file1.write("\n----------------------------\n")
        file1.close() 
    
    def parse_items(commentBody):
        foundItems = main.findItemsInComment(commentBody)
        if len(foundItems) > 0:
            response = main.construct_Response(foundItems)
            return response

    def lookup_player(playerName):
        if len(playerName) < 3:
            return ""
        BASE_HISCORE_URL = "https://secure.runescape.com/m=hiscore_oldschool/hiscorepersonal?user1="
        HISCORE_URL = BASE_HISCORE_URL + playerName.replace(" ", "%A0")
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        page = requests.get(HISCORE_URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser').get_text()
        if 'No player "' in soup:
            return ""
        else:
            return soup.split("SkillRankLevelXP\n\n\n\n\n\n")[1]

    def construct_Response_Highscore(highscoreText, playerName):
        SKILL_BASE_TABLE = ("Hello, I've found leaderboard stats for player " + playerName + ", here they are:\n\n"
                "| Skillname     | Rank      | lv  |      xp      |\n"
                "|---------------|:-----------:|:---:|:-----------:|\n")
        skillsTable = main.lookup_player_skills(highscoreText)

        MINIGAME_BASE_TABLE = ("\n| Minigame     | Rank      | Score  |\n"
                "|---------------|:-----------:|:-----------:|\n")
        minigameTable = main.lookup_player_minigames(highscoreText)

        BASE_POST_TABLE = ("\n\nI am a bot, use (playername) or [itemname] in any comment on /r/2007scape to trigger me, "
                            "some nicknamed items like [tbow] or [76] work! | "
                            "[Message my owner](https://www.reddit.com/message/compose?to=swordstoo&subject=osrsitemsbot) | "
                            "Made with [PRAW](https://github.com/praw-dev/praw) | "
                            "Say 'Good bot' to give me the good chemicals | "
                            "Criticize me on [Github](https://github.com/Otteko/osrsitembot) - open source!")
        return (SKILL_BASE_TABLE + skillsTable + MINIGAME_BASE_TABLE + minigameTable + BASE_POST_TABLE)

    def lookup_player_skills(highscoreText):
        skillsText = highscoreText.split("\nMinigame")[0]
        skillName = []
        rank = []
        level = []
        xp = []
        for i in range(int(len(skillsText.split("\n")) / 9)):
            skillName.append(skillsText.split("\n")[0])
            rank.append(skillsText.split("\n")[2])
            level.append(skillsText.split("\n")[3])
            xp.append(skillsText.split("\n")[4])
            skillsText = skillsText.split("\n", 9)[9]
        skillsString = ""
        for i in range(len(skillName)):
            skillsString = skillsString + "|" + skillName[i] + "|" + rank[i] + "|" + level[i] + "|" + xp[i] + "|\n"
        return skillsString

    def lookup_player_minigames(minigamesText):
        minigamesText = minigamesText.split("Minigame\nRank\nScore\n\n\n")[1].split("\n\n\n\n\n\n\n\n\n\n\n\nSearch")[0]
        minigame = []
        minigameRank = []
        minigameScore = []
        for i in range(int(len(minigamesText.split("\n")) / 6)):
            minigame.append(minigamesText.split("\n")[1])
            minigameRank.append(minigamesText.split("\n")[2])
            minigameScore.append(minigamesText.split("\n")[3])
            minigamesText = minigamesText.split("\n", 6)[6]
        minigamesString = ""
        for i in range(len(minigame)):
            minigamesString = minigamesString + "|" + minigame[i] + "|" + minigameRank[i] + "|" + minigameScore[i] + "|\n"
        return minigamesString

    def parse_players(commentBody):
        toReturn = ""
        if '(' in commentBody and ')' in commentBody:
            playerName = commentBody.split("(")[1].split(")")[0]
            leaderboardText = main.lookup_player(playerName)
            if leaderboardText:
                toReturn = main.construct_Response_Highscore(leaderboardText, playerName)
        return toReturn

    def comment_On_Reddit(originalComment, response):
        print("Attempting to parse comment https://www.reddit.com" + originalComment.permalink)
        print("The comment says: " + originalComment.body)
        if debug:
            main.write_To_Disk(originalComment, response)
            print("I would have responded to " + originalComment.author.name + " on " + main.curr_Time() + " at " + originalComment.permalink)
        else: 
            originalComment.reply(response)
            main.write_To_Disk(originalComment, response)
            print("Responded to " + originalComment.author.name + " on " + main.curr_Time() + " at " + originalComment.permalink)







    def parse_comment(comment):
        print("\n####### New comment found ######## Link: https://www.reddit.com" + comment.permalink + "\n")

        if str(comment.author.name) != "osrsitembot":
            commentBody = comment.body

            foundItems = main.findItemsInComment(commentBody)
            if len(foundItems) > 0:
                main.comment_On_Reddit(comment, main.construct_Response(foundItems))
            
            foundPlayers = main.parse_players(commentBody)
            if foundPlayers:
                main.comment_On_Reddit(comment, main.parse_players(commentBody))

    def yes_or_no(question):
        while True:
            reply = str(input(question+' (y/n): ')).lower().strip()
            if reply[0] == 'y':
                return True
            if reply[0] == 'n':
                return False
#End main class

if __name__ == '__main__':
    # Get reddit instance with login details - Uses praw.ini
    reddit = praw.Reddit("bot1", user_agent="pythonscript:osrsitembot:v1.0.0: (by u/swordstoo)")

    # Create Bot with methods to parse comments
    bot = CommentBot(reddit=reddit,
                    func_comment=main.parse_comment,
                    subreddits=['2007scape'])

    # Start Bot
    if main.yes_or_no("Turn on debug mode? (Print to file only)"):
        debug = True
        print("Starting bot in debug mode...")
        bot.start()
    else:
        debug = False
        print("Starting bot...")
        bot.start()

    # Run bot for 10 minutes
    #time.sleep(10*60)

    # Stop Bot
    #bot.stop()