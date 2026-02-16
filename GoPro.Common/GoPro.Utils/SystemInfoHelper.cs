using System;
using System.Collections.Generic;
using System.Drawing;
using System.Management;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace GoPro.Utils
{
	public class SystemInfoHelper
	{
		public struct AvailableSize
		{
			public ulong Size;

			public ulong FreeSize;
		}

		public struct Dpi
		{
			public uint DpiX;

			public uint DpiY;
		}

		public struct DisplayInfo
		{
			public int Width;

			public int Height;

			public Dpi Dpi;
		}

		public struct CpuInfo
		{
			public string Name;

			public string Manufacturer;
		}

		private enum DpiType
		{
			Effective,
			Angular,
			Raw
		}

		private static readonly uint localDiskDriveType = 3u;

		private static readonly uint MONITOR_DEFAULTTONULL = 0u;

		private static readonly uint MONITOR_DEFAULTTOPRIMARY = 1u;

		private static readonly uint MONITOR_DEFAULTTONEAREST = 2u;

		private static readonly string MANAGEMENT_OBJECT_VALUE_NULL_REPLACEMENT = string.Empty;

		public static AvailableSize GetLocalDisksSize()
		{
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Expected O, but got Unknown
			AvailableSize availableSize = default(AvailableSize);
			availableSize.Size = 0uL;
			availableSize.FreeSize = 0uL;
			AvailableSize result = availableSize;
			try
			{
				ManagementObjectEnumerator enumerator = new ManagementObjectSearcher("select * from Win32_LogicalDisk").Get().GetEnumerator();
				try
				{
					while (enumerator.MoveNext())
					{
						ManagementObject val = (ManagementObject)enumerator.get_Current();
						if ((uint)((ManagementBaseObject)val).get_Item("DriveType") == localDiskDriveType)
						{
							object obj = ((ManagementBaseObject)val).get_Item("Size");
							if (obj != null)
							{
								result.Size += (ulong)obj;
							}
							object obj2 = ((ManagementBaseObject)val).get_Item("FreeSpace");
							if (obj2 != null)
							{
								result.FreeSize += (ulong)obj2;
							}
						}
					}
					return result;
				}
				finally
				{
					((IDisposable)enumerator)?.Dispose();
				}
			}
			catch
			{
				availableSize = default(AvailableSize);
				availableSize.Size = 0uL;
				availableSize.FreeSize = 0uL;
				return availableSize;
			}
		}

		public static AvailableSize GetMemorySize()
		{
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			AvailableSize availableSize = default(AvailableSize);
			availableSize.Size = 0uL;
			availableSize.FreeSize = 0uL;
			AvailableSize result = availableSize;
			try
			{
				ManagementObjectEnumerator enumerator = new ManagementObjectSearcher("select * from Win32_OperatingSystem ").Get().GetEnumerator();
				try
				{
					while (enumerator.MoveNext())
					{
						ManagementObject val = (ManagementObject)enumerator.get_Current();
						object obj = ((ManagementBaseObject)val).get_Item("TotalVisibleMemorySize");
						if (obj != null)
						{
							result.Size += (ulong)obj;
						}
						object obj2 = ((ManagementBaseObject)val).get_Item("FreePhysicalMemory");
						if (obj2 != null)
						{
							result.FreeSize += (ulong)obj2;
						}
					}
					return result;
				}
				finally
				{
					((IDisposable)enumerator)?.Dispose();
				}
			}
			catch
			{
				availableSize = default(AvailableSize);
				availableSize.Size = 0uL;
				availableSize.FreeSize = 0uL;
				return availableSize;
			}
		}

		public static List<DisplayInfo> GetDisplayInfo()
		{
			List<DisplayInfo> list = new List<DisplayInfo>();
			Screen[] allScreens = Screen.get_AllScreens();
			foreach (Screen val in allScreens)
			{
				list.Add(new DisplayInfo
				{
					Width = val.get_Bounds().Width,
					Height = val.get_Bounds().Height,
					Dpi = GetDpi(val, DpiType.Effective)
				});
			}
			return list;
		}

		public static CpuInfo GetCpuInfo()
		{
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			CpuInfo result = default(CpuInfo);
			try
			{
				ManagementObjectEnumerator enumerator = new ManagementObjectSearcher("select * from Win32_Processor").Get().GetEnumerator();
				try
				{
					while (enumerator.MoveNext())
					{
						ManagementObject val = (ManagementObject)enumerator.get_Current();
						object obj = ((ManagementBaseObject)val).get_Item("Name");
						if (obj != null)
						{
							result.Name = (string)obj;
						}
						object obj2 = ((ManagementBaseObject)val).get_Item("Manufacturer");
						if (obj2 != null)
						{
							result.Manufacturer = (string)obj2;
						}
					}
					return result;
				}
				finally
				{
					((IDisposable)enumerator)?.Dispose();
				}
			}
			catch
			{
				return default(CpuInfo);
			}
		}

		[DllImport("User32.dll")]
		private static extern IntPtr MonitorFromPoint([In] Point pt, [In] uint dwFlags);

		[DllImport("Shcore.dll")]
		private static extern IntPtr GetDpiForMonitor([In] IntPtr hmonitor, [In] DpiType dpiType, out uint dpiX, out uint dpiY);

		private static Dpi GetDpi(Screen screen, DpiType dpiType)
		{
			GetDpiForMonitor(MonitorFromPoint(new Point(screen.get_Bounds().Left + 1, screen.get_Bounds().Top + 1), MONITOR_DEFAULTTONEAREST), dpiType, out var dpiX, out var dpiY);
			Dpi result = default(Dpi);
			result.DpiX = dpiX;
			result.DpiY = dpiY;
			return result;
		}

		public static string ConvertManagementObjectValueToString(object managementObjectValue, bool allowNull)
		{
			if (!allowNull && managementObjectValue == null)
			{
				return MANAGEMENT_OBJECT_VALUE_NULL_REPLACEMENT;
			}
			return (string)managementObjectValue;
		}
	}
}
