using System;
using System.Reflection;
using System.Runtime.InteropServices;

namespace GoPro.Utils
{
	public class ExportDll
	{
		private const uint PAGE_READWRITE = 4u;

		private const uint GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT = 2u;

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool VirtualProtect(IntPtr lpAddress, uint dwSize, uint flNewProtect, out uint lpflOldProtect);

		[DllImport("kernel32.dll", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
		private static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

		[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
		private static extern bool GetModuleHandleEx(uint dwFlags, string lpModuleName, out IntPtr phModule);

		public static void SetVariableInt32(string name, int value)
		{
			Assembly executingAssembly = Assembly.GetExecutingAssembly();
			IntPtr phModule = IntPtr.Zero;
			if (!GetModuleHandleEx(2u, executingAssembly.ManifestModule.Name, out phModule))
			{
				return;
			}
			IntPtr procAddress = GetProcAddress(phModule, name);
			if (procAddress != IntPtr.Zero)
			{
				uint lpflOldProtect = 0u;
				if (VirtualProtect(procAddress, 4u, 4u, out lpflOldProtect))
				{
					Marshal.WriteInt32(procAddress, value);
					VirtualProtect(procAddress, 4u, lpflOldProtect, out lpflOldProtect);
				}
			}
		}
	}
}
