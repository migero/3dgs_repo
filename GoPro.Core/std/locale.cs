using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace std
{
	[StructLayout(LayoutKind.Sequential, Size = 16)]
	[NativeCppClass]
	internal struct locale
	{
		[StructLayout(LayoutKind.Sequential, Size = 8)]
		[NativeCppClass]
		[CLSCompliant(false)]
		public struct id
		{
			private long _003Calignment_0020member_003E;
		}

		[StructLayout(LayoutKind.Sequential, Size = 16)]
		[NativeCppClass]
		[CLSCompliant(false)]
		public struct facet
		{
			private long _003Calignment_0020member_003E;
		}

		[StructLayout(LayoutKind.Sequential, Size = 56)]
		[CLSCompliant(false)]
		[NativeCppClass]
		public struct _Locimp
		{
			private long _003Calignment_0020member_003E;
		}

		private long _003Calignment_0020member_003E;
	}
}
