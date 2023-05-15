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

#ifndef __qTrainUSAppMainWindow_p_h
#define __qTrainUSAppMainWindow_p_h

// TrainUS includes
#include "qTrainUSAppMainWindow.h"

// Slicer includes
#include "qSlicerMainWindow_p.h"

//-----------------------------------------------------------------------------
class Q_TRAINUS_APP_EXPORT qTrainUSAppMainWindowPrivate
  : public qSlicerMainWindowPrivate
{
  Q_DECLARE_PUBLIC(qTrainUSAppMainWindow);
public:
  typedef qSlicerMainWindowPrivate Superclass;
  qTrainUSAppMainWindowPrivate(qTrainUSAppMainWindow& object);
  virtual ~qTrainUSAppMainWindowPrivate();

  virtual void init();
  /// Reimplemented for custom behavior
  virtual void setupUi(QMainWindow * mainWindow);
};

#endif
