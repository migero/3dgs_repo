using System;

namespace GoPro.Instance
{
	internal static class Extension
	{
		public static Exception Unwrap(this Exception e)
		{
			if (e.InnerException == null)
			{
				return e;
			}
			return e.InnerException;
		}
	}
}
