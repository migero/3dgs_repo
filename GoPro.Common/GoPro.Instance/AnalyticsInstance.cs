using GoPro.Analytics;

namespace GoPro.Instance
{
	public static class AnalyticsInstance
	{
		public static AnalyticsService Service { get; private set; }

		public static void Initialize(AnalyticsServiceType type, string key)
		{
			if (type == AnalyticsServiceType.AppCenter)
			{
				Service = new AppCenterAnalytics();
			}
		}
	}
}
