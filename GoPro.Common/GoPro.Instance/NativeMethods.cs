using System;
using System.Runtime.InteropServices;
using System.Security;

namespace GoPro.Instance
{
	[SuppressUnmanagedCodeSecurity]
	internal static class NativeMethods
	{
		[DllImport("user32.dll")]
		public static extern bool PostMessage(IntPtr hwnd, int msg, IntPtr wparam, IntPtr lparam);

		[DllImport("user32.dll", CharSet = CharSet.Unicode)]
		public static extern int RegisterWindowMessage(string message);
	}
}
