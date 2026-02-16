using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace camera
{
	[StructLayout(LayoutKind.Sequential, Size = 184)]
	[UnsafeValueType]
	[NativeCppClass]
	internal struct Session
	{
		[CLSCompliant(false)]
		[NativeCppClass]
		public enum ThumbnailType
		{

		}

		private long _003Calignment_0020member_003E;
	}
}
