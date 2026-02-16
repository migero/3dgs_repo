namespace GoPro.Analytics
{
	public static class AnalyticsEvents
	{
		public static class SystemInfo
		{
			public static readonly string GraphicsAdapterDetectedEvent = "Graphics Adapter Detected";

			public static readonly string VideoControllerNameKey = "Name";

			public static readonly string VideoControllerVendorNameKey = "Vendor Name";

			public static readonly string VideoControllerDeviceNameKey = "Device Name";

			public static readonly string VideoControllerDriverVersionKey = "Driver Version";

			public static readonly string VideoControllerDriverDateKey = "Driver Date";

			public static readonly string VideoControllerPnpIdsKey = "PNP IDs";

			public static readonly string VideoControllerLatestKey = "Latest Driver";

			public static readonly string VideoControllerDriverDateUnknown = "Unknown";

			public static readonly string VideoControllerDriverDateFormatYMD = "{0}-{1}-{2}";

			public static readonly string SystemInfoEvent = "System Info";

			public static readonly string DiskSpaceKey = "Disk Space";

			public static readonly string DiskFreeSpaceKey = "Disk Free Space";

			public static readonly string MemorySizeKey = "Memory Size";

			public static readonly string MemoryFreeSizeKey = "Memory Free Size";

			public static readonly string NetworkAvailableKey = "Network Available";

			public static readonly string MonitorsKey = "Monitors";

			public static readonly string ResolutionKey = "Resolution";

			public static readonly string DpiKey = "Dpi";

			public static readonly string CpuName = "Cpu Name";

			public static readonly string CpuManufacturer = "Cpu Manufacturer";
		}

		public static readonly string TimeKey = "_ProcessingTime";

		public static readonly string StatusKey = "_ProcessingStatus";

		public static readonly string ErrorActionNotFinished = "ActionNotFinished";
	}
}
