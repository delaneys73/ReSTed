import cherrypy
import os
from Cheetah.Template import Template
import sys
import shutil
import glob
from docutils import core, io
import subprocess
import html2rst

config = {}
mainTemplate = ""

def setup(baseDir,webRoot):
    ReSTed.config = {
              "baseDir":baseDir,
              "templateDir": webRoot +"templates/",
              "templateExt" : "html",
              "usePandoc" : True
             }
    
    ReSTed.mainTemplate = "%(templateDir)smain.%(templateExt)s" % ReSTed.config

def getRST(html):
    if config["usePandoc"]==True:
        p = subprocess.Popen(['pandoc', '--from=html', '--to=rst'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return p.communicate(html)[0]
    else:
        return html2rst.html2text(html)
    
def getTemplate(view,title):
        indexTpl = Template(file=ReSTed.mainTemplate) 
        indexTpl.body = "%(templateDir)s%(view)s.%(templateExt)s" % dict(ReSTed.config,**{"view":view})
        indexTpl.title = title
        indexTpl.templateDir = ReSTed.config["templateDir"]
        return indexTpl

class ReSTed:
    
    def index(self):
        return self._browse(ReSTed.config["baseDir"],False)
    index.exposed = True

    def browse(self,dir):
        return self._browse(ReSTed.config["baseDir"]+"/"+dir,True)
    browse.exposed = True

    def _browse(self,dir,showBack):
        tpl = getTemplate("index","")
        tpl.showBack = showBack
        tpl.files = glob.glob1(dir, "*.rst")
        tpl.images = glob.glob1(dir, "*.png") + glob.glob1(dir, "*.jpg")
        dirs = [ name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name)) ]
        tpl.directories = dirs
        return str(tpl)
    
    def edit(self,file):
        return self._edit(file,"")

    def _edit(self,file,message):
        tpl= getTemplate("edit",file)
        tpl.message = message
        tpl.file = file
        fileName = ReSTed.config["baseDir"]+"/"+file
        fp = open(fileName, 'r')
        rst = fp.read()
        tpl.rst = rst
        overrides = {'doctitle_xform': file,
                 'initial_header_level': 1}
        parts = core.publish_parts(
        source=rst, source_path=ReSTed.config["baseDir"],
        destination_path=ReSTed.config["baseDir"],
        writer_name='html', settings_overrides=overrides)
        fragment = parts['html_body']
        tpl.html = fragment
        
        return str(tpl)
    edit.exposed = True

    def save(self,file,html):
        rstsrc = getRST(html)
        fileName = ReSTed.config["baseDir"]+"/"+file
        fp = open(fileName,'w')
        fp.write(rstsrc)
        fp.close()
        return self._edit(file,"Saved.")
    save.exposed = True
    
    def shutdown(self):
        cherrypy.engine.exit()
    shutdown.exposed = True


def start(baseDir,webRoot):
    setup(baseDir, webRoot)
    webconfig = {
        'global': 
        {
            'server.socket_port': 8000,
            'server.thread_pool': 10
        },
        '/include':
        {
            'tools.staticdir.on':True,
            'tools.staticdir.dir':webRoot+"/static/"
        },
        '/editor':
        {
            'tools.staticdir.on':True,
            'tools.staticdir.dir':baseDir
        }
    }
    cherrypy.quickstart(ReSTed(),"/",webconfig)