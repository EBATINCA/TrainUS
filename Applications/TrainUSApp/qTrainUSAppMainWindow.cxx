/*==============================================================================

  Copyright (c) Ebatinca S.L., Las Palmas de Gran Canaria, Spain

  Licensed under the Apache License, Version 2.0 (the "License"); you may 
  not use this file except in compliance with the License. You may obtain 
  a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0
    
  Unless required by applicable law or agreed to in writing, software 
  distributed under the License is distributed on an "AS IS" BASIS, 
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  The development of this software has been funded by NEOTEC grant from 
  the Centre for the Development of Technology and Innovation (CDTI) of 
  the Ministry for Science and Innovation of the Government of Spain.

==============================================================================*/

// TrainUS includes
#include "qTrainUSAppMainWindow.h"
#include "qTrainUSAppMainWindow_p.h"

// Qt includes
#include <QDesktopWidget>

// Slicer includes
#include "qSlicerApplication.h"
#include "qSlicerAboutDialog.h"
#include "qSlicerMainWindow_p.h"
#include "qSlicerModuleSelectorToolBar.h"

//-----------------------------------------------------------------------------
// qTrainUSAppMainWindowPrivate methods

qTrainUSAppMainWindowPrivate::qTrainUSAppMainWindowPrivate(qTrainUSAppMainWindow& object)
  : Superclass(object)
{
}

//-----------------------------------------------------------------------------
qTrainUSAppMainWindowPrivate::~qTrainUSAppMainWindowPrivate()
{
}

//-----------------------------------------------------------------------------
void qTrainUSAppMainWindowPrivate::init()
{
#if (QT_VERSION >= QT_VERSION_CHECK(5, 7, 0))
  QApplication::setAttribute(Qt::AA_UseHighDpiPixmaps);
#endif
  Q_Q(qTrainUSAppMainWindow);
  this->Superclass::init();
}

//-----------------------------------------------------------------------------
void qTrainUSAppMainWindowPrivate::setupUi(QMainWindow * mainWindow)
{
  qSlicerApplication * app = qSlicerApplication::application();

  //----------------------------------------------------------------------------
  // Add actions
  //----------------------------------------------------------------------------
  QAction* helpAboutSlicerAppAction = new QAction(mainWindow);
  helpAboutSlicerAppAction->setObjectName("HelpAboutTrainUSAppAction");
  helpAboutSlicerAppAction->setText("About " + app->applicationName());

  //----------------------------------------------------------------------------
  // Calling "setupUi()" after adding the actions above allows the call
  // to "QMetaObject::connectSlotsByName()" done in "setupUi()" to
  // successfully connect each slot with its corresponding action.
  this->Superclass::setupUi(mainWindow);
  
  // Add Help Menu Action
  this->HelpMenu->addAction(helpAboutSlicerAppAction);

  //----------------------------------------------------------------------------
  // Configure
  //----------------------------------------------------------------------------
  mainWindow->setWindowIcon(QIcon(":/Icons/Medium/DesktopIcon.png"));

  // QPixmap logo(":/LogoFull.png");
  // this->LogoLabel->setPixmap(logo);

  // Hide the toolbars
  this->MainToolBar->setVisible(false);
  //this->ModuleSelectorToolBar->setVisible(false);
  this->ModuleToolBar->setVisible(false);
  this->ViewToolBar->setVisible(false);
  this->MouseModeToolBar->setVisible(false);
  this->CaptureToolBar->setVisible(false);
  this->ViewersToolBar->setVisible(false);
  this->DialogToolBar->setVisible(false);

  // Hide the menus
  //this->menubar->setVisible(false);
  //this->FileMenu->setVisible(false);
  //this->EditMenu->setVisible(false);
  //this->ViewMenu->setVisible(false);
  //this->LayoutMenu->setVisible(false);
  //this->HelpMenu->setVisible(false);

  // Hide the modules panel
  //this->PanelDockWidget->setVisible(false);
  this->DataProbeCollapsibleWidget->setCollapsed(true);
  this->DataProbeCollapsibleWidget->setVisible(false);
  this->StatusBar->setVisible(false);
}

//-----------------------------------------------------------------------------
// qTrainUSAppMainWindow methods

//-----------------------------------------------------------------------------
qTrainUSAppMainWindow::qTrainUSAppMainWindow(QWidget* windowParent)
  : Superclass(new qTrainUSAppMainWindowPrivate(*this), windowParent)
{
  Q_D(qTrainUSAppMainWindow);
  d->init();
}

//-----------------------------------------------------------------------------
qTrainUSAppMainWindow::qTrainUSAppMainWindow(
  qTrainUSAppMainWindowPrivate* pimpl, QWidget* windowParent)
  : Superclass(pimpl, windowParent)
{
  // init() is called by derived class.
}

//-----------------------------------------------------------------------------
qTrainUSAppMainWindow::~qTrainUSAppMainWindow()
{
}

//-----------------------------------------------------------------------------
void qTrainUSAppMainWindow::on_HelpAboutTrainUSAppAction_triggered()
{
  qSlicerAboutDialog about(this);
  about.setLogo(QPixmap(":/Logo.png"));
  about.exec();
}
