using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;

namespace GoPro.Analytics
{
	public abstract class AnalyticsService
	{
		private Dictionary<string, AnalyticsEvent> mPendingEvents = new Dictionary<string, AnalyticsEvent>();

		private readonly object mPendingEventsLock = new object();

		public abstract Task SetEnabledAsync(bool enable);

		protected abstract bool ValidateData(string name, Dictionary<string, object> properties);

		protected abstract void TrackEvent(string name, Dictionary<string, object> properties);

		~AnalyticsService()
		{
			SendAllPendingEvents();
		}

		public bool SendEvent(string name, Dictionary<string, object> properties)
		{
			if (!ValidateData(name, properties))
			{
				return false;
			}
			TrackEvent(name, properties);
			return true;
		}

		public AnalyticsEvent StartEvent(string name, Dictionary<string, object> properties)
		{
			if (!ValidateData(name, properties))
			{
				return null;
			}
			AnalyticsEvent analyticsEvent = new AnalyticsEvent(Guid.NewGuid().ToString(), name, properties);
			analyticsEvent.Start();
			lock (mPendingEventsLock)
			{
				mPendingEvents.Add(analyticsEvent.Id, analyticsEvent);
				return analyticsEvent;
			}
		}

		public void PauseEvent(AnalyticsEvent analyticsEvent)
		{
			lock (mPendingEventsLock)
			{
				GetPendingEvent(analyticsEvent)?.Stop();
			}
		}

		public void ResumeEvent(AnalyticsEvent analyticsEvent)
		{
			lock (mPendingEventsLock)
			{
				GetPendingEvent(analyticsEvent)?.Start();
			}
		}

		public void StopEvent(AnalyticsEvent analyticsEvent, string errorCode)
		{
			lock (mPendingEventsLock)
			{
				AnalyticsEvent pendingEvent = GetPendingEvent(analyticsEvent);
				if (pendingEvent != null)
				{
					pendingEvent.Stop();
					pendingEvent.Properties[AnalyticsEvents.TimeKey] = string.Format(CultureInfo.InvariantCulture, "{0:0.###}s", pendingEvent.ProcessingTimeMS / 1000.0);
					if (errorCode != null)
					{
						pendingEvent.Properties[AnalyticsEvents.StatusKey] = errorCode;
					}
					if (ValidateData(pendingEvent.Name, pendingEvent.Properties))
					{
						SendEvent(pendingEvent.Name, pendingEvent.Properties);
						mPendingEvents.Remove(pendingEvent.Id);
					}
				}
			}
		}

		public void SendAllPendingEvents()
		{
			List<AnalyticsEvent> list;
			lock (mPendingEventsLock)
			{
				list = mPendingEvents.Values.ToList();
			}
			foreach (AnalyticsEvent item in list)
			{
				StopEvent(item, AnalyticsEvents.ErrorActionNotFinished);
			}
		}

		private AnalyticsEvent GetPendingEvent(AnalyticsEvent analyticsEvent)
		{
			if (analyticsEvent == null || analyticsEvent.Id == null)
			{
				return null;
			}
			if (!mPendingEvents.ContainsKey(analyticsEvent.Id))
			{
				return null;
			}
			return mPendingEvents[analyticsEvent.Id];
		}
	}
}
