using System.Security.Cryptography;

namespace GoPro.Security
{
	public static class Cryptography
	{
		public static string ComputeHash(byte[] data)
		{
			if (data == null || data.Length == 0)
			{
				return null;
			}
			string text = "";
			byte[] array = SHA1.Create().ComputeHash(data);
			foreach (byte b in array)
			{
				text += b.ToString("x2");
			}
			return text;
		}
	}
}
