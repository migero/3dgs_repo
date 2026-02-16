using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace std
{
	[StructLayout(LayoutKind.Sequential, Size = 16)]
	[NativeCppClass]
	internal struct shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E
	{
		private long _003Calignment_0020member_003E;

		[SpecialName]
		public unsafe static void _003CMarshalCopy_003E(shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* A_0, shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* A_1)
		{
			if (A_0 != null)
			{
				*(long*)A_0 = 0L;
				*(long*)((long)(IntPtr)A_0 + 8) = 0L;
				*(long*)A_0 = *(long*)A_1;
				*(long*)((long)(IntPtr)A_0 + 8) = *(long*)((long)(IntPtr)A_1 + 8);
				*(long*)A_1 = 0L;
				*(long*)((long)(IntPtr)A_1 + 8) = 0L;
			}
		}

		[SpecialName]
		public unsafe static void _003CMarshalDestroy_003E(shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* A_0)
		{
			//IL_000f: Expected I, but got I8
			ulong num = *(ulong*)((long)(IntPtr)A_0 + 8);
			if (num != 0L)
			{
				_003CModule_003E.std_002E_Ref_count_base_002E_Decref((_Ref_count_base*)num);
			}
		}
	}
	[StructLayout(LayoutKind.Sequential, Size = 16)]
	[NativeCppClass]
	internal struct shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E
	{
		private long _003Calignment_0020member_003E;
	}
	[StructLayout(LayoutKind.Sequential, Size = 16)]
	[NativeCppClass]
	internal struct shared_ptr_003Ccommon_003A_003Aio_003A_003ASeekable_003E
	{
		private long _003Calignment_0020member_003E;
	}
}
