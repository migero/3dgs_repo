using System.Windows;
using System.Windows.Controls;

namespace GoPro.Utils
{
	public static class WindowExtensions
	{
		public static bool? ShowDialogWithContent(this Window window, UIElement view)
		{
			((ContentControl)window).set_Content((object)view);
			return window.ShowDialog();
		}
	}
}
