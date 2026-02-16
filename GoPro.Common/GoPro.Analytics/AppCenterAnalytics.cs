using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AppCenter;
using Microsoft.AppCenter.Analytics;

namespace GoPro.Analytics
{
	internal sealed class AppCenterAnalytics : AnalyticsService
	{
		private static readonly uint maximumProperties = 20u;

		private static readonly uint maximumEventNameLength = 256u;

		private static readonly uint maximumPropertyNameLength = 125u;

		private static readonly uint maximumValueLength = 125u;

		public AppCenterAnalytics()
		{
			AppCenter.Start(typeof(Microsoft.AppCenter.Analytics.Analytics));
		}

		public override async Task SetEnabledAsync(bool enable)
		{
			await Microsoft.AppCenter.Analytics.Analytics.SetEnabledAsync(enable);
		}

		protected override void TrackEvent(string name, Dictionary<string, object> properties)
		{
			Task.Run(delegate
			{
				Dictionary<string, string> properties2 = ((properties == null) ? null : properties.ToDictionary((KeyValuePair<string, object> pair) => pair.Key, (KeyValuePair<string, object> pair) => (string)pair.Value));
				Microsoft.AppCenter.Analytics.Analytics.TrackEvent(name, properties2);
			});
		}

		protected override bool ValidateData(string name, Dictionary<string, object> properties)
		{
			if (string.IsNullOrEmpty(name))
			{
				return false;
			}
			if (properties != null)
			{
				foreach (KeyValuePair<string, object> property in properties)
				{
					if (!(property.Value.GetType() == typeof(string)))
					{
						return false;
					}
				}
			}
			return true;
		}
	}
}
