globalStyle = """

                 QsciScintilla#editor {
                         border: none;
                         border-top: 2px solid #007ACC;
                 }

                QToolButton {
                    background: transparent;
                    border-radius: 0px;
                    padding: 1px;
                    border: none;
                }

                QToolButton:hover {
                    background: white;
                }

                QToolButton:pressed {
                    background: #007ACC;
                }

                QToolButton:checked {
                    background: #007ACC;
                }

                QToolButton:disabled {
                    background: transparent;
                }

                 QToolButton::menu-button {
                     color: black;
                 }

             QGroupBox {
                 background-color: none;
                 border: none;
                 font: bold;
                 border-radius: 0px;
                 margin-top: 5ex; /* leave space at the top for the title */
             }

             QGroupBox::title {
                 padding-left: 8px;
                 subcontrol-origin: margin;
                 subcontrol-position: top left; /* position at the top left */
                 background-color: none;
             }

             QComboBox {
                 color: #003366;
                 border-top: transparent;
                 border-right: transparent;
                 border-left: transparent;
                 border-bottom: 1px solid #007ACC;
                 border-radius: 0px;
                 padding: 2px 2px 2px 3px;
             }

             QComboBox:disabled {
                 color: gray;
             }

             QComboBox:editable {
                 background: white;
             }

             QComboBox:!editable, QComboBox::drop-down:editable {
                  background: lightgrey;
                  border-radius: 0px;
             }

             /* QComboBox gets the "on" state when the popup is open */
             QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                 background: darkgray;
             }

             QComboBox:on { /* shift the text when the popup opens */
             
             }

             QComboBox::drop-down {
                 subcontrol-origin: padding;
                 subcontrol-position: top right;
                 width: 15px;
                 border: none;
             }

             QComboBox::down-arrow {
                 image: url(Resources/style/images/downarrow.png);
             }

             QComboBox::down-arrow:on { /* shift the arrow when popup is open */
                 top: 1px;
                 left: 0px;
             }

             QComboBox QAbstractItemView {
                 border: 1px solid lightgray;
                 selection-background-color: #2B2BFF;
             }

             QComboBox QAbstractItemView::item {
                 min-height: 25px;
             }

        QTabWidget::pane { /* The tab widget frame */
             border-top: none;
        }

        QTabWidget#settingsTab::pane { /* The tab widget frame */
             border-top: 1px solid #007ACC;
             position: absolute;
        }

        QTabWidget::pane#buildTab { /* The tab widget frame */
             border-top: 2px solid #007ACC;
        }

        QTabWidget::pane#sideBottomTab { /* The tab widget frame */
             border-top: 2px solid #007ACC;
        }

        QTabWidget::tab-bar {
             left: 0px; /* move to the right by 0px */
        }

        QTabWidget#sideBottomTab::tab-bar {
             left: 0px; /* move to the right by 0px */
        }

        QTabWidget#settingsTab::tab-bar {
             left: 10px; /* move to the right by 0px */
        }

        /* Style the tab using the tab sub-control. Note that
             it reads QTabBar _not_ QTabWidget */
        QTabBar::tab {
             background: none;
             border: none;
             min-width: 24ex;
             min-height: 5ex;
             padding: 2px;
             padding-left: 5px;
             padding-right: 5px;
        }

        QTabBar::tab:hover {
             background: #70A7DC;
             color: black;
        }

        QTabBar::tab:selected{
             background: #007ACC;
             color: white;
        }

        QTabBar::tab:!selected {
             margin-top: 0px; /* make non-selected tabs look smaller */
        }

        QTabBar::tab:first {
             border-left: none;
         }

        QTabBar::tab:only-one {
             border-left: none;
        }

        QTabBar::tear {
             image: url(Resources/style/images/tear.png);
        }

        QTabBar::scroller { /* the width of the scroll buttons */
             width: 20px;
        }

        QTabBar QToolButton { /* the scroll buttons are tool buttons */
             border-image: url(Resources/style/images/scrollbutton.png) 2;

        }

        QTabBar QToolButton::right-arrow { /* the arrow mark in the tool buttons */
             image: url(Resources/style/images/Arrow Right.png);
        }

        QTabBar QToolButton::left-arrow {
             image: url(Resources/style/images/Arrow Left.png);
        }


        QTabBar::close-button {
             image: url(Resources/style/images/close1.png)

         }

        QTabBar::close-button:hover {
             image: url(Resources/style/images/close-hover.png)
        }

        QTabBar::close-button:pressed {
             image: url(Resources/style/images/close-pressed.png)
        }

        QToolBar {
            border: none;
            background-color: transparent;
        }

        QToolBar QToolButton {
            border: 1px solid transparent;
            background: transparent;
            padding: 1px;
        }

        QToolBar QToolButton:hover:enabled { /* when selected using mouse or keyboard */
             background-color: white;
        }

        QToolBar QToolButton:pressed:enabled {
             background-color: #007ACC;
        }

        QToolBar QToolButton:disabled {
             background-color: transparent;
        }

        QToolBar QToolButton:checked {
             background-color: #007ACC;
        }

        QStatusBar {
             background: transparent;
        }

        QStatusBar::item {
             border-radius: 3px;
        }


        QDockWidget {
             color: white;
             titlebar-close-icon: url(Resources/style/images/close_black.png);
             titlebar-normal-icon: url(Resources/style/images/undock.png);
        }

        QDockWidget::title {
             border: none;
             text-align: left; /* align the text to the left */
             background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #585858, stop:1 #3F3F3F);
             padding-left: 5px;
        }

        QDockWidget::close-button, QDockWidget::float-button {
             border: none;
             background: transparent;
             padding: 2px;
        }

        QDockWidget::close-button:hover, QDockWidget::float-button:hover {
             background: transparent;
        }

        QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
             padding: 1px -1px -1px 1px;
        }

        QToolTip {
             color: white;
             border: none;
             opacity: 200;
             border-radius: 3px;
             background: #333333;
        }

        QMenuBar {
             background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 lightgray, stop:1 darkgray);
        }

        QMenuBar {
             background-color: #F0F0F0;
             border-bottom: 1px solid darkgrey;
        }

        QMenuBar::item {
             spacing: 3px; /* spacing between menu bar items */
             padding: 3px 8px;
             background: none;
             border-radius: 0px;
        }

        QMenuBar::item:selected { /* when selected using mouse or keyboard */
             background: rgba(255, 0, 0, 80);
        }

        QMenuBar::item:pressed {
             background: rgba(255, 0, 0, 80);
        }

        QMenu {
             background: #E6E6E6;
             padding: 2px;
        }

        QMenu::item {
             padding: 5px 30px 5px 30px;
             border: none;
        }

        QMenu::item:selected:enabled {
             border-color: none;
             background: #FAFAFA;
        }

        QMenu::separator {
             height: 1px;
             background-color: lightgrey;
        }

        QMenu::indicator {
             width: 13px;
             height: 13px;
        }

        QListView {
             show-decoration-selected: 1; /* make the selection span the entire width of the view */
        }

        QListView::item:selected:!active {
             color: black;
             border: 1px solid white;
             background: lightgray;
        }

        QListView::item:selected:active {
             color: white;
             background: #337BFF;
        }

         QHeaderView::section {
             background: none;
             color: black;
             padding-left: 2px;
             border: none;
             border-bottom: 1px solid lightgray;
             height: 20px;
         }

         QHeaderView::section:checked
         {
             background-color: red;
         }

         /* style the sort indicator */
         QHeaderView::down-arrow {
             image: url(Resources/style/images/downarrow.png);
         }

         QHeaderView::up-arrow {
             image: url(Resources/style/images/uparrow.png);
         }


        QTreeView {
             show-decoration-selected: 1; /* make the selection span the entire width of the view */
             background: #E6E6E6;
             border: none;
        }

        QTreeView#sidebarItem {
             border: none;
             show-decoration-selected: 1; /* make the selection span the entire width of the view */
             background: #E6E6E6;
        }

        QTreeView::item:selected:!active {
             font: bold 20px;
             color: black;
             background: lightgrey;}

        QTreeView::item:selected:active {
             font: bold 20px;
             color: white;
             background: grey;
        }

        QTreeView::item:hover {
             border: none;
             background: #CCCCCC;
        }

        QSlider::groove:horizontal {
             border: 1px inset #999999;
             height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
             background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                 stop:0 #B3B3B3, stop:1 #FFFFFF);
             margin: 2px 7px 0 7px;
             border-radius: 5px;
        }

        QSlider::handle:horizontal {
             background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                 stop:0 #D2D2D2, stop:1 #C3C3C3);
             border: 1px solid #5c5c5c;
             width: 18px;
             margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
             border-radius: 3px;
        }

        QScrollBar:vertical{
            padding-left: 0px;
            padding-right: 1px;
            border-left-width: 1px;
            background: #f1f1f1;
            width: 12px;
        }

        QScrollBar:horizontal{
            padding-top: 0px;
            padding-bottom: 1px;
            border-top-width: 1px;
            border-style:solid;
            border: none;
            background: #E7E7E7;
            height: 10px;
        }

        QScrollBar::handle:vertical{
            margin-top: 15px;
            margin-bottom: 15px;
            background: #B2B8BE;
            border-radius: 0px;
            border: 1px solid #FFFFFF;
            min-height: 30px;
        }

        QScrollBar::handle:horizontal{
            margin-left: 15px;
            margin-right: 15px;
            background: #B2B8BE;
            border-radius: 0px;
            border: none;
            min-width: 30px;
        }

        QScrollBar::handle:hover{
            background: #6F767D;
        }

        QScrollBar::handle:pressed{
            background: #141414;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical,
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal{
            background: none;
            border: none;
        }
        
        QScrollBar::add-line:vertical:pressed,
        QScrollBar::sub-line:vertical:pressed,
        QScrollBar::add-page:vertical:pressed,
        QScrollBar::sub-page:vertical:pressed,
        QScrollBar::add-line:horizontal:pressed,
        QScrollBar::sub-line:horizontal:pressed,
        QScrollBar::add-page:horizontal:pressed,
        QScrollBar::sub-page:horizontal:pressed{
            background: lightgrey;
            border: none;
        }

        QScrollBar::up-arrow:vertical {
          border: none;
          width: 10px;
          height: 10px;
          margin-left: 0px;
          image: url(Resources/style/images/uparrow.png);
        }

        QScrollBar::down-arrow:vertical {
          border: none;
          width: 10px;
          height: 10px;
          margin-left: 0px;
          image: url(Resources/style/images/downarrow.png);
        }

        QScrollBar::left-arrow:horizontal {
          border: none;
          width: 10px;
          height: 10px;
          image: url(Resources/style/images/leftarrow.png);
        }

        QScrollBar::right-arrow:horizontal {
          border: none;
          width: 10px;
          height: 10px;
          image: url(Resources/style/images/rightarrow.png);
        }

        QPushButton {
            min-width: 70px;
            min-height: 20px;
            color: black;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #F1F1F1, stop: 1 #DFDFDF);
            border-radius: 2px;
            border: 1px solid #A8A8A8;
        }

        QPushButton:hover {
            border: 1px solid #AAAAAA;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #F1F1F1, stop: 1 #F0F0F0);
        }

        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #D7D7D7, stop: 1 #BDBDBD);
            padding-top: 2px;
            border: 1px solid #A1A1A1;
        }

        QPushButton:checked {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #D7D7D7, stop: 1 #BDBDBD);
            padding-top: 2px;
            border: 1px solid #A1A1A1;
        }

        QPushButton:disabled {
            color: black;
            background: #FFFFFF;
        }

         QSplitter::handle {
             background: none;
         }

         QSplitter::handle:horizontal {
             width: 5px;
             background: #E6E6E6;
         }

         QSplitter::handle:vertical {
             height: 5px;
             background: lightgray;
         }

         QSplitter::handle:hover {
             background: lightgray;
         }

         QSplitter::handle:pressed {
             background: gray;
         }

         QLineEdit {
             border: 1px solid lightgrey;
             min-height: 20px;
             border-radius: 0px;
             padding: 0 4px;
             background: none;
         }

         QLineEdit:disabled {
             border: 1px solid lightgray;
         }

        """

projectTitleBoxStyle = """

        QListView {
            border: none;
            border-top: 1px solid lightgray;
            show-decoration-selected: 1; /* make the selection span the entire width of the view */
        }

        QListView::item:selected:!active {
             color: black;
             border: none;
             background: none;
        }

        QListView::item:selected:active {
             color: white;
             border: none;
             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5a91d4, stop: 1 #1a57ad);;
        }

        """

bottomSwitcherStyle = """

        QPushButton {
             min-height: 17px;
             background: none;
             border: none;
             border-radius: 0px;
             min-width: 13ex;
             padding: 2px;
        }

        QPushButton:hover {
             color: black;
             background: none;
        }

        QPushButton:pressed {
            background: none;
        }

        QPushButton:checked {
             color: black;
             border-left: 1px solid lightgray;
             border-right: 1px solid lightgray;
        }

        QPushButton:disabled {
            color: black;
            background: #FFFFFF;
        }
        """

editorStyle = """
                 QListView {
                        border: 1px solid black;
                        color: lightgrey;
                        min-width: 500px;
                        min-height: 190px;
                        background: #1C1C1C;
                        show-decoration-selected: 1; /* make the selection span the entire width of the view */
                 }

                 QListView::item:alternate {
                        background: #EEEEEE;
                 }

                 QListView::item:selected {
                        color: white;
                        font: bold;
                        border: none;
                        background: #363636;
                 }

                 QListView::item:selected:!active {
                        color: white;
                        font: bold;
                        border: none;
                        background: #363636;
                 }

                 QListView::item:selected:active {
                        color: white;
                        background: #575757;
                 }

                 QListView::item:hover {
                        border-bottom:  none;
                 }
                """

mainMenuStyle = """

                QPushButton {
                    padding: 2px 6px 2px 6px;
                    color: grey;
                    background: transparent;
                    border: none;
                    border-radius: 0px;
                }

                QPushButton:hover {
                    color: black;
                }

                QPushButton:pressed {

                }

                QPushButton:checked {
                    color: black;
                }

                """

toolWidgetStyle = """

                QLabel#containerLabel { border-left: 1px solid #0099FF;
                                       border-right: 1px solid #0099FF;
                                       border-bottom: 1px solid #0099FF;
                                       background: #F0F0F0;
                                       }

                QLabel#toolWidgetNameLabel { font: 14px; color: grey;}

                """

viewSwitcherStyle = """

                    QLabel {
                        background:  rgba(138, 201, 255, 200);
                        padding: 1px;
                    }

                    QToolButton {
                        min-width: 30px;
                        min-height: 30px;
                        background: #A3D5FF;
                        border-radius: 0px;
                        border: none;
                    }

                    QToolButton:hover {
                        background: white;
                        border: none;
                        border-bottom: 3px solid #A3D5FF;
                    }

                    QToolButton:checked {
                        background: white;
                        border-bottom: 3px solid #3DA7FF;
                    }

                    QToolButton:disabled {
                        background: #FFFFFF;
                    }
                """
