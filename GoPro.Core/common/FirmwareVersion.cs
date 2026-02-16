using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace common
{
	[StructLayout(LayoutKind.Sequential, Size = 64)]
	[UnsafeValueType]
	[NativeCppClass]
	internal struct FirmwareVersion
	{
		private long _003Calignment_0020member_003E;
	}
}
