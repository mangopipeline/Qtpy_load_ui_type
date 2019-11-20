"""

is a helper lib that exposed the "loadUiType" method to both Qt4 and Qt5

 :example:

    >>> from load_ui_type import loadUiType
    >>>
    >>> BASE,FORM = loadUiType(path_to_uic_file)
    >>>
    >>> class MyQtApp(BASE,FORM):
    >>>     def __init__(self,*args,**kwargs):
    >>>         super(MyQtApp,self).__init__(*args,**kwargs)
    >>>         self.setupUi(self)
"""
from Qt import IsPyQt4, IsPyQt5, IsPySide, IsPySide2, QtWidgets


if IsPyQt4 or IsPyQt5:
    if IsPyQt4:
        from PyQt4.uic import loadUiType
    else:
        from PyQt5.uic import loadUiType

else:
    if IsPySide:
        import pysideuic as uic
    else:
        import pyside2uic as uic

    import xml.etree.ElementTree as xml

    try:
        from cStringIO import StringIO  # Python 2.7
    except ModuleNotFoundError:
        from io import StringIO  # Python 3.7

    def loadUiType(ui_file):
        """
        Pyside "loadUiType" command like PyQt4 has one, so we have to convert the
        ui file to py code in-memory first and then execute it in a special frame
        to retrieve the form_class.
        """

        parsed = xml.parse(ui_file)
        widget_class = parsed.find('widget').get('class')
        form_class = parsed.find('class').text

        with open(ui_file, 'r') as f:
            stringioval = StringIO()
            frame = {}

            uic.compileUi(f, stringioval, indent=0)
            pyc = compile(stringioval.getvalue(), '<string>', 'exec')
            exec(pyc, frame)

            # Fetch the base_class and form class based on their type
            # in the xml from designer
            form_class = frame['Ui_%s' % form_class]
            base_class = eval('QtWidgets.%s' % widget_class)

        return form_class, base_class
