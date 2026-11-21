"""Обновляет содержание в DOCX через LibreOffice (UNO) и сохраняет DOCX и PDF."""
import sys, time, subprocess, uno
from com.sun.star.beans import PropertyValue

def prop(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p

src = sys.argv[1]
proc = subprocess.Popen(['/Applications/LibreOffice.app/Contents/MacOS/soffice', '--headless', '--norestore',
                         '--accept=socket,host=127.0.0.1,port=2002;urp;'])
ctx = None
for _ in range(60):
    try:
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
        ctx = resolver.resolve('uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext')
        break
    except Exception:
        time.sleep(0.5)
desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
url = uno.systemPathToFileUrl(src)
doc = desktop.loadComponentFromURL(url, '_blank', 0, (prop('Hidden', True),))
idx = doc.getDocumentIndexes()
for i in range(idx.getCount()):
    idx.getByIndex(i).update()
doc.store()
doc.storeToURL(uno.systemPathToFileUrl(src[:-5] + '.pdf'), (prop('FilterName', 'writer_pdf_Export'),))
doc.close(True)
try:
    desktop.terminate()
except Exception:
    pass
proc.wait(timeout=20)
print('toc updated:', idx.getCount())
