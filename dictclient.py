import socket, re

def dequote(str):
    quotechars = "'\""
    while len(str) and str[0] in quotechars:
        str = str[1:]
    while len(str) and str[-1] in quotechars:
        str = str[0:-1]
    return str

def enquote(str):
    return '"' + str.replace('"', "\\\"") + '"'

class Connection:
    def __init__(self, hostname = 'localhost', port = 2628):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((hostname, port))
        self.rfile = self.sock.makefile("rt")
        self.wfile = self.sock.makefile("wt", 0)
        self.saveconnectioninfo()

    def getresultcode(self):
        line = self.rfile.readline().strip()
        code, text = line.split(' ', 1)
        return [int(code), text]

    def get200result(self):
        """Used when expecting a single line of text -- a 200-class
        result.  Returns [intcode, remaindertext]"""

        code, text = self.getresultcode()
        if code < 200 or code >= 300:
            raise Exception, "Got '%s' when 200-class response expected" % \
                  line
        return [code, text]

    def get100block(self):
        """Used when expecting multiple lines of text -- gets the block
        part only.  Does not get any codes or anything!  Returns a string."""
        data = []
        while 1:
            line = self.rfile.readline().strip()
            if line == '.':
                break
            data.append(line)
        return "\n".join(data)

    def get100result(self):
        """Used when expecting multiple lines of text, terminated by a period
        and a 200 code.  Returns: [initialcode, [bodytext_1lineperentry],
        finalcode]"""
        code, text = self.getresultcode()
        if code < 100 or code >= 200:
            raise Exception, "Got '%s' when 100-class response expected" % \
                  code

        bodylines = self.get100block().split("\n")

        code2 = self.get200result()[0]
        return [code, bodylines, code2]

    def get100dict(self):
        """Used when expecting a dictionary of results."""
        dict = {}
        for line in self.get100result()[1]:
            key, val = line.split(' ', 1)
            dict[key] = dequote(val)
        return dict

    def saveconnectioninfo(self):
        code, string = self.get200result()
        assert code == 220
        capstr, msgid = re.search('<(.*)> (<.*>)$', string).groups()
        self.capabilities = capstr.split('.')
        self.messageid = msgid
        
    def getcapabilities(self):
        """Returns a list of the capabilities advertised by the server."""
        return self.capabilities

    def getmessageid(self):
        """Returns the message id, including angle brackets."""
        return self.messageid

    def getdbdescs(self):
        """Gets a dict of available databases.  The key is the db name
        and the value is the db description."""
        if hasattr(self, 'dbdescs'):
            return self.dbdescs
        
        self.sendcommand("SHOW DB")
        self.dbdescs = self.get100dict()
        return self.dbdescs

    def getstratdescs(self):
        """Gets a dict of available strategies.  The key is the strat
        name and the value is the strat description."""
        if hasattr(self, 'stratdescs'):
            return self.stratdescs

        self.sendcommand("SHOW STRAT")
        self.stratdescs = self.get100dict()
        return self.stratdescs

    def getdbobj(self, dbname):
        if not hasattr(self, 'dbobjs'):
            self.dbobjs = {}

        if self.dbobjs.has_key(dbname):
            return self.dbobjs[dbname]

        # We use self.dbdescs explicitly since we don't want to
        # generate net traffic with this request!

        if not dbname in self.dbdescs.keys():
            raise Exception, "Invalid database name '%s'" % dbname

        self.dbobjs[dbname] = Database(self, dbname)
        return self.dbobjs[dbname]

    def sendcommand(self, command):
        self.wfile.write(command + "\n")

    def define(self, database, word):
        """Returns a list of Definition objects for each matching
        definition."""
        self.getdbdescs()               # Prime the cache

        if database != '*' and database != '!' and \
           not database in self.getdbdescs():
            raise Exception, "Invalid database '%s' specified" % database
        
        self.sendcommand("DEFINE " + enquote(database) + " " + enquote(word))
        code = self.getresultcode()[0]

        retval = []

        if code == 552:
            # No definitions.
            return []
        if code != 150:
            raise Exception, "Unknown code %d" % code

        while 1:
            code, text = self.getresultcode()
            if code != 151:
                break

            resultword, resultdb = re.search('^"(.+)" (\S+)', text).groups()
            defstr = self.get100block()
            retval.append(Definition(self, self.getdbobj(resultdb),
                                     resultword, defstr))
        return retval


class Database:
    def __init__(self, dictconn, dbname):
        self.conn = dictconn
        self.name = dbname
    
    def getname(self):
        return self.name
    
    def getdescription(self):
        if hasattr(self, 'description'):
            return self.description
        self.description = self.conn.getdbdescs()[self.name]
        return self.description
    
    def getinfo(self):
        """Returns a string of info describing this database."""
        if hasattr(self, 'info'):
            return self.info
        
        self.conn.sendcommand("SHOW INFO " + self.name)
        self.info = "\n".join(self.conn.get100result()[1])
        return self.info

class Definition:
    def __init__(self, dictconn, db, word, defstr = None):
        self.conn = dictconn
        self.db = db
        self.word = word
        self.defstr = defstr

    def getdb(self):
        return self.db

    def getdefstr(self):
        if not self.defstr:
            self.defstr = self.conn.define(self.getdb().getname(), self.word)[0].getdefstr()
        return self.defstr

    def getword(self):
        return self.word
