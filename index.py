import os
import sys
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QTabBar,
                              QFrame, QStackedLayout)
from PyQt5.QtGui import QIcon, QWindow, QImage
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class AddressBar(QLineEdit):
      def __init__(self):
            super().__init__()
      
      def mousePressEvent(self, e):
            self.selectAll()

class App(QFrame):
      def __init__(self):
            super().__init__()
            self.setWindowTitle("Net-90")
            self.setBaseSize(1366, 768)
            self.setMinimumSize(1366 ,768)
            self.CreateApp()
            
      def CreateApp(self):
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)

            #create tabs
            self.tabbar = QTabBar(movable = True, tabsClosable = True)
            self.tabbar.tabCloseRequested.connect(self.CloseTab)
            self.tabbar.tabBarClicked.connect(self.SwitchTab)
            self.tabbar.setCurrentIndex(0)
            self.tabbar.setDrawBase(False)
            self.tabbar.setLayoutDirection(Qt.LeftToRight)
            self.tabbar.setElideMode(Qt.ElideLeft)

            # Keep Track of Tabs
            self.tabCount = 0
            self.tabs = []
   
            #create Address bar
            self.Toolbar = QWidget()
            self.Toolbar.setObjectName("Toolbar")
            self.ToolbarLayout = QHBoxLayout()
            self.addressbar = AddressBar()
            self.AddTabButton = QPushButton("+")

            #New Tab Button
            self.addressbar.returnPressed.connect(self.BrowseTo)
            self.AddTabButton.clicked.connect(self.AddTab)

            #set toolbar buttons
            self.BackButton = QPushButton("<")
            self.BackButton.clicked.connect(self.GoBack)

            self.ForwardButton = QPushButton(">")
            self.ForwardButton.clicked.connect(self.GoForward)

            self.ReloadButton = QPushButton("R")
            self.ReloadButton.clicked.connect(self.ReloadPage)

            #Build Toolbar
            self.Toolbar.setLayout(self.ToolbarLayout)
            self.ToolbarLayout.addWidget(self.BackButton)
            self.ToolbarLayout.addWidget(self.ForwardButton)
            self.ToolbarLayout.addWidget(self.ReloadButton)
            self.ToolbarLayout.addWidget(self.addressbar)
            self.ToolbarLayout.addWidget(self.AddTabButton)

            #Set Main view
            self.container = QWidget()
            self.container.layout = QStackedLayout()
            self.container.setLayout(self.container.layout)

            #construct main view from top level elements
            self.layout.addWidget(self.tabbar)
            self.layout.addWidget(self.Toolbar)
            self.layout.addWidget(self.container) 

            self.setLayout(self.layout)

            self.AddTab()

            self.show()

      def CloseTab(self, i):
            self.tabbar.removeTab(i)

      def AddTab(self):
            i = self.tabCount

            self.tabs.append(QWidget())
            self.tabs[i].layout = QVBoxLayout()
            self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

            self.tabs[i].setObjectName("tab" + str(i))

            #Open Webview
            self.tabs[i].content = QWebEngineView()
            self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

            self.tabs[i].content.titleChanged.connect(lambda: self.SetTabContent(i, "title"))
            self.tabs[i].content.iconChanged.connect(lambda: self.SetTabContent(i, "icon"))
            self.tabs[i].content.urlChanged.connect(lambda: self.SetTabContent(i, "url"))

            #Add WebView to tabs layout
            self.tabs[i].layout.addWidget(self.tabs[i].content)

            #set top level tab from [] to layout
            self.tabs[i].setLayout(self.tabs[i].layout)

            #Add tab to top level stackedwidget
            self.container.layout.addWidget(self.tabs[i])
            self.container.layout.setCurrentWidget(self.tabs[i])

            #set the tab at the top of screen
            self.tabbar.addTab("New Tab")
            self.tabbar.setTabData(i, {"object" : "tab" + str(i), "initial" : 1})
            #self.tabbar.setTabData(i, "tab" + str(i))
            self.tabbar.setCurrentIndex(i)
            
            self.tabCount += 1

      def SwitchTab(self, i):
            if self.tabbar.tabData(i):
                  tab_data = self.tabbar.tabData(i)["object"]
                  #print("tab: ", tab_data)
                  tab_content = self.findChild(QWidget, tab_data)
                  self.container.layout.setCurrentWidget(tab_content)  
                  new_url = tab_content.content.url().toString()
                  self.addressbar.setText(new_url)

      def BrowseTo(self):
            text = self.addressbar.text()
            print(text)
            i = self.tabbar.currentIndex()
            tab = self.tabbar.tabData(i)["object"]
            wv = self.findChild(QWidget, tab).content

            if "http" not in text :
                  if "." not in text :
                        url ="http://google.com/#q=" + text
                  else:
                        url = "http://" + text
            else:
                  url = text            

            wv.load(QUrl.fromUserInput(url))

      def SetTabContent(self, i, type):
            tab_name = self.tabs[i].objectName()

            count = 0
            running = True
            current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]

            if current_tab == tab_name and type == "url":
                  new_url = self.findChild(QWidget, tab_name).content.url().toString()
                  self.addressbar.setText(new_url)
                  return False

            while running:
                  tab_data_name = self.tabbar.tabData(count)

                  if count >= 99:
                        running = False
                  
                  if tab_name == tab_data_name["object"]:
                        if type == "title":
                              newTitle = self.findChild(QWidget, tab_name).content.title()
                              self.tabbar.setTabText(count, newTitle)
                        elif type == "icon":
                              newIcon = self.findChild(QWidget, tab_name).content.icon()
                              self.tabbar.setTabIcon(count, newIcon)
                        running = False
                  
                  else:
                        count += 1

      def GoBack(self):
            activeIndex = self.tabbar.currentIndex()
            tab_name = self.tabbar.tabData(activeIndex)["object"]
            tab_content = self.findChild(QWidget, tab_name).content

            tab_content.back()

      def GoForward(self):
            activeIndex = self.tabbar.currentIndex()
            tab_name = self.tabbar.tabData(activeIndex)["object"]
            tab_content = self.findChild(QWidget, tab_name).content

            tab_content.forward()
      
      def ReloadPage(self):
            activeIndex = self.tabbar.currentIndex()
            tab_name = self.tabbar.tabData(activeIndex)["object"]
            tab_content = self.findChild(QWidget, tab_name).content

            tab_content.reload()

if __name__ == "__main__":
      app = QApplication(sys.argv)
      window = App()

      with open("index.css", "r") as style:
            app.setStyleSheet(style.read())

      sys.exit(app.exec_()) 