# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bibleimportdialog.ui'
#
# Created: Thu Feb 19 16:01:11 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_BibleImportDialog(object):
    def setupUi(self, BibleImportDialog):
        BibleImportDialog.setObjectName("BibleImportDialog")
        BibleImportDialog.resize(494, 725)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/openlp.org-icon-32.bmp"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        BibleImportDialog.setWindowIcon(icon)
        self.ImportToolBox = QtGui.QToolBox(BibleImportDialog)
        self.ImportToolBox.setGeometry(QtCore.QRect(20, 20, 451, 401))
        self.ImportToolBox.setFrameShape(QtGui.QFrame.StyledPanel)
        self.ImportToolBox.setObjectName("ImportToolBox")
        self.FileImportPage = QtGui.QWidget()
        self.FileImportPage.setGeometry(QtCore.QRect(0, 0, 447, 337))
        self.FileImportPage.setObjectName("FileImportPage")
        self.OSISGroupBox = QtGui.QGroupBox(self.FileImportPage)
        self.OSISGroupBox.setGeometry(QtCore.QRect(18, 65, 411, 81))
        self.OSISGroupBox.setObjectName("OSISGroupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.OSISGroupBox)
        self.gridLayout_2.setMargin(8)
        self.gridLayout_2.setSpacing(8)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.LocatioLabel = QtGui.QLabel(self.OSISGroupBox)
        self.LocatioLabel.setObjectName("LocatioLabel")
        self.gridLayout_2.addWidget(self.LocatioLabel, 0, 0, 1, 1)
        self.OSISLocationEdit = QtGui.QLineEdit(self.OSISGroupBox)
        self.OSISLocationEdit.setObjectName("OSISLocationEdit")
        self.gridLayout_2.addWidget(self.OSISLocationEdit, 0, 1, 1, 1)
        self.OsisFileButton = QtGui.QPushButton(self.OSISGroupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/imports/import_load.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.OsisFileButton.setIcon(icon1)
        self.OsisFileButton.setObjectName("OsisFileButton")
        self.gridLayout_2.addWidget(self.OsisFileButton, 0, 2, 1, 1)
        self.CVSGroupBox = QtGui.QGroupBox(self.FileImportPage)
        self.CVSGroupBox.setGeometry(QtCore.QRect(20, 170, 411, 191))
        self.CVSGroupBox.setObjectName("CVSGroupBox")
        self.gridLayout = QtGui.QGridLayout(self.CVSGroupBox)
        self.gridLayout.setMargin(8)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName("gridLayout")
        self.BooksLocationLabel = QtGui.QLabel(self.CVSGroupBox)
        self.BooksLocationLabel.setObjectName("BooksLocationLabel")
        self.gridLayout.addWidget(self.BooksLocationLabel, 0, 0, 1, 1)
        self.VerseLocationLabel = QtGui.QLabel(self.CVSGroupBox)
        self.VerseLocationLabel.setObjectName("VerseLocationLabel")
        self.gridLayout.addWidget(self.VerseLocationLabel, 4, 0, 1, 1)
        self.VerseLocationEdit = QtGui.QLineEdit(self.CVSGroupBox)
        self.VerseLocationEdit.setObjectName("VerseLocationEdit")
        self.gridLayout.addWidget(self.VerseLocationEdit, 4, 1, 1, 1)
        self.BooksLocationEdit = QtGui.QLineEdit(self.CVSGroupBox)
        self.BooksLocationEdit.setObjectName("BooksLocationEdit")
        self.gridLayout.addWidget(self.BooksLocationEdit, 0, 1, 1, 1)
        self.BooksFileButton = QtGui.QPushButton(self.CVSGroupBox)
        self.BooksFileButton.setIcon(icon1)
        self.BooksFileButton.setObjectName("BooksFileButton")
        self.gridLayout.addWidget(self.BooksFileButton, 0, 2, 1, 1)
        self.VersesFileButton = QtGui.QPushButton(self.CVSGroupBox)
        self.VersesFileButton.setIcon(icon1)
        self.VersesFileButton.setObjectName("VersesFileButton")
        self.gridLayout.addWidget(self.VersesFileButton, 4, 2, 1, 1)
        self.BibleNameEdit = QtGui.QLineEdit(self.FileImportPage)
        self.BibleNameEdit.setGeometry(QtCore.QRect(100, 20, 280, 28))
        self.BibleNameEdit.setObjectName("BibleNameEdit")
        self.BibleNameLabel = QtGui.QLabel(self.FileImportPage)
        self.BibleNameLabel.setGeometry(QtCore.QRect(18, 20, 98, 22))
        self.BibleNameLabel.setObjectName("BibleNameLabel")
        self.ImportToolBox.addItem(self.FileImportPage, "")
        self.WebBiblePage = QtGui.QWidget()
        self.WebBiblePage.setGeometry(QtCore.QRect(0, 0, 192, 228))
        self.WebBiblePage.setObjectName("WebBiblePage")
        self.WebBibleLayout = QtGui.QVBoxLayout(self.WebBiblePage)
        self.WebBibleLayout.setSpacing(8)
        self.WebBibleLayout.setMargin(8)
        self.WebBibleLayout.setObjectName("WebBibleLayout")
        self.OptionsGroupBox = QtGui.QGroupBox(self.WebBiblePage)
        self.OptionsGroupBox.setObjectName("OptionsGroupBox")
        self.formLayout_2 = QtGui.QFormLayout(self.OptionsGroupBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.LocationLabel = QtGui.QLabel(self.OptionsGroupBox)
        self.LocationLabel.setObjectName("LocationLabel")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.LocationLabel)
        self.LocationComboBox = QtGui.QComboBox(self.OptionsGroupBox)
        self.LocationComboBox.setObjectName("LocationComboBox")
        self.LocationComboBox.addItem(QtCore.QString())
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.LocationComboBox)
        self.BibleLabel = QtGui.QLabel(self.OptionsGroupBox)
        self.BibleLabel.setObjectName("BibleLabel")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.BibleLabel)
        self.BibleComboBox = QtGui.QComboBox(self.OptionsGroupBox)
        self.BibleComboBox.setObjectName("BibleComboBox")
        self.BibleComboBox.addItem(QtCore.QString())
        self.BibleComboBox.setItemText(0, "")
        self.BibleComboBox.addItem(QtCore.QString())
        self.BibleComboBox.addItem(QtCore.QString())
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.BibleComboBox)
        self.WebBibleLayout.addWidget(self.OptionsGroupBox)
        self.ProxyGroupBox = QtGui.QGroupBox(self.WebBiblePage)
        self.ProxyGroupBox.setObjectName("ProxyGroupBox")
        self.ProxySettingsLayout = QtGui.QFormLayout(self.ProxyGroupBox)
        self.ProxySettingsLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.ProxySettingsLayout.setMargin(8)
        self.ProxySettingsLayout.setSpacing(8)
        self.ProxySettingsLayout.setObjectName("ProxySettingsLayout")
        self.AddressLabel = QtGui.QLabel(self.ProxyGroupBox)
        self.AddressLabel.setObjectName("AddressLabel")
        self.ProxySettingsLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.AddressLabel)
        self.AddressEdit = QtGui.QLineEdit(self.ProxyGroupBox)
        self.AddressEdit.setObjectName("AddressEdit")
        self.ProxySettingsLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.AddressEdit)
        self.UsernameLabel = QtGui.QLabel(self.ProxyGroupBox)
        self.UsernameLabel.setObjectName("UsernameLabel")
        self.ProxySettingsLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.UsernameLabel)
        self.UsernameEdit = QtGui.QLineEdit(self.ProxyGroupBox)
        self.UsernameEdit.setObjectName("UsernameEdit")
        self.ProxySettingsLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.UsernameEdit)
        self.PasswordLabel = QtGui.QLabel(self.ProxyGroupBox)
        self.PasswordLabel.setObjectName("PasswordLabel")
        self.ProxySettingsLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.PasswordLabel)
        self.PasswordEdit = QtGui.QLineEdit(self.ProxyGroupBox)
        self.PasswordEdit.setObjectName("PasswordEdit")
        self.ProxySettingsLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.PasswordEdit)
        self.WebBibleLayout.addWidget(self.ProxyGroupBox)
        self.ImportToolBox.addItem(self.WebBiblePage, "")
        self.LicenceDetailsGroupBox = QtGui.QGroupBox(BibleImportDialog)
        self.LicenceDetailsGroupBox.setGeometry(QtCore.QRect(10, 435, 471, 151))
        self.LicenceDetailsGroupBox.setMinimumSize(QtCore.QSize(0, 123))
        self.LicenceDetailsGroupBox.setObjectName("LicenceDetailsGroupBox")
        self.formLayout = QtGui.QFormLayout(self.LicenceDetailsGroupBox)
        self.formLayout.setMargin(8)
        self.formLayout.setHorizontalSpacing(8)
        self.formLayout.setObjectName("formLayout")
        self.VersionNameLabel = QtGui.QLabel(self.LicenceDetailsGroupBox)
        self.VersionNameLabel.setObjectName("VersionNameLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.VersionNameLabel)
        self.VersionNameEdit = QtGui.QLineEdit(self.LicenceDetailsGroupBox)
        self.VersionNameEdit.setObjectName("VersionNameEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.VersionNameEdit)
        self.CopyrightLabel = QtGui.QLabel(self.LicenceDetailsGroupBox)
        self.CopyrightLabel.setObjectName("CopyrightLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.CopyrightLabel)
        self.CopyrightEdit = QtGui.QLineEdit(self.LicenceDetailsGroupBox)
        self.CopyrightEdit.setObjectName("CopyrightEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.CopyrightEdit)
        self.PermisionLabel = QtGui.QLabel(self.LicenceDetailsGroupBox)
        self.PermisionLabel.setObjectName("PermisionLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.PermisionLabel)
        self.PermisionEdit = QtGui.QLineEdit(self.LicenceDetailsGroupBox)
        self.PermisionEdit.setObjectName("PermisionEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.PermisionEdit)
        self.MessageLabel = QtGui.QLabel(BibleImportDialog)
        self.MessageLabel.setGeometry(QtCore.QRect(20, 670, 271, 17))
        self.MessageLabel.setObjectName("MessageLabel")
        self.ProgressGroupBox = QtGui.QGroupBox(BibleImportDialog)
        self.ProgressGroupBox.setGeometry(QtCore.QRect(10, 600, 471, 70))
        self.ProgressGroupBox.setObjectName("ProgressGroupBox")
        self.gridLayout_3 = QtGui.QGridLayout(self.ProgressGroupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.ProgressBar = QtGui.QProgressBar(self.ProgressGroupBox)
        self.ProgressBar.setProperty("value", QtCore.QVariant(0))
        self.ProgressBar.setInvertedAppearance(False)
        self.ProgressBar.setObjectName("ProgressBar")
        self.gridLayout_3.addWidget(self.ProgressBar, 0, 0, 1, 1)
        self.layoutWidget = QtGui.QWidget(BibleImportDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(300, 680, 180, 38))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ImportButton = QtGui.QPushButton(self.layoutWidget)
        self.ImportButton.setObjectName("ImportButton")
        self.horizontalLayout.addWidget(self.ImportButton)
        self.CancelButton = QtGui.QPushButton(self.layoutWidget)
        self.CancelButton.setObjectName("CancelButton")
        self.horizontalLayout.addWidget(self.CancelButton)

        self.retranslateUi(BibleImportDialog)
        self.ImportToolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(BibleImportDialog)
        BibleImportDialog.setTabOrder(self.BibleNameEdit, self.OSISLocationEdit)
        BibleImportDialog.setTabOrder(self.OSISLocationEdit, self.OsisFileButton)
        BibleImportDialog.setTabOrder(self.OsisFileButton, self.BooksLocationEdit)
        BibleImportDialog.setTabOrder(self.BooksLocationEdit, self.BooksFileButton)
        BibleImportDialog.setTabOrder(self.BooksFileButton, self.VerseLocationEdit)
        BibleImportDialog.setTabOrder(self.VerseLocationEdit, self.VersesFileButton)
        BibleImportDialog.setTabOrder(self.VersesFileButton, self.LocationComboBox)
        BibleImportDialog.setTabOrder(self.LocationComboBox, self.BibleComboBox)
        BibleImportDialog.setTabOrder(self.BibleComboBox, self.AddressEdit)
        BibleImportDialog.setTabOrder(self.AddressEdit, self.UsernameEdit)
        BibleImportDialog.setTabOrder(self.UsernameEdit, self.PasswordEdit)
        BibleImportDialog.setTabOrder(self.PasswordEdit, self.VersionNameEdit)
        BibleImportDialog.setTabOrder(self.VersionNameEdit, self.CopyrightEdit)
        BibleImportDialog.setTabOrder(self.CopyrightEdit, self.PermisionEdit)

    def retranslateUi(self, BibleImportDialog):
        BibleImportDialog.setWindowTitle(QtGui.QApplication.translate("BibleImportDialog", "Bible Registration", None, QtGui.QApplication.UnicodeUTF8))
        self.OSISGroupBox.setTitle(QtGui.QApplication.translate("BibleImportDialog", "OSIS Bible", None, QtGui.QApplication.UnicodeUTF8))
        self.LocatioLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "File Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.CVSGroupBox.setTitle(QtGui.QApplication.translate("BibleImportDialog", "CVS Bible", None, QtGui.QApplication.UnicodeUTF8))
        self.BooksLocationLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Books Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.VerseLocationLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Verse Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.BibleNameLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Bible Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.ImportToolBox.setItemText(self.ImportToolBox.indexOf(self.FileImportPage), QtGui.QApplication.translate("BibleImportDialog", "File Import Page", None, QtGui.QApplication.UnicodeUTF8))
        self.OptionsGroupBox.setTitle(QtGui.QApplication.translate("BibleImportDialog", "Download Options", None, QtGui.QApplication.UnicodeUTF8))
        self.LocationLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.LocationComboBox.setItemText(0, QtGui.QApplication.translate("BibleImportDialog", "Crosswalk", None, QtGui.QApplication.UnicodeUTF8))
        self.BibleLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Bible:", None, QtGui.QApplication.UnicodeUTF8))
        self.BibleComboBox.setItemText(1, QtGui.QApplication.translate("BibleImportDialog", "NIV", None, QtGui.QApplication.UnicodeUTF8))
        self.BibleComboBox.setItemText(2, QtGui.QApplication.translate("BibleImportDialog", "KJV", None, QtGui.QApplication.UnicodeUTF8))
        self.ProxyGroupBox.setTitle(QtGui.QApplication.translate("BibleImportDialog", "Proxy Settings (Optional)", None, QtGui.QApplication.UnicodeUTF8))
        self.AddressLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Proxy Address:", None, QtGui.QApplication.UnicodeUTF8))
        self.UsernameLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.PasswordLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.ImportToolBox.setItemText(self.ImportToolBox.indexOf(self.WebBiblePage), QtGui.QApplication.translate("BibleImportDialog", "Web Bible Import page", None, QtGui.QApplication.UnicodeUTF8))
        self.LicenceDetailsGroupBox.setTitle(QtGui.QApplication.translate("BibleImportDialog", "Licence Details", None, QtGui.QApplication.UnicodeUTF8))
        self.VersionNameLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Version Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.CopyrightLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Copyright:", None, QtGui.QApplication.UnicodeUTF8))
        self.PermisionLabel.setText(QtGui.QApplication.translate("BibleImportDialog", "Permission:", None, QtGui.QApplication.UnicodeUTF8))
        self.ProgressGroupBox.setTitle(QtGui.QApplication.translate("BibleImportDialog", "Import Progress", None, QtGui.QApplication.UnicodeUTF8))
        self.ProgressBar.setFormat(QtGui.QApplication.translate("BibleImportDialog", "%p", None, QtGui.QApplication.UnicodeUTF8))
        self.ImportButton.setText(QtGui.QApplication.translate("BibleImportDialog", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelButton.setText(QtGui.QApplication.translate("BibleImportDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

