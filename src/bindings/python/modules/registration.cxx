/*ckwg +5
 * Copyright 2011 by Kitware, Inc. All Rights Reserved. Please refer to
 * KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
 * Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.
 */

#include "registration.h"

#include <vistk/pipeline/utils.h>

#include <boost/python/import.hpp>

#include <Python.h>

using namespace boost::python;
using namespace vistk;

static envvar_name_t const python_suppress_envvar = envvar_name_t("VISTK_NO_PYTHON_MODULES");

static bool is_suppressed();

void
register_processes()
{
  if (is_suppressed())
  {
    return;
  }

  Py_Initialize();

  try
  {
    object modules = import("vistk.modules.modules");
    object loader = modules.attr("load_python_modules");

    loader();
  }
  catch (error_already_set& /*e*/)
  {
    /// \todo Implement.
  }
}

bool
is_suppressed()
{
  envvar_value_t const python_suppress = get_envvar(python_suppress_envvar);

  bool suppress_python_modules = false;

  if (python_suppress)
  {
    suppress_python_modules = true;
  }

  free_envvar(python_suppress);

  return suppress_python_modules;
}