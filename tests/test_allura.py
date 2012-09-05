import errno, json, os, pprint, sys, unittest, urllib
sys.path.insert(0, "..")
from Bicho.backends import Backend
from Bicho.Config import Config

# search/?limit=15&q=status%3Aopen&page=10

class AlluraTest(unittest.TestCase):
    
    trk_name = "allura"
    page = 10
    limit = 15
    status = 'open'
    issue_id_test = 2643
    tests_data_dir = os.path.join("./data/", trk_name)
    
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
        return f
    
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
        return f

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
        issuesList_data = json.loads(self.read_issues().read())
        for issue in issuesList_data['tickets']:
            issue_data = self.read_issue(issue['ticket_num'])
            changes_file = self.read_issue_changes(issue['ticket_num'])
        
    def testReadIssue(self): 
        self.read_issue(self.issue_id_test)
        
    def testReadChange(self):
        self.read_issue_changes(self.issue_id_test)
        
    def testRunBackend(self):
        print ("Running backed")
        # self.backend.run()
    
    def setUp(self):
        Config.delay = 1
        Config.url = "http://sourceforge.net/rest/p/allura/tickets"
        self.backend = Backend.create_backend('allura')
            
if __name__ == '__main__':
    unittest.main()