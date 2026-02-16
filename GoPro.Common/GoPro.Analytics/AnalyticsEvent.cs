using System;
using System.Collections.Generic;

namespace GoPro.Analytics
{
	public class AnalyticsEvent
	{
		private DateTime mStartTime;

		private bool mStarted;

		public string Id { get; private set; }

		public string Name { get; private set; }

		public Dictionary<string, object> Properties { get; private set; }

		public double ProcessingTimeMS { get; private set; }

		public AnalyticsEvent(string id, string name, Dictionary<string, object> properties)
		{
			Id = id;
			Name = name;
			Properties = properties;
			if (Properties == null)
			{
				Properties = new Dictionary<string, object>();
			}
		}

		internal void Start()
		{
			if (!mStarted)
			{
				mStarted = true;
				mStartTime = DateTime.UtcNow;
			}
		}

		internal void Stop()
		{
			if (mStarted)
			{
				mStarted = false;
				DateTime utcNow = DateTime.UtcNow;
				ProcessingTimeMS += (utcNow - mStartTime).TotalMilliseconds;
			}
		}
	}
}
