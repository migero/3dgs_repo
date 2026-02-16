using System;

namespace GoPro.Utils
{
	public class ExportHelper
	{
		private static readonly uint DEFAULT_ALIGNMENT = 2u;

		public static uint ComputeSize(double size)
		{
			return ComputePaddedSize((uint)Math.Ceiling(size));
		}

		public static uint ComputePaddedSize(uint size)
		{
			return size + size % DEFAULT_ALIGNMENT;
		}
	}
}
