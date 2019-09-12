import os
import subprocess
import urllib

import requests


def lint(payload):
    global syntax_check, process, comment_body
    url = payload['pull_request']['url']
    url = url + '/files'
    r = requests.get(url)
    a = r.json()
    # print(a)
    print("Received Pull Request for %d Changed Files" % (len(a)))
    print("Initializing Linting Process")
    i = 0
    x = []
    filelist = []
    comment_body = ""
    for i in range(len(a)):
        raw = (a[i]['raw_url'])
        #print(raw)
        filename = (a[i]['filename']).split("/")
        file = filename[-1]

        re = urllib.request.urlopen('%s' % raw)
        # returned_value = os.system("start \"\" %s" %raw)
        data = re.read()
        dst = open("%s" % file, "wb")
        dst.write(data)
        dst = open("%s" % file, "r")
        print("Checking syntax errors for File: %d. %s" % (i + 1, file))

        file_ext = (file).split(".")
        print("File extension of the file: %s" % file_ext[-1])
        # HARD CODES FOR LINTERS
        lint = None
        # PHP
        if file_ext[-1] == 'php':
            lint = 'C:/Users/biswajit_nath/Desktop/text_gitpredictions/Linters/php/php.exe -l'
        # PY
        elif file_ext[-1] == 'py':
            lint = 'pycodestyle --select=E1,E4,E7,E9,W6'
            env_path = 'C:/Users/biswajit_nath/AppData/Local/Programs/Python/Python37-32/Lib/site-packages'
            #cmd = '%s %s' % (lintpy, file)
            #process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                       #stderr=subprocess.PIPE).communicate(0)
            #print(process)
        # C
        elif file_ext[-1] == 'c':
            env_path = 'C:/MinGW/bin'
            lintgcc = 'gcc'
            print("Cloned file: %s deleted" % file)
            print("Linting file : %s" % file)
            cmd = '%s %s' % (lintgcc, file)
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env=dict(os.environ, PATH=env_path)).communicate(0)
            #syntax_check = str(process).split(", b'")[-1]
            syntax_check = ""
            for j in range(len(process)):
                syntax_check = syntax_check + process[j].decode("utf_8")
                print(syntax_check)
        # CPP
        elif file_ext[-1] == 'cpp':
            env_path = 'C:/MinGW/bin'
            lintgpp = 'g++'
            print("Cloned file: %s deleted" % file)
            print("Linting file : %s" % file)
            cmd = '%s %s' % (lintgpp, file)
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env=dict(os.environ, PATH=env_path)).communicate(0)
            #print(process)
            #syntax_check = str(process).split(", b'")[-1]
            syntax_check = ""
            for j in range(len(process)):
                syntax_check = syntax_check + process[j].decode("utf_8")
                print(syntax_check)

        # JAVA
        #elif file_ext[-1] == 'java':
            #env_path = 'C:/Program Files/Java/jdk1.7.0_80/bin'
            #lintgpp = 'javac'
            #print("Cloned file: %s deleted" % file)
            #print("Linting file : %s" % file)
            #cmd = '%s %s' % (lintgpp, file)
            #process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
            #                           stderr=subprocess.PIPE,
            #                          env=dict(os.environ, PATH=env_path)).communicate(0)
            #syntax_check = str(process).replace("\\n", "")[6:-1]
            #syntax_check = ""
            #for j in range(len(process)):
            #    syntax_check = syntax_check + process[j].decode("utf_8")


        else:
            print("No linter found for %s extension" % file_ext[-1])
            s = "No linter found for %s extension" % file_ext[-1]
            syntax_check = ""

        if (lint != None):
            # print("Cloned file: %s deleted" % file)
            print("Linting file : %s" % file)
            cmd = '%s %s' % (lint, file)
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE).communicate(0)
            syntax_check = ""
            for j in range(len(process)):
                syntax_check = syntax_check + process[j].decode("utf_8")
                print (syntax_check)
                if "No syntax errors detected" in syntax_check:
                    syntax_check = ""

        # p = str(p)
        # p = p[2:-1]
        #a = process[-1]
        # if a == b'':
        # q = "No syntax error found"
        # print(q)
        #a = process[-1]
        if syntax_check != "":
            filelist.append(file)
            # print("Syntax error found: %s" % syntax_check)
            # q = "Syntax error found"
        dst.close()
        os.remove("%s" % file)
        # s = "%s %s" % (q, syntax_check)
        # x.append(s)
        i = i + 1

    if filelist:
        filelist = list(dict.fromkeys(filelist))
        filelist = ', '.join(filelist)
        comment_body = "Git Assist Prediction: To Be Rejected." \
                       "Syntax Errors found in the following files: %s." % filelist
        #x = []
        return comment_body
    else:
        comment_body = "No syntax error found in any file."
        #x = []
        #return comment_body
        return 1