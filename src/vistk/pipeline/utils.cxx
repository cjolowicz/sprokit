/*ckwg +5
 * Copyright 2011 by Kitware, Inc. All Rights Reserved. Please refer to
 * KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
 * Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.
 */

#include "utils.h"

#ifdef HAVE_SETPROCTITLE
#include <cstdlib>
#elif defined(__linux__)
#include <sys/prctl.h>
#endif

#if defined(_WIN32) || defined(_WIN64)
#include <boost/scoped_array.hpp>

#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#else
#include <cstdlib>
#endif

#if defined(_WIN32) || defined(_WIN64)
static DWORD const current_thread = -1;

static void SetThreadName(DWORD dwThreadID, LPCSTR threadName);
#endif

/**
 * \file utils.cxx
 *
 * \brief Implementation of pipeline utilities.
 */

namespace vistk
{

bool
name_thread(thread_name_t const& name)
{
#ifdef HAVE_SETPROCTITLE
  setproctitle("%s", name.c_str());
#elif defined(__linux__)
  int const ret = prctl(PR_SET_NAME, reinterpret_cast<unsigned long>(name.c_str()), 0, 0, 0);

  return (ret < 0);
#elif defined(_WIN32) || defined(_WIN64)
#ifndef NDEBUG
  SetThreadName(current_thread, name.c_str());
#else
  return false;
#endif
#else
  return false;
#endif

  return true;
}

envvar_value_t
get_envvar(envvar_name_t const& name)
{
  envvar_value_t value;

#if defined(_WIN32) || defined(_WIN64)
  char const* const name_cstr = name.c_str();

  DWORD sz = GetEnvironmentVariable(name_cstr, NULL, 0);

  if (sz)
  {
    typedef boost::scoped_array<char> raw_envvar_value_t;
    raw_envvar_value_t const envvalue(new char[sz]);

    sz = GetEnvironmentVariable(name_cstr, envvalue.get(), sz);

    value = envvalue.get();
  }

  if (!sz)
  {
    /// \todo Log error that the environment reading failed.
  }
#else
  char const* const envvalue = getenv(name.c_str());

  if (envvalue)
  {
    value = envvalue;
  }
#endif

  return value;
}

}

#if defined(_WIN32) || defined(_WIN64)

// Code obtained from http://msdn.microsoft.com/en-us/library/xcb2z8hs.aspx
static DWORD const MS_VC_EXCEPTION = 0x406D1388;

#pragma pack(push,8)
typedef struct tagTHREADNAME_INFO
{
   DWORD dwType; // Must be 0x1000.
   LPCSTR szName; // Pointer to name (in user addr space).
   DWORD dwThreadID; // Thread ID (-1 = caller thread).
   DWORD dwFlags; // Reserved for future use, must be zero.
} THREADNAME_INFO;
#pragma pack(pop)

void SetThreadName(DWORD dwThreadID, LPCSTR threadName)
{
   THREADNAME_INFO info;
   info.dwType = 0x1000;
   info.szName = threadName;
   info.dwThreadID = dwThreadID;
   info.dwFlags = 0;

   __try
   {
      RaiseException(MS_VC_EXCEPTION, 0, sizeof(info) / sizeof(ULONG_PTR), (ULONG_PTR*)&info);
   }
   __except(EXCEPTION_EXECUTE_HANDLER)
   {
   }
}

#endif