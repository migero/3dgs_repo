namespace GoPro.Utils
{
	public static class AlgorithmHelper
	{
		public static void Swap<T>(ref T a, ref T b)
		{
			T val = a;
			a = b;
			b = val;
		}
	}
}
