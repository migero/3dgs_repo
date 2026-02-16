using System;
using System.Collections.Generic;
using System.Net.NetworkInformation;
using System.Text;
using System.Threading.Tasks;
using GoPro.Analytics;
using GoPro.Instance;

namespace GoPro.Utils
{
	public class AnalyticsHelper
	{
		public static async Task PushHardwareInfoAnalytics()
		{
			foreach (VideoController item in await GraphicsHardwareHelper.GetOrCreateVideoControllers())
			{
				PushVideoControllerAnalytics(item);
			}
			PushSystemInfoAnalytics();
		}

		public static void PushVideoControllerAnalytics(VideoController videoController)
		{
			if (videoController != null)
			{
				string value = AnalyticsEvents.SystemInfo.VideoControllerDriverDateUnknown;
				_ = videoController.CurrentDriverDate;
				if (videoController.CurrentDriverDate != default(DateTime))
				{
					value = string.Format(AnalyticsEvents.SystemInfo.VideoControllerDriverDateFormatYMD, videoController.CurrentDriverDate.Year, videoController.CurrentDriverDate.Month, videoController.CurrentDriverDate.Day);
				}
				AnalyticsInstance.Service.SendEvent(AnalyticsEvents.SystemInfo.GraphicsAdapterDetectedEvent, new Dictionary<string, object>
				{
					{
						AnalyticsEvents.SystemInfo.VideoControllerNameKey,
						videoController.Name
					},
					{
						AnalyticsEvents.SystemInfo.VideoControllerVendorNameKey,
						videoController.VendorName
					},
					{
						AnalyticsEvents.SystemInfo.VideoControllerDeviceNameKey,
						videoController.DeviceName
					},
					{
						AnalyticsEvents.SystemInfo.VideoControllerDriverVersionKey,
						videoController.CurrentDriverVersionString
					},
					{
						AnalyticsEvents.SystemInfo.VideoControllerDriverDateKey,
						value
					},
					{
						AnalyticsEvents.SystemInfo.VideoControllerPnpIdsKey,
						videoController.PnpID
					},
					{
						AnalyticsEvents.SystemInfo.VideoControllerLatestKey,
						(!videoController.UpdateAvailable()).ToString()
					}
				});
			}
		}

		public static void PushSystemInfoAnalytics()
		{
			Dictionary<string, object> dictionary = new Dictionary<string, object>();
			SystemInfoHelper.AvailableSize localDisksSize = SystemInfoHelper.GetLocalDisksSize();
			dictionary.Add(AnalyticsEvents.SystemInfo.DiskSpaceKey, localDisksSize.Size.ToString());
			dictionary.Add(AnalyticsEvents.SystemInfo.DiskFreeSpaceKey, localDisksSize.FreeSize.ToString());
			SystemInfoHelper.AvailableSize memorySize = SystemInfoHelper.GetMemorySize();
			dictionary.Add(AnalyticsEvents.SystemInfo.MemorySizeKey, memorySize.Size.ToString());
			dictionary.Add(AnalyticsEvents.SystemInfo.MemoryFreeSizeKey, memorySize.FreeSize.ToString());
			List<SystemInfoHelper.DisplayInfo> displayInfo = SystemInfoHelper.GetDisplayInfo();
			dictionary.Add(AnalyticsEvents.SystemInfo.MonitorsKey, displayInfo.Count.ToString());
			StringBuilder stringBuilder = new StringBuilder();
			StringBuilder stringBuilder2 = new StringBuilder();
			foreach (SystemInfoHelper.DisplayInfo item in displayInfo)
			{
				stringBuilder.Append($"{item.Width}x{item.Height};");
				stringBuilder2.Append($"{item.Dpi.DpiX}x{item.Dpi.DpiY};");
			}
			dictionary.Add(AnalyticsEvents.SystemInfo.ResolutionKey, stringBuilder.ToString());
			dictionary.Add(AnalyticsEvents.SystemInfo.DpiKey, stringBuilder2.ToString());
			SystemInfoHelper.CpuInfo cpuInfo = SystemInfoHelper.GetCpuInfo();
			dictionary.Add(AnalyticsEvents.SystemInfo.CpuName, cpuInfo.Name);
			dictionary.Add(AnalyticsEvents.SystemInfo.CpuManufacturer, cpuInfo.Manufacturer);
			dictionary.Add(value: NetworkInterface.GetIsNetworkAvailable().ToString(), key: AnalyticsEvents.SystemInfo.NetworkAvailableKey);
			AnalyticsInstance.Service.SendEvent(AnalyticsEvents.SystemInfo.SystemInfoEvent, dictionary);
		}
	}
}
