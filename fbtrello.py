#!/usr/bin/python

"""
  This script uses Trello API and Mechanize to get info about a Trello Board
  like cards and lists. After a card is chosen it posts information about it
  to a facebook account.

  the file $HOME/trello-creds.txt contains these needed info:
  
  TRELLO_API_KEY='trello API key'
  TRELLO_SECRET='trello secret'
  TRELLO_TOKEN='trello token'
  FBUSER='facebook username'
  FBPASS='facebook password'

  the file $HOME/.trelloenv keeps info about the card chosen. It is updated 
  everytime a new card is chosen to work on
"""
 
import os

USERNAME = 'oskarkossuth1'
DOINGLIST = '505af35f0c01f26f501b1e69'

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def check_library(name):
    print 'The library %s is not installed \n' % name
    print
    print 'Execute pip install %s and enjoy :)' % name

try:
    from argh import *
except ImportError:
    check_library('argh')
    raise SystemExit(1)

try:
    from mechanize import Browser
except ImportError:
    check_library('mechanize')
    raise SystemExit(1)

try:
    from trello import TrelloApi
except ImportError:
    check_library('trello')
    raise SystemExit(1)

def get_creds(name):
    trellocreds = os.path.expanduser(os.path.join("~", "trello-creds.txt"))
    f = open(trellocreds,"r")
    c = f.readlines()
    f.seek(0)
    app_key = c[0]
    app_token = c[2]
    fb_user = c[3]
    fb_pass = c[4]
    for i in range(len(app_key)):
        if app_key[i] == "=":
	    pos = i
    for j in range(len(app_token)):
        if app_token[j] == "=":
	    pos_tok = j
    for i in range(len(fb_user)):
	if fb_user[i] == "=":
	    pos_tokf = i
    for i in range(len(fb_pass)):
	if fb_pass[i] == "=":
	    pos_tokp = i
    if name == "workon":
        return app_key[pos+2:-2], app_token[pos_tok+2:-2]
    if name == "postfb":
	return fb_user[pos_tokf+2:-2], fb_pass[pos_tokp+2:-2]
        
def listcards():
    TRELLO_API_KEY, TRELLO_TOKEN = get_creds(name="workon")
    trello = TrelloApi(TRELLO_API_KEY)
    trello.set_token(TRELLO_TOKEN)

    b=trello.members.get_card(USERNAME, fields='name,idShort,shortUrl')
    print "My trello cards:"
    for i in b:
        print i['name'] +'- ID:'+ color.BLUE +str(i['idShort']) + color.END

def workon():
    TRELLO_API_KEY, TRELLO_TOKEN = get_creds(name="workon")
    trello = TrelloApi(TRELLO_API_KEY)
    trello.set_token(TRELLO_TOKEN)
    b=trello.lists.get_card(DOINGLIST)
    #b=trello.members.get_card(USERNAME, fields='name,idShort,shortUrl,idBoard,idList')
    print "My trello cards:"
    for i in b:
        print i['name'] +'- ID:'+ color.BLUE +str(i['idShort']) +color.END
    input = raw_input("Choose card to work on: ")
    print "Card chosen is %s \n" % input
    val =''
    for i in b:
        if str(i['idShort']) == input :
	    c=trello.boards.get(i['idBoard'], fields='name,shortUrl')
	    d=trello.lists.get(i['idList'], fields='name')
	    val = i['name'] + '\n' + str(i['idShort']) + '\n' + str(c['shortUrl']) + '\n' + str(d['name'])
    trelloconf = os.path.expanduser(os.path.join("~", ".trelloenv"))
    f = open(trelloconf, "w+")
    f.seek(0)
    f.truncate()
    f.write(val)
    f.close()

@arg('--card',help='Message',)
@arg('--url',help='URL',)
@arg('--status',help='Status',)

def postfb(args):
    fbuser,fbpass = get_creds(name="postfb")
    message =''
    message = "Oskar is doing sysadmin work on the Trello card: \n" \
              + "*** " + args.card + " ***" + "\n" + args.url + "\n" \
	      + "Status: " + args.status + "\n" + "Organization: " + "http://www.ovivo.dk"
    br = Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Firefox/3.0.1')]
    br.open( "https://m.facebook.com/" )
    br.select_form(nr=0)
    br.form['email'] = fbuser
    br.form['pass'] = fbpass
    br.submit()
    br.open("https://m.facebook.com/upload.php?source_loc=composer&refid=7")
    br.select_form(nr=0)
    filepath = './trello2b.jpg'
    br.form.add_file(open(filepath, 'rb'), 'text/plain', 'd6sEz.jpg', nr=0, name='file1')
    print br.form
    br.form["caption"] = message
    br.submit()

if __name__=='__main__':
    p = ArghParser()
    p.add_commands([listcards,postfb,workon])
    p.dispatch()

