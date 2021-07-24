/* cpuid.h
 *
 * Author           : Alexander J. Yee
 * Date Created     : 01/19/2012
 * Last Modified    : 01/25/2012
 *
 *
 *
 * And of course... The typical copyright stuff...
 *
 *      Redistribution of this program in both source or binary, regardless of
 *  form, with or without modification is permitted as long as the following
 *  conditions are met:
 *          1.  This copyright notice is maintained either inline in the source
 *              or distributed with the binary.
 *          2.  A list of all contributing authors along with their contributions
 *              is included either inline in the source or distributed with the
 *              binary.
 *          3.  The following disclaimer is maintained either inline in the
 *              source or distributed with the binary.
 *
 *  Disclaimer:
 *  This software is provided "as is", without any guarantee made to its
 *  suitability or fitness for any particular use. It may contain bugs so use
 *  of this program is at your own risk. I take no responsibility for any
 *  damage that may unintentionally be caused through its use.
 */

// https://github.com/Mysticial/Flops/blob/e571da6e94f7b6d2d1a90e87b19398c5c4de4375/version1/source/cpuid.h

#ifndef _cpuid_h
#define _cpuid_h
#ifdef __cplusplus
extern "C" {
#endif
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
#ifdef WIN32
#include <intrin.h>
#define cpuid __cpuid
#else
  void cpuid(int *info,int x);
#endif
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
  void cpuid_print_name();
  void cpuid_print_exts();
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
  ////////////////////////////////////////////////////////////////////////////////
#ifdef __cplusplus
}
#endif
#endif
