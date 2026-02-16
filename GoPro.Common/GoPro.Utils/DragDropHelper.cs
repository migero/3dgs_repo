using System;
using System.Linq;
using System.Windows;

namespace GoPro.Utils
{
	public class DragDropHelper
	{
		public static string[] GetValidFiles(DragEventArgs e)
		{
			if (e.get_Data().GetDataPresent(DataFormats.FileDrop))
			{
				return (e.get_Data().GetData(DataFormats.FileDrop) as string[]).Where((string file) => ExtensionsHelper.IsFileExtensionAllowed(file)).ToArray();
			}
			return new string[0];
		}

		public static void ValidateDraggedFiles(DragEventArgs e, bool singleFileDrag)
		{
			if (singleFileDrag)
			{
				ValidateDraggedFiles(e, FirstFileValid);
			}
			else
			{
				ValidateDraggedFiles(e, AnyFileValid);
			}
		}

		private static void ValidateDraggedFiles(DragEventArgs e, Func<string[], bool> validateFiles)
		{
			bool flag = false;
			if (e.get_Data().GetDataPresent(DataFormats.FileDrop))
			{
				string[] arg = e.get_Data().GetData(DataFormats.FileDrop) as string[];
				flag = validateFiles(arg);
			}
			if (!flag)
			{
				e.set_Effects((DragDropEffects)0);
				((RoutedEventArgs)e).set_Handled(true);
			}
		}

		private static bool FirstFileValid(string[] files)
		{
			if (files.Length != 0)
			{
				return ExtensionsHelper.IsFileExtensionAllowed(files[0]);
			}
			return false;
		}

		private static bool AnyFileValid(string[] files)
		{
			bool flag = false;
			foreach (string path in files)
			{
				flag |= ExtensionsHelper.IsFileExtensionAllowed(path);
			}
			return flag;
		}
	}
}
