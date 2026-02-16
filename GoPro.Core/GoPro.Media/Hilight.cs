using media;

namespace GoPro.Media
{
	public class Hilight
	{
		public long TimeSinceStart = 0L;

		public HilightType HilightMode = HilightType.Manual;

		public Hilight(long timestamp, HilightType type)
		{
			TimeSinceStart = timestamp;
			HilightMode = type;
		}

		public Hilight(long timestamp, media.HilightType type)
		{
			TimeSinceStart = timestamp;
			HilightMode = (HilightType)type;
		}
	}
}
