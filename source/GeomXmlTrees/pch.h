#ifndef __PCH_H__
#define __PCH_H__

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

#include <filesystem>
#include <regex>

#define TIXML_USE_STL
#include "tinyxml.h"

#endif
