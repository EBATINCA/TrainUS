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

#ifndef __qTrainUSAppMainWindow_h
#define __qTrainUSAppMainWindow_h

// TrainUS includes
#include "qTrainUSAppExport.h"
class qTrainUSAppMainWindowPrivate;

// Slicer includes
#include "qSlicerMainWindow.h"

class Q_TRAINUS_APP_EXPORT qTrainUSAppMainWindow : public qSlicerMainWindow
{
  Q_OBJECT
public:
  typedef qSlicerMainWindow Superclass;

  qTrainUSAppMainWindow(QWidget *parent=0);
  virtual ~qTrainUSAppMainWindow();

public slots:
  void on_HelpAboutTrainUSAppAction_triggered();

protected:
  qTrainUSAppMainWindow(qTrainUSAppMainWindowPrivate* pimpl, QWidget* parent);

private:
  Q_DECLARE_PRIVATE(qTrainUSAppMainWindow);
  Q_DISABLE_COPY(qTrainUSAppMainWindow);
};

#endif
