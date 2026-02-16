using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace camera
{
	[StructLayout(LayoutKind.Sequential, Size = 240)]
	[NativeCppClass]
	[UnsafeValueType]
	internal struct Descriptor
	{
		[NativeCppClass]
		[CLSCompliant(false)]
		public enum SdCardStateType
		{

		}

		private long _003Calignment_0020member_003E;
	}
}
