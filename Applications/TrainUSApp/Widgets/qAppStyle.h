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

#ifndef __qAppStyle_h
#define __qAppStyle_h

// TrainUS includes
#include "qTrainUSAppExport.h"

// Slicer includes
#include "qSlicerStyle.h"

class Q_TRAINUS_APP_EXPORT qAppStyle
  : public qSlicerStyle
{
  Q_OBJECT
public:
  /// Superclass typedef
  typedef qSlicerStyle Superclass;

  /// Constructors
  qAppStyle();
  virtual ~qAppStyle();

  /// Reimplemented to customize colors.
  /// \sa QStyle::standardPalette()
  virtual QPalette standardPalette() const;

  /// Reimplemented to apply custom palette to widgets
  /// \sa QStyle::drawComplexControl()
  void drawComplexControl(ComplexControl control,
                          const QStyleOptionComplex* option,
                          QPainter* painter,
                          const QWidget* widget = 0)const;
  /// Reimplemented to apply custom palette to widgets
  /// \sa QStyle::drawControl()
  virtual void drawControl(ControlElement element,
                           const QStyleOption* option,
                           QPainter* painter,
                           const QWidget* widget = 0 )const;

  /// Reimplemented to apply custom palette to widgets
  /// \sa QStyle::drawPrimitive()
  virtual void drawPrimitive(PrimitiveElement element,
                             const QStyleOption* option,
                             QPainter* painter,
                             const QWidget* widget = 0 )const;

  /// Tweak the colors of some widgets.
  virtual QPalette tweakWidgetPalette(QPalette palette,
                                      const QWidget* widget)const;

  /// Reimplemented to apply styling to widgets.
  /// \sa QStyle::polish()
  virtual void polish(QWidget* widget);
  using Superclass::polish;
};

#endif
