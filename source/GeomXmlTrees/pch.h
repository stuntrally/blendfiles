#ifndef __PCH_H__
#define __PCH_H__

//  this is the precompiled header file for VS, only for Windows build
#ifdef _MSC_VER
// include file for project specific include files that are used frequently, but are changed infrequently

///  std
#include <vector>
#include <string>
#include <sstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

///  win
#ifdef _WIN32
	#define WINVER 0x0510
	#define _WIN32_WINNT 0x0510
	#define _WIN32_WINDOWS 0x0410
	#define WIN32_LEAN_AND_MEAN
	#include <windows.h>
	#include <tchar.h>
#endif

#include <boost/filesystem.hpp>
#include <boost/regex.hpp>

#include "tinyxml.h"

#endif
#endif