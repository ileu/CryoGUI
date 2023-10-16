# import Statements
from PyQt6 import QtCore, QtGui, QtWidgets

# from PyQt5.QtWidgets import QMessageBox, QWidget
# from reportViewerWindow import Ui_reportViewerWindow
import os


# Main Class that holds User Interface Objects
class Ui_MainWindow(object):
    # Function for Opening Report Viewer Window From Main Window by clicking View Reports button
    def openReportViewer(self):
        self.window = QtWidgets.QMainWindow()
        # self.ui = Ui_reportViewerWindow()
        # self.ui.setupUi(self.window)
        self.window.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(834, 428)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setStyleSheet("background-color: Cornflowerblue")
        MainWindow.setAutoFillBackground(True)

        # Sim Card Button
        self.simCardButton = QtWidgets.QPushButton(self.centralwidget)
        self.simCardButton.setGeometry(QtCore.QRect(30, 200, 211, 30))
        self.simCardButton.setToolTip("Select to parse sim card data")
        self.simCardButton.setStyleSheet("background-color: Silver")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.simCardButton.setFont(font)
        self.simCardButton.setObjectName("simCardButton")

        # Call Logs Button
        self.callLogButton = QtWidgets.QPushButton(self.centralwidget)
        self.callLogButton.setGeometry(QtCore.QRect(30, 300, 211, 30))
        self.callLogButton.setToolTip("Select to parse call log data")
        self.callLogButton.setStyleSheet("background-color: Silver")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.callLogButton.setFont(font)
        self.callLogButton.setObjectName("callLogButton")

        # SMS Button
        self.smsButton = QtWidgets.QPushButton(self.centralwidget)
        self.smsButton.setGeometry(QtCore.QRect(30, 250, 211, 30))
        self.smsButton.setToolTip("Select to parse sms data")
        self.smsButton.setStyleSheet("background-color: Silver")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.smsButton.setFont(font)
        self.smsButton.setObjectName("smsButton")

        # Canonical Address Button
        self.canonicalAddressesButton = QtWidgets.QPushButton(self.centralwidget)
        self.canonicalAddressesButton.setGeometry(QtCore.QRect(30, 150, 211, 30))
        self.canonicalAddressesButton.setToolTip(
            "Select to parse canonical address data"
        )
        self.canonicalAddressesButton.setStyleSheet("background-color: Silver")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.canonicalAddressesButton.setFont(font)
        self.canonicalAddressesButton.setObjectName("canonicalAddressesButton")

        # Main Window Label
        self.windowMainLabel = QtWidgets.QLabel(self.centralwidget)
        self.windowMainLabel.setGeometry(QtCore.QRect(200, 20, 423, 32))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.windowMainLabel.setFont(font)
        self.windowMainLabel.setObjectName("windowMainLabel")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 110, 291, 20))
        self.label.setObjectName("label")

        # # View Reports Button
        self.viewReportsButton = QtWidgets.QPushButton(self.centralwidget)
        self.viewReportsButton.setStyleSheet("background-color: Silver")
        self.viewReportsButton.setGeometry(QtCore.QRect(650, 370, 175, 31))
        self.viewReportsButton.clicked.connect(self.openReportViewer)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.viewReportsButton.setFont(font)
        self.viewReportsButton.setObjectName("viewReportsButton")
        self.viewReportsButton.setEnabled(False)

        # Label for evidence viewer
        self.evidenceViewingLabel = QtWidgets.QLabel(self.centralwidget)
        self.evidenceViewingLabel.setGeometry(QtCore.QRect(650, 120, 141, 16))
        self.evidenceViewingLabel.setObjectName("evidenceViewingLabel")

        # Buttons for report generation
        self.generate_canonical_report = QtWidgets.QPushButton(self.centralwidget)
        self.generate_canonical_report.setGeometry(QtCore.QRect(650, 150, 175, 31))
        self.generate_canonical_report.setObjectName("generate_canonical_report")
        self.generate_canonical_report.setStyleSheet("background-color: Silver")
        self.generate_canonical_report.setEnabled(False)

        self.generate_Sim_Report = QtWidgets.QPushButton(self.centralwidget)
        self.generate_Sim_Report.setGeometry(QtCore.QRect(650, 190, 175, 31))
        self.generate_Sim_Report.setObjectName("generate_sim_report")
        self.generate_Sim_Report.setStyleSheet("background-color: Silver")
        self.generate_Sim_Report.setEnabled(False)

        self.generateSMS_Report = QtWidgets.QPushButton(self.centralwidget)
        self.generateSMS_Report.setGeometry(QtCore.QRect(650, 230, 175, 31))
        self.generateSMS_Report.setObjectName("generate_sms_report")
        self.generateSMS_Report.setStyleSheet("background-color: Silver")
        self.generateSMS_Report.setEnabled(False)

        self.generate_callLog_report = QtWidgets.QPushButton(self.centralwidget)
        self.generate_callLog_report.setGeometry(QtCore.QRect(650, 270, 175, 31))
        self.generate_callLog_report.setObjectName("generate_callLog_report")
        self.generate_callLog_report.setStyleSheet("background-color: Silver")
        self.generate_callLog_report.setEnabled(False)

        self.generateFullReportButton = QtWidgets.QPushButton(self.centralwidget)
        self.generateFullReportButton.setGeometry(QtCore.QRect(650, 310, 175, 31))
        self.generateFullReportButton.setObjectName("generateFullReportButton")
        self.generateFullReportButton.setStyleSheet("background-color: Silver")
        self.generateFullReportButton.setEnabled(False)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        # self.actionOpen = QtWidgets.QAction(MainWindow)
        # self.actionOpen.setObjectName("actionOpen")
        # self.actionExit = QtWidgets.QAction(MainWindow)
        # self.actionExit.setObjectName("actionExit")
        # self.actionOpen_2 = QtWidgets.QAction(MainWindow)
        # self.actionOpen_2.setObjectName("actionOpen_2")
        # self.actionExit_2 = QtWidgets.QAction(MainWindow)
        # self.actionExit_2.setObjectName("actionExit_2")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # Function that sets the text on all the UI Buttons
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DB Parser"))
        self.label.setText(_translate("MainWindow", "Data Parsing Options"))
        self.simCardButton.setText(_translate("MainWindow", "Sim Card"))
        self.callLogButton.setText(_translate("MainWindow", "Call Logs"))
        self.smsButton.setText(_translate("MainWindow", "SMS "))
        self.canonicalAddressesButton.setText(
            _translate("MainWindow", "Canonical Addresses")
        )
        self.windowMainLabel.setText(
            _translate("MainWindow", "Python Mobile Device Parser")
        )

        # Report Button set text and tool_tips
        self.evidenceViewingLabel.setText(_translate("MainWindow", "Report Generator"))

        self.generate_canonical_report.setText(
            _translate("MainWindow", "Canonical Report")
        )
        self.generate_canonical_report.setToolTip(
            "Select to generate canonical address report"
        )

        self.generate_Sim_Report.setText(_translate("MainWindow", "Sim Report"))
        self.generate_Sim_Report.setToolTip("Select to generate sim card report")

        self.generateSMS_Report.setText(_translate("MainWindow", "SMS Report"))
        self.generateSMS_Report.setToolTip("Select to generate sms report")

        self.generate_callLog_report.setText(
            _translate("MainWindow", "Call Log Report")
        )
        self.generate_callLog_report.setToolTip("Select to generate call log report")

        self.viewReportsButton.setText(_translate("MainWindow", "View Reports"))
        self.viewReportsButton.setToolTip("Select to open report viewing window")

        self.generateFullReportButton.setText(_translate("MainWindow", "Full Report"))
        self.generateFullReportButton.setToolTip("Select to generate full report")

        # self.actionOpen.setText(_translate("MainWindow", "Open"))
        # self.actionExit.setText(_translate("MainWindow", "Exit"))
        # self.actionOpen_2.setText(_translate("MainWindow", "Open"))
        # self.actionExit_2.setText(_translate("MainWindow", "Exit"))

        # Event Handling Code Section

        # Parsing Area!!!

        # Canonical Addresses Button click functionality to parse canonical address data
        self.canonicalAddressesButton.clicked.connect(self.select_canonical_data)

        # Sim Card Button click functionality to parse sim card data
        self.simCardButton.clicked.connect(self.select_sim_data)

        # Call Logs Button click functionality to parse call log data
        self.callLogButton.clicked.connect(self.select_call_data)

        # SMS Button click functionality to parse SMS data
        self.smsButton.clicked.connect(self.select_sms_data)

        # Reporting Area!!!

        # canonical address report generating functionality
        self.generate_canonical_report.clicked.connect(self.generate_canonicalR)

        # sim card report generating functionality
        self.generate_Sim_Report.clicked.connect(self.generate_simR)

        # sms report generating functionality
        self.generateSMS_Report.clicked.connect(self.generate_smsR)

        # call log report generating functionality
        self.generate_callLog_report.clicked.connect(self.generate_call_LogR)

        # All data report
        self.generateFullReportButton.clicked.connect(self.generate_full_reportR)

        # Report Generation Functions!!!
        self.one_pass = True
        self.two_pass = False
        self.three_pass = False
        self.four_pass = False

    # Data Parsing Functions!!!

    # Canonical Addresses button function
    def select_canonical_data(self):
        os.system("CanonicalAddressesParser.py")
        self.generate_canonical_report.setEnabled(True)

    # call log button function
    def select_call_data(self):
        os.system("CallLogParser.py")
        self.generate_callLog_report.setEnabled(True)

    # sms button function
    def select_sms_data(self):
        os.system("SmsParser.py")
        self.generateSMS_Report.setEnabled(True)

    # sim card button function
    def select_sim_data(self):
        os.system("SimCardParser.py")
        self.generate_Sim_Report.setEnabled(True)

    def generate_canonicalR(self):
        os.system("CanonicalAddressReporter.py")
        self.generate_canonical_report.setEnabled(True)
        self.check_run_button()

    def generate_call_LogR(self):
        os.system("CallLogReporter.py")
        self.generate_callLog_report.setEnabled(True)
        self.check_run_button()

    def generate_smsR(self):
        os.system("SmsDataReporter.py")
        self.generateSMS_Report.setEnabled(True)
        self.check_run_button()

    def generate_simR(self):
        os.system("SimCardReporter.py")
        self.generate_Sim_Report.setEnabled(True)
        self.check_run_button()

    def generate_full_reportR(self):
        os.system("AllDataReport.py")
        self.check_run_button()

    def check_run_button(self):
        if self.one_pass == self.two_pass == self.three_pass == self.four_pass is True:
            self.generateFullReportButton.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
