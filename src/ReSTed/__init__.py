import cherrypy
import os
from Cheetah.Template import Template
import sys
import shutil
import glob
from docutils import core, io
import subprocess
import html2rst
import webbrowser

config = {}
mainTemplate = ""

def setup(baseDir,webRoot):
    ReSTed.config = {
              "baseDir":baseDir,
              "templateDir": webRoot +"templates/",
              "templateExt" : "html",
              "usePandoc" : False
             }
    
    ReSTed.mainTemplate = "%(templateDir)smain.%(templateExt)s" % ReSTed.config

def getRST(html):
    if ReSTed.config["usePandoc"]==True:
        p = subprocess.Popen(['pandoc', '--from=html', '--to=rst'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return p.communicate(html)[0]
    else:
        return html2rst.html2text(html)

def getTemplatePath(view):
    return "%(templateDir)s%(view)s.%(templateExt)s" % dict(ReSTed.config,**{"view":view})
    
def getTemplate(view,title):
        indexTpl = Template(file=ReSTed.mainTemplate) 
        indexTpl.body = getTemplatePath(view)
        indexTpl.title = title
        indexTpl.templateDir = ReSTed.config["templateDir"]
        return indexTpl

class ReSTed:
    
    def index(self):
        return self._browse(ReSTed.config["baseDir"],"",False)
    index.exposed = True

    def browse(self,dir):
        return self._browse(os.path.join(ReSTed.config["baseDir"],dir),dir,True)
    browse.exposed = True

    def _browse(self,dir,subdir,showBack):
        tpl = getTemplate("index","")
        tpl.showBack = showBack
        tpl.files = glob.glob1(dir, "*.rst")
        tpl.subdir = subdir
        tpl.images = glob.glob1(dir, "*.png") + glob.glob1(dir, "*.jpg")
        dirs = []
       
        for d in os.listdir(dir):
            if (os.path.isdir(os.path.join(dir,d))):
                dirs.append(d+'/')
   
        tpl.directories = dirs
        return str(tpl)
    
    def edit(self,file):
        return self._edit(file,"")
    
    
    def _getEditor(self):
        cookieEditor = "wysiwyg"
        if cherrypy.request.cookie.has_key("rested.editor"):
            morsel = cherrypy.request.cookie["rested.editor"]
            cookieEditor = morsel.value
        return cookieEditor
    
    def _edit(self,file,message):
        rawedit = False
        
        cookieEditor = self._getEditor(); 
        
        if cookieEditor=="raw":
            rawedit = True
        
        tpl= getTemplate("edit",file)
        tpl.message = message
        tpl.file = file
        fileName = os.path.join(ReSTed.config["baseDir"],file)
        fp = open(fileName, 'r')
        rst = fp.read()
        tpl.rst = rst
        
        if rawedit:
            tpl.editor = getTemplatePath("editraw")
        else:
            tpl.editor = getTemplatePath("editgui")
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

    def save(self,file,html,rst,source):
        if source=="html":
            rstsrc = getRST(html)
        else:
            rstsrc = rst
            
        fileName = os.path.join(ReSTed.config["baseDir"],file)
        fp = open(fileName,'w')
        fp.write(rstsrc)
        fp.close()
        return self._edit(file,"Saved.")
    save.exposed = True
    
    def shutdown(self):
        cherrypy.engine.exit()
    shutdown.exposed = True
    
    def preview(self,rst,file):
        tpl= Template(file=getTemplatePath("preview"))
        
        overrides = {'doctitle_xform': file,
             'initial_header_level': 1}
    
        parts = core.publish_parts(
            source=rst, source_path=ReSTed.config["baseDir"],
            destination_path=ReSTed.config["baseDir"],
            writer_name='html', settings_overrides=overrides)
        
        fragment = parts['html_body']
        tpl.html = fragment
        return str(tpl)
    preview.exposed = True

    def stylesheet(self):
        fileName =os.path.join(ReSTed.config["baseDir"],'styles','mincom.css')
        fp = open(fileName, 'r')
        css = fp.read()
        return css
    stylesheet.exposed = True
        
def start(baseDir,webRoot):
    setup(baseDir, webRoot)
    port = 8000
    webconfig = {
        'global': 
        {
            'server.socket_port': port,
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
        },
    }
    
    webbrowser.open_new("http://127.0.0.1:%s" % port)
    cherrypy.quickstart(ReSTed(),"/",webconfig)
    

    