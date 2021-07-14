/*==============================================================================

  Copyright (c) Kitware, Inc.

  See http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Julien Finet, Kitware, Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

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
