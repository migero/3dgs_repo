using System.IO;
using System.Linq;

namespace GoPro.Utils
{
	public class ExtensionsHelper
	{
		private static readonly string[] _allowedVideoExtensions = new string[3] { ".360", ".mp4", ".mov" };

		private static readonly string[] _allowedImageExtensions = new string[6] { ".36p", ".jpg", ".jpeg", ".jpe", ".jfif", ".png" };

		public static bool IsFileExtensionAllowed(string path)
		{
			string value = Path.GetExtension(path)!.ToLower();
			return _allowedImageExtensions.Contains(value) | _allowedVideoExtensions.Contains(value);
		}

		public static string GetImageDialogFilter()
		{
			return string.Join(";", _allowedImageExtensions.Select((string x) => "*" + x));
		}

		public static string GetVideoDialogFilter()
		{
			return string.Join(";", _allowedVideoExtensions.Select((string x) => "*" + x));
		}

		public static string GetVideoImageDialogFilter()
		{
			return $"{GetVideoDialogFilter()};{GetImageDialogFilter()}";
		}
	}
}
