using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace std
{
	[StructLayout(LayoutKind.Sequential, Size = 64)]
	[NativeCppClass]
	[UnsafeValueType]
	internal struct function_003Cvoid_0020__cdecl_0028void_0029_003E
	{
		private long _003Calignment_0020member_003E;

		[SpecialName]
		public unsafe static void _003CMarshalCopy_003E(function_003Cvoid_0020__cdecl_0028void_0029_003E* A_0, function_003Cvoid_0020__cdecl_0028void_0029_003E* A_1)
		{
			if (A_0 != null)
			{
				*(long*)((long)(IntPtr)A_0 + 56) = 0L;
				try
				{
					_003CModule_003E.std_002E_Func_class_003Cvoid_003E_002E_Reset_move((_Func_class_003Cvoid_003E*)A_0, (_Func_class_003Cvoid_003E*)A_1);
					return;
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Func_class<void>*, void>*/)(&_003CModule_003E.std_002E_Func_class_003Cvoid_003E_002E_007Bdtor_007D), A_0);
					throw;
				}
			}
		}

		[SpecialName]
		public unsafe static void _003CMarshalDestroy_003E(function_003Cvoid_0020__cdecl_0028void_0029_003E* A_0)
		{
			_003CModule_003E.std_002E_Func_class_003Cvoid_003E_002E_Tidy((_Func_class_003Cvoid_003E*)A_0);
		}
	}
}
