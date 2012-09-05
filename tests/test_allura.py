import errno, feedparser, json, MySQLdb, os, pprint, sys, unittest, urllib
sys.path.insert(0, "..")
from Bicho.backends import Backend
from Bicho.backends.allura import DBAlluraBackend
from Bicho.Config import Config
from Bicho.common import Tracker #, Issue, People, Change
from Bicho.db.database import DBIssue, DBBackend, get_database

# search/?limit=15&q=status%3Aopen&page=10

class AlluraTest(unittest.TestCase):
    
    page = 10
    limit = 15
    status = 'open'
    issue_id_test = 2643
    tests_data_dir = None
    issuesDB = None
    
    def read_issues(self):
        if not os.path.isdir (self.tests_data_dir):
            create_dir (self.tests_data_dir)
        project_name = Config.url.split("/")[-2]                
        issues_file = project_name+"_p"+str(self.page)+"_"+str(self.limit)+"_"+self.status
        self.project_issues_file = os.path.join(self.tests_data_dir, issues_file)
        print("Using project file test: " + issues_file)

        try:
            f = open(self.project_issues_file)
        except Exception, e:
            print "Can not find test data"
            if e.errno == errno.ENOENT:
                f = open(self.project_issues_file,'w+')
                issues_url = Config.url+"/search/?limit="+str(self.limit)
                issues_url +="&q=status%3A"+self.status+"&page="+str(self.page)
                print "URL for getting data: " + issues_url
                fr = urllib.urlopen(issues_url)
                f.write(fr.read())
                f.close()
                f = open(self.project_issues_file)
        return f.read()
    
    def read_issue(self, issue_id):
        issue_url = Config.url+"/"+str(issue_id)
        project_name = Config.url.split("/")[-2]                 
        issue_file = os.path.join(self.tests_data_dir, project_name+"." + str(issue_id))
         
        try:             
            f = open(issue_file)
        except Exception, e:
            if e.errno == errno.ENOENT:
                print ("Downloading " + issue_file)
                f = open(issue_file,'w')
                fr = urllib.urlopen(issue_url)
                f.write(fr.read())
                f.close()
                f = open(issue_file)
            else:
                print "ERROR", e.errno
                raise e
        return f.read()

    # Open the changes bug data from a file for testing purposes
    def read_issue_changes(self, issue_id):
        issue_url = Config.url+"/"+str(issue_id)
        changes_url = issue_url.replace("rest/","")+"/feed.atom"
        project_name = Config.url.split("/")[-2]
        changes_file = os.path.join(self.tests_data_dir, project_name+"." + str(issue_id) + ".changes")

        if os.path.isfile(changes_file): pass
        else:
            print ("Downloading " + changes_file)
            f = open(changes_file,'w')
            fr = urllib.urlopen(changes_url)
            f.write(fr.read())
            f.close()
        return changes_file

    def testReadIssues(self):
        issuesList_data = json.loads(self.read_issues())
        for issue in issuesList_data['tickets']:
            issue_data = json.loads(self.read_issue(issue['ticket_num']))
            issue_bicho = self.backend.parse_bug(issue_data['ticket'])
            changes_file = self.read_issue_changes(issue['ticket_num'])
            changes_data = feedparser.parse(changes_file)
            changes_bicho = self.backend.parse_changes(changes_data)
            for c in changes_bicho:
                issue_bicho.add_change(c)                 
            self.issuesDB.insert_issue(issue_bicho, AlluraTest.dbtracker.id)
        
    def testReadIssue(self): 
        self.read_issue(self.issue_id_test)
        
    def testReadChange(self):
        self.read_issue_changes(self.issue_id_test)
        
    def testRunBackend(self):
        print ("Running backed")
        # self.backend.run()
    
    def setUp(self):
        self.backend = AlluraTest.backend
        self.tests_data_dir = AlluraTest.tests_data_dir
        self.issuesDB = AlluraTest.issuesDB

    @staticmethod
    def setUpDB():
        Config.db_driver_out = "mysql"
        Config.db_user_out = "root"
        Config.db_password_out = ""
        Config.db_hostname_out = ""
        Config.db_port_out = ""
        Config.db_database_out = "bichoalluraTest"
        
        db = MySQLdb.connect(user=Config.db_user_out, passwd=Config.db_password_out)
        c = db.cursor()
        sql = "DROP DATABASE " + Config.db_database_out
        sql += "; CREATE DATABASE "+ Config.db_database_out +" CHARACTER SET utf8 COLLATE utf8_unicode_ci"
        c.execute(sql)                        

    @staticmethod                
    def setUpBackend():
        backend_name = 'allura' 
        Config.delay = 1
        Config.debug = True
        Config.url = "http://sourceforge.net/rest/p/allura/tickets"
        AlluraTest.setUpDB()
        AlluraTest.issuesDB = get_database (DBAlluraBackend())                    
                
        AlluraTest.issuesDB.insert_supported_traker(backend_name, "beta")
        AlluraTest.tracker = Tracker (Config.url, backend_name, "beta")
        AlluraTest.dbtracker = AlluraTest.issuesDB.insert_tracker(AlluraTest.tracker)
        
        AlluraTest.tests_data_dir = os.path.join('./data/', AlluraTest.tracker.name)        
        AlluraTest.backend = Backend.create_backend(backend_name)
        
if __name__ == '__main__':
    AlluraTest.setUpBackend()
    unittest.main()