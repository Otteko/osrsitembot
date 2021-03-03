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
        BASE_POST_TABLE = ("\n\nI am a bot, use [item name] in any comment on /r/2007scape to trigger me, "
                            "nicknamed items like [tbow] do not work yet | "
                            "[Message my owner](https://www.reddit.com/message/compose?to=swordstoo&subject=osrsitemsbot) | "
                            "Made with [PRAW](https://github.com/praw-dev/praw) | "
                            "Use !goodbot to give me the good chemicals | "
                            "[Github](https://github.com/Otteko/osrsitembot)")
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
            if "This page doesn't exist on the wiki" in soup.get_text() or URL == "https://oldschool.runescape.wiki/w/":
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
        file1.write("\nLink to comment: " + comment.permalink)
        file1.write("\nI said: ")
        file1.write(response)
        file1.write("\n----------------------------\n")
        file1.close() 

    def parse_comment(comment):
        if str(comment.author.name) != "osrsitembot":
            commentBody = comment.body
            foundItems = main.findItemsInComment(commentBody)
            if len(foundItems) > 0:
                response = main.construct_Response(foundItems)
                if debug:
                    main.write_To_Disk(comment, response)
                    print("Would have responded to " + comment.author.name + " on " + main.curr_Time() + " with " + str(len(foundItems)) + " items: " + str(foundItems))
                else: 
                    comment.reply(response)
                    print("Responded to " + comment.author.name + " on " + main.curr_Time() + " with " + str(len(foundItems)) + " items: " + str(foundItems))

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