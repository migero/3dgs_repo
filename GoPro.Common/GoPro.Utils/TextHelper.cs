using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace GoPro.Utils
{
	public class TextHelper
	{
		public static Size MeasureTextBlock(TextBlock text)
		{
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_0049: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_006c: Expected O, but got Unknown
			//IL_0067: Unknown result type (might be due to invalid IL or missing references)
			//IL_006d: Expected O, but got Unknown
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			if (text.get_Text().Length == 0)
			{
				return new Size(0.0, 0.0);
			}
			string text2 = text.get_Text();
			CultureInfo currentCulture = CultureInfo.CurrentCulture;
			Typeface val = new Typeface(text.get_FontFamily(), text.get_FontStyle(), text.get_FontWeight(), text.get_FontStretch());
			double fontSize = text.get_FontSize();
			SolidColorBrush black = Brushes.get_Black();
			DpiScale dpi = VisualTreeHelper.GetDpi((Visual)(object)text);
			FormattedText val2 = new FormattedText(text2, currentCulture, (FlowDirection)0, val, fontSize, (Brush)(object)black, ((DpiScale)(ref dpi)).get_PixelsPerDip());
			return new Size(val2.get_Width(), val2.get_Height());
		}
	}
}
