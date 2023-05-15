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
#include "Widgets/qAppStyle.h"

// Slicer includes
#include "qSlicerApplication.h"
#include "qSlicerApplicationHelper.h"

namespace
{

//----------------------------------------------------------------------------
int SlicerAppMain(int argc, char* argv[])
{
  typedef qTrainUSAppMainWindow SlicerMainWindowType;

  qSlicerApplicationHelper::preInitializeApplication(argv[0], new qAppStyle);

  qSlicerApplication app(argc, argv);
  if (app.returnCode() != -1)
    {
    return app.returnCode();
    }

  QScopedPointer<SlicerMainWindowType> window;
  QScopedPointer<QSplashScreen> splashScreen;

  qSlicerApplicationHelper::postInitializeApplication<SlicerMainWindowType>(
        app, splashScreen, window);

  if (!window.isNull())
    {
    QString windowTitle = QString("%1 %2").arg(Slicer_MAIN_PROJECT_APPLICATION_NAME).arg(Slicer_MAIN_PROJECT_VERSION_FULL);
    window->setWindowTitle(windowTitle);
    }

  return app.exec();
}

} // end of anonymous namespace

#include "qSlicerApplicationMainWrapper.cxx"
