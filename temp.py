__author__ = 'chanakya'


from collections import Counter
from operator import itemgetter

t = [[u'I20091207-1800', u'Resourc', u'filter', u'cannot', u'edit', u'link', u'packag', u'(', u'properti', u'page', u'show', u'folder', u',', u'packag', u')', u'.'], [u'Thi', u'problem', u'adapt', u'registered/impl', u'type', u'(', u'IResource/IContainer/IFolder/', u'...', u')', u'.'], [u'Need', u'look', u'RC1', u'fix', u'togeth', u'Platform', u'UI.'], [u'OK', u',', u'multipl', u'problem', u':', u'1.', u'org.eclipse.ui.ide/plugin.xml', u'contribut', u'propertyPag', u'"', u'org.eclipse.ui.propertypages.resource.filt', u'"', u':', u'<enabledWhen>', u'<or>', u'<adapt', u'type=', u'"', u'org.eclipse.core.resources.IProject', u'"', u'/>', u'<adapt', u'type=', u'"', u'org.eclipse.core.resources.IFold', u'"', u'/>', u'</or>', u'</enabledWhen>', u'2.', u'org.eclipse.jdt.ui', u"'s", u'JavaElementAdapterFactori', u'contribut', u'adapt', u'IJavaEl', u'IResourc', u',', u'IFold', u'IContain', u'(', u'project', u'case', u'handl', u'separ', u'adapt', u'IJavaProject', u'IProject', u')', u'.'], [u'3.'], [u'The', u'ResourceFilterPag', u'class', u'get', u'adapt', u'IContainer.class', u',', u'IFolder.class', u'would', u'expect', u'enabl', u'expression.'], [u'Solv', u'2.'], [u'(', u'i.e.'], [u'ad', u'adapte', u'IJavaEl', u')', u'unwant', u'consequ', u'whole', u'platform', u',', u'shouldn', u"'t", u'risk', u'RC1.'], [u'Up', u',', u'never', u'need', u'adapt', u'IContain', u'IFold', u',', u'I', u'think', u'best', u'way', u'fix', u'would', u'chang', u'resourc', u'filter', u'page', u',', u'adapt', u'IResource.'], [u'I', u"'ll", u'attach', u'patch', u'implement', u'o.e.ui.ide.'], [u'Serg', u',', u'could', u'pleas', u'review', u'?'], [u'Creat', u'attach', u'168178', u'Fix', u'Sorri', u',', u'I', u"'m", u'sure', u'Serg', u'involv', u'all.'], [u'+1', u'RC1', u'anyon', u'?'], [u'You', u'also', u'releas', u'patch', u'(', u"'s", u'get', u'late', u'...', u')', u'.'], [u'Review', u'-', u'look', u'good.'], [u'Thank', u'(', u'In', u'repli', u'comment', u'#', u'5', u')', u'>', u'Sorri', u',', u'I', u"'m", u'sure', u'Serg', u'involv', u'all.'], [u'>', u'>', u'+1', u'RC1', u'anyon', u'?'], [u'You', u'also', u'releas', u'patch', u'(', u"'s", u'get', u'late', u'>', u'...', u')', u'.'], [u'Fair', u'enough', u',', u'I', u"'ll", u'commit', u'patch', u'-', u'fix', u'head.'], [u'hum', u',', u'add', u'+1', u'?'], [u'I', u'guess', u'mine', u'would', u'strang', u'sinc', u'I', u'commit', u'it.'], [u'ThanksThank', u',', u'Serge.Thi', u'bug', u'inadvert', u'disabl', u'properti', u'page', u'regular', u'folder', u'containers.Nev', u'mind', u',', u'someth', u'els', u'caus', u'bug', u'fail', u'3.7M6', u',', u'I', u"'ll", u'open', u'anoth', u'bug', u'track', u'failur', u'case.']]
thematic = {}
st = []
for x in t:
    lower_sentence = [s.lower() for s in x]
    st.append(lower_sentence)
#print t, st

for x in st:
    tp = Counter(x)
    for k in tp:
        if k in thematic.keys():
            thematic[k] += tp[k]
        else:
            thematic[k] = tp[k]

sth = sorted(thematic.items(), key=itemgetter(1), reverse=True)
for val in sth:
    if len(val[0]) > 3:
        print val
#temp = sorted(thematic.items(), key=itemgetter(1))
