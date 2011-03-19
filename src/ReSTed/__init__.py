import cherrypy
import os
from Cheetah.Template import Template
import sys
import shutil
import glob
from docutils import core, io
import subprocess



config = {
          "baseDir":os.getcwd(),
          "templateDir": "../templates/",
          "templateExt" : "html"
         }

mainTemplate = "%(templateDir)smain.%(templateExt)s" % config

def html2rst(html):
    p = subprocess.Popen(['pandoc', '--from=html', '--to=rst'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return p.communicate(html)[0]

def getTemplate(view,title):
        indexTpl = Template(file=mainTemplate) 
        indexTpl.body = "%(templateDir)s%(view)s.%(templateExt)s" % dict(config,**{"view":view})
        indexTpl.title = title
        indexTpl.templateDir = config["templateDir"]
        return indexTpl

class ReSTed:
    
    def index(self):
        tpl = getTemplate("index","")
        tpl.files = glob.glob1(config["baseDir"], "*.rst")
        tpl.directories = []
        return str(tpl)
    index.exposed = True

    def edit(self,file):
        return self._edit(file,"")

    def _edit(self,file,message):
        tpl= getTemplate("edit",file)
        tpl.message = message
        tpl.file = file
        fileName = config["baseDir"]+"/"+file
        fp = open(fileName, 'r')
        rst = fp.read()
        tpl.rst = rst
        overrides = {'doctitle_xform': file,
                 'initial_header_level': 1}
        parts = core.publish_parts(
        source=rst, source_path=config["baseDir"],
        destination_path=config["baseDir"],
        writer_name='html', settings_overrides=overrides)
        fragment = parts['html_body']
        tpl.html = fragment
        
        return str(tpl)
    edit.exposed = True

    def save(self,file,html):
        rstsrc = html2rst(html)
        fileName = config["baseDir"]+"/"+file
        fp = open(fileName,'w')
        fp.write(rstsrc)
        fp.close()
        return self._edit(file,"Saved.")
    save.exposed = True
    
config["baseDir"] = sys.argv[1]

webconfig = {
    'global': 
    {
        'server.socket_port': 8000,
        'server.thread_pool': 10
    },
    '/include':
    {
        'tools.staticdir.on':True,
        'tools.staticdir.dir':os.getcwd()+"/../static/"
    },
    '/editor':
    {
        'tools.staticdir.on':True,
        'tools.staticdir.dir':sys.argv[1]
    }
}

cherrypy.quickstart(ReSTed(),"/",webconfig)