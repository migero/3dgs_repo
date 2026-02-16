using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace GoPro.Core.Camera
{
	[StructLayout(LayoutKind.Sequential, Size = 40)]
	[NativeCppClass]
	[CLSCompliant(false)]
	public struct CameraWatcherCallback
	{
		private long _003Calignment_0020member_003E;
	}
}
